# Standalone Examples

Each file covers one topic independently. Study these before (or alongside) the main contacts_api code.

| # | File | Topic | Needs |
|---|------|-------|-------|
| 01 | `01_email_sending.py` | smtplib → FastAPI-Mail | MailHog (optional) |
| 02 | `02_email_verification_tokens.py` | Token security: UUID → JWT+TTL | Nothing |
| 03 | `03_cloudinary_upload.py` | File upload + MIME validation | Cloudinary account |
| 04 | `04_rate_limiting.py` | SlowAPI rate limiting | Nothing |
| 05 | `05_redis_caching.py` | Cache-aside + token blacklist | Redis |
| 06 | `06_async_testing.py` | pytest-asyncio + AsyncMock | `pytest 06_async_testing.py` |
| 07 | `07_github_actions_explained.py` | Generates CI/CD YAML | Nothing |

## Quick Start

```bash
# Self-contained (no external services)
python 02_email_verification_tokens.py
python 07_github_actions_explained.py

# With MailHog
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
python 01_email_sending.py

# With Redis
docker run -p 6379:6379 redis:7-alpine
python 05_redis_caching.py

# Run as tests
pytest 06_async_testing.py -v

# Generate CI config
python 07_github_actions_explained.py > ../contacts_api/.github/workflows/ci.yml
```
