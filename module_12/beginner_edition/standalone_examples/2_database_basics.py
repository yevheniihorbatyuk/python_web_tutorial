"""
SQLAlchemy Database Basics

Learn fundamental database concepts:
- Define models
- Create tables
- CRUD operations
- Sessions
- Relationships

This example uses SQLite (no setup needed).
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import declarative_base, Session, relationship
from typing import List, Optional

# ============================================================================
# DATABASE SETUP
# ============================================================================

# Create SQLite database (file-based, no server needed)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL statements

# Base class for all models
Base = declarative_base()

# ============================================================================
# DEFINE MODELS
# ============================================================================

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # Relationship to posts
    posts: "List[Post]" = relationship("Post", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

class Post(Base):
    """Post model - represents a blog post."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to user
    author: User = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author_id={self.author_id})>"

# ============================================================================
# CREATE TABLES
# ============================================================================

Base.metadata.create_all(bind=engine)
print("✅ Tables created")

# ============================================================================
# CRUD OPERATIONS
# ============================================================================

def get_db():
    """Get database session."""
    db = Session(engine)
    return db

# --- CREATE (INSERT) ---

def create_user(db: Session, name: str, email: str) -> User:
    """Create a new user."""
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)  # Load the ID assigned by database
    print(f"✅ Created: {user}")
    return user

def create_post(db: Session, title: str, content: str, author_id: int) -> Post:
    """Create a new post."""
    post = Post(title=title, content=content, author_id=author_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    print(f"✅ Created: {post}")
    return post

# --- READ (SELECT) ---

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    user = db.query(User).filter(User.email == email).first()
    return user

def get_all_users(db: Session) -> List[User]:
    """Get all users."""
    users = db.query(User).all()
    return users

def get_user_posts(db: Session, user_id: int) -> List[Post]:
    """Get all posts by a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user.posts  # Access related posts
    return []

# --- UPDATE ---

def update_user(db: Session, user_id: int, name: str, email: str) -> Optional[User]:
    """Update user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.email = email
        db.commit()
        db.refresh(user)
        print(f"✅ Updated: {user}")
        return user
    return None

# --- DELETE ---

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        print(f"✅ Deleted user {user_id}")
        return True
    return False

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    db = get_db()

    print("\n=== CREATE ===")
    user1 = create_user(db, "Alice", "alice@example.com")
    user2 = create_user(db, "Bob", "bob@example.com")

    post1 = create_post(db, "My First Post", "This is my first post", user1.id)
    post2 = create_post(db, "Another Post", "Another interesting post", user1.id)
    post3 = create_post(db, "Bob's Post", "Bob's first post", user2.id)

    print("\n=== READ ===")
    print(f"Get user by ID 1: {get_user_by_id(db, 1)}")
    print(f"Get user by email: {get_user_by_email(db, 'bob@example.com')}")
    print(f"All users: {get_all_users(db)}")

    print("\n=== RELATIONSHIPS ===")
    alice = get_user_by_id(db, user1.id)
    print(f"Alice's posts: {alice.posts}")
    print(f"Alice's post titles: {[p.title for p in alice.posts]}")

    print("\n=== UPDATE ===")
    update_user(db, user1.id, "Alice Updated", "alice.updated@example.com")

    print("\n=== QUERY PATTERNS ===")

    # Find posts by title
    post = db.query(Post).filter(Post.title.contains("First")).first()
    print(f"Post containing 'First': {post}")

    # Count posts
    post_count = db.query(Post).count()
    print(f"Total posts: {post_count}")

    # Filter with multiple conditions
    posts = db.query(Post).filter(
        (Post.author_id == user1.id) & (Post.title.contains("Post"))
    ).all()
    print(f"Posts by Alice containing 'Post': {posts}")

    print("\n=== DELETE ===")
    # delete_user(db, user2.id)  # Uncomment to delete

    db.close()
    print("\n✅ Example complete - check test.db file")
