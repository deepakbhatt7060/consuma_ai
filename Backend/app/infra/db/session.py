
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings


#async database engine and session creation
def create_async_engine_and_session():
    settings = Settings()
    DATABASE_URL = settings.database_url
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True
    )
    asyncSession = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    return engine, asyncSession
