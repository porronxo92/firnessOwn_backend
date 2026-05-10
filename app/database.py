import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Obtener DATABASE_URL y convertir a asyncpg si es necesario
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://trainer:trainer_local@localhost:5432/training_tracker")

# Convertir postgresql:// a postgresql+asyncpg:// para Supabase u otras URLs
if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Reemplazar variables de entorno en la URL (como ${PASSWORD_BBDD})
import re
def replace_env_vars(url):
    pattern = r'\$\{(\w+)\}'
    def replacer(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))
    return re.sub(pattern, replacer, url)

DATABASE_URL = replace_env_vars(DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
