import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from btcedu.db import Base


@pytest.fixture
def db_engine():
    """In-memory SQLite engine for tests with FTS5."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    # Create FTS5 virtual table
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts "
            "USING fts5(chunk_id UNINDEXED, episode_id UNINDEXED, text)"
        ))
        conn.commit()
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Database session for tests."""
    factory = sessionmaker(bind=db_engine)
    session = factory()
    yield session
    session.close()
