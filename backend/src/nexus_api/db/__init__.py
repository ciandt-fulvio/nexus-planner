"""
Database layer for Nexus API.

This package provides database access and ORM table definitions using SQLAlchemy 2.0
with async support via aiosqlite.

Exports:
    - engine: Async SQLite engine
    - async_session: Session factory for async database operations
    - Base: Declarative base for SQLAlchemy models
    - get_db: Dependency for FastAPI route handlers
"""
