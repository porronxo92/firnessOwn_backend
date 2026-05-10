"""
Script para inicializar la base de datos.
Crea todas las tablas definidas en los modelos SQLAlchemy.

Uso:
    python -m bbdd.init_db

O desde el directorio backend:
    python bbdd/init_db.py
"""

import asyncio
import sys
import os

# Añadir el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, Base
from app.models import (
    User, Phase, Exercise, CustomExercise, 
    WorkoutLog, CardioLog, UserProfile, 
    GeneratedPlan, WeeklyProgress
)


async def create_tables():
    """Crea todas las tablas en la base de datos."""
    print("🔄 Conectando a la base de datos...")
    
    async with engine.begin() as conn:
        print("📋 Creando tablas...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas creadas correctamente")
        
        # Verificar tablas creadas
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = result.fetchall()
        
        print(f"\n📊 Tablas en la base de datos ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")


async def drop_tables():
    """Elimina todas las tablas de la base de datos. ¡CUIDADO!"""
    print("⚠️  ADVERTENCIA: Esto eliminará TODAS las tablas y datos.")
    confirm = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
    
    if confirm != "SI":
        print("❌ Operación cancelada")
        return
    
    async with engine.begin() as conn:
        print("🗑️  Eliminando tablas...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tablas eliminadas")


async def reset_database():
    """Elimina y recrea todas las tablas."""
    print("🔄 Reseteando base de datos...")
    
    async with engine.begin() as conn:
        print("🗑️  Eliminando tablas existentes...")
        await conn.run_sync(Base.metadata.drop_all)
        
        print("📋 Creando tablas nuevas...")
        await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Base de datos reseteada correctamente")


async def check_connection():
    """Verifica la conexión a la base de datos."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexión exitosa")
            print(f"📊 PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def main():
    """Función principal con menú de opciones."""
    print("\n" + "="*50)
    print("🏋️  FitnessOwn - Gestión de Base de Datos")
    print("="*50 + "\n")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("Opciones:")
        print("  1. check    - Verificar conexión")
        print("  2. create   - Crear tablas")
        print("  3. drop     - Eliminar tablas (¡PELIGRO!)")
        print("  4. reset    - Resetear base de datos (drop + create)")
        print()
        command = input("Selecciona una opción: ").strip().lower()
    
    if command in ['1', 'check']:
        asyncio.run(check_connection())
    elif command in ['2', 'create']:
        asyncio.run(create_tables())
    elif command in ['3', 'drop']:
        asyncio.run(drop_tables())
    elif command in ['4', 'reset']:
        confirm = input("⚠️  ¿Resetear la base de datos? (escribe 'RESET' para confirmar): ")
        if confirm == "RESET":
            asyncio.run(reset_database())
        else:
            print("❌ Operación cancelada")
    else:
        print(f"❌ Comando no reconocido: {command}")


if __name__ == "__main__":
    main()
