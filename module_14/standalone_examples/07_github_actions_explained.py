"""
07. GitHub Actions CI/CD — Explained
======================================

This script generates a GitHub Actions workflow file with inline comments
explaining each section. Running it produces a ready-to-use CI config.

Usage:
    python 07_github_actions_explained.py > ../contacts_api/.github/workflows/ci.yml

Then commit and push — the workflow runs automatically on every push.
"""

WORKFLOW = """\
# GitHub Actions CI Workflow for Contacts API
# ============================================
# This file tells GitHub to run tests automatically on every push.
# If tests fail, Render will not deploy (configure this in Render settings).

name: CI

# TRIGGERS: when does this workflow run?
on:
  push:
    branches: [main, develop]  # run on push to main or develop
  pull_request:
    branches: [main]           # run on PRs targeting main

jobs:
  test:
    # GitHub provides free Linux runners for public repos
    runs-on: ubuntu-latest

    # SERVICE CONTAINERS: run alongside the job (like docker-compose)
    # These start before the job steps and stop after.
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: contacts_test
        # GitHub maps container port 5432 to host port 5432
        ports: ["5432:5432"]
        # Wait for postgres to be ready before running tests
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      # 1. Get the code
      - uses: actions/checkout@v4

      # 2. Set up Python
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"  # cache pip downloads between runs (faster)

      # 3. Install dependencies
      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      # 4. Run unit tests with SQLite (fast, no external services)
      - name: Run unit tests
        run: pytest tests/unit/ -v
        # Unit tests use SQLite in-memory — no DATABASE_URL needed.
        # These are the fastest tests and catch most logic errors.

      # 5. Run integration tests with PostgreSQL + Redis
      - name: Run integration tests
        env:
          # These env vars are available to the app during integration tests.
          # They connect to the service containers above.
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/contacts_test
          REDIS_URL: redis://localhost:6379/0

          # Secrets for JWT (fake values, only for tests)
          # NEVER use real secrets here — they'd be visible in logs.
          JWT_SECRET_KEY: ci-test-secret-minimum-32-characters-here
          JWT_ALGORITHM: HS256
          JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "30"
          JWT_REFRESH_TOKEN_EXPIRE_DAYS: "7"
          EMAIL_TOKEN_SECRET: ci-email-token-secret-32-chars-here
          EMAIL_TOKEN_EXPIRE_HOURS: "24"

          # Email: use fake SMTP (won't actually send)
          SMTP_HOST: localhost
          SMTP_PORT: "1025"
          SMTP_USER: test@test.com
          SMTP_PASSWORD: ""
          SMTP_FROM: test@test.com

          # Cloudinary: fake credentials (service is mocked in tests)
          CLOUDINARY_CLOUD_NAME: test
          CLOUDINARY_API_KEY: "test"
          CLOUDINARY_API_SECRET: test

          # App settings
          FRONTEND_URL: http://localhost:3000
          DEBUG: "true"

        run: |
          # Run migrations against the test database first
          alembic upgrade head

          # Run integration tests with coverage
          pytest tests/integration/ -v --cov=app --cov-report=xml --cov-fail-under=80

      # 6. Upload coverage report (optional but useful)
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        if: always()  # upload even if tests fail
        with:
          file: coverage.xml
          fail_ci_if_error: false  # don't fail CI if upload fails
"""


EXPLANATION = """
# HOW IT WORKS

Push to GitHub
    ↓
GitHub detects .github/workflows/ci.yml
    ↓
Spins up ubuntu-latest runner
Starts postgres:16-alpine and redis:7-alpine as service containers
    ↓
Checks out your code
    ↓
pip install -r requirements-dev.txt
    ↓
pytest tests/unit/              ← SQLite, fast
pytest tests/integration/       ← PostgreSQL + Redis, comprehensive
    ↓
Pass → green checkmark on PR/commit
Fail → red X, merge blocked (if branch protection enabled)

# BRANCH PROTECTION (optional but recommended)

In GitHub → Settings → Branches → Branch protection rules:
  - Require status checks to pass before merging
  - Select: "CI / test"
  - This prevents merging broken code into main

# RENDER AUTO-DEPLOY

In Render → Settings:
  - Auto-deploy: Enabled
  - Render watches GitHub for pushes to main
  - If CI fails, Render still deploys (by default)
  - To prevent this: use GitHub Environments with required checks

# SECRETS (real credentials)

For production, store real credentials as GitHub Secrets:
  GitHub → Settings → Secrets and variables → Actions
  Add: CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, etc.

Then reference them in the workflow:
  env:
    CLOUDINARY_API_KEY: ${{ secrets.CLOUDINARY_API_KEY }}

Secrets are masked in logs. Never commit real credentials.
"""


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--explain":
        print(EXPLANATION)
    else:
        # Default: print the workflow YAML (redirect to file)
        print(WORKFLOW)

    # If writing to stdout (redirected to file), also print explanation to stderr
    if not sys.stdout.isatty():
        import sys
        print(EXPLANATION, file=sys.stderr)
        print("✅ Workflow written.", file=sys.stderr)
        print("Next steps:", file=sys.stderr)
        print("  git add .github/workflows/ci.yml", file=sys.stderr)
        print("  git commit -m 'add CI workflow'", file=sys.stderr)
        print("  git push", file=sys.stderr)
    else:
        print()
        print("Usage:")
        print("  python 07_github_actions_explained.py > .github/workflows/ci.yml")
        print("  python 07_github_actions_explained.py --explain")
