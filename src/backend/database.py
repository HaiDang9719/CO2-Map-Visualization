from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'postgresql://developer:&yJv_4Sqw#vX2UbKB4Vw5NRJawRw!VV4@database:5432/geographic-information-system', echo=True)

session_maker = sessionmaker(bind=engine)


@contextmanager
def get_database():
    """Provide a transactional scope around a series of operations."""
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
