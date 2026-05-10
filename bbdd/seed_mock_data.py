"""
Script para insertar datos mockeados en la base de datos.
Incluye fases, ejercicios, usuarios de prueba y logs de ejemplo.

Uso:
    python -m bbdd.seed_mock_data

O desde el directorio backend:
    python bbdd/seed_mock_data.py
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Añadir el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import async_session
from app.models import User, Phase, Exercise, UserProfile, WorkoutLog, CardioLog
from app.auth import get_password_hash


# =====================================================
# DATOS DE FASES
# =====================================================
PHASES_DATA = [
    {
        "num": 1,
        "name": "Adaptación",
        "weeks_start": 1,
        "weeks_end": 4,
        "focus": "Base técnica",
        "description": "Fase de adaptación anatómica y aprendizaje de patrones de movimiento. Énfasis en técnica y conexión mente-músculo.",
        "series_per_muscle": "10-12",
        "rep_range": "10-15",
        "rir_target": "3-4",
        "rest_seconds_min": 90,
        "rest_seconds_max": 120
    },
    {
        "num": 2,
        "name": "Acumulación",
        "weeks_start": 5,
        "weeks_end": 8,
        "focus": "Volumen",
        "description": "Fase de acumulación de volumen. Incremento progresivo de la carga manteniendo técnica. Mayor número de series efectivas.",
        "series_per_muscle": "14-18",
        "rep_range": "8-12",
        "rir_target": "2-3",
        "rest_seconds_min": 90,
        "rest_seconds_max": 150
    },
    {
        "num": 3,
        "name": "Intensificación",
        "weeks_start": 9,
        "weeks_end": 12,
        "focus": "Intensidad",
        "description": "Fase de intensificación. Cargas más pesadas, menor volumen, máxima intensidad. Preparación para PRs.",
        "series_per_muscle": "12-14",
        "rep_range": "5-8",
        "rir_target": "1-2",
        "rest_seconds_min": 120,
        "rest_seconds_max": 180
    },
    {
        "num": 4,
        "name": "Resolución",
        "weeks_start": 13,
        "weeks_end": 16,
        "focus": "Superseries",
        "description": "Fase de resolución con superseries y circuitos. Alta densidad, trabajo metabólico, definición y resistencia muscular.",
        "series_per_muscle": "10-12",
        "rep_range": "10-15",
        "rir_target": "2-3",
        "rest_seconds_min": 60,
        "rest_seconds_max": 90
    }
]

# =====================================================
# DATOS DE EJERCICIOS POR FASE
# =====================================================
EXERCISES_DATA = {
    1: {  # Fase 1 - Adaptación
        "pull": [
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, trapecio medio, bíceps", "default_sets": 4, "default_reps": "8", "rir": "3-4", "notes": "Rango completo, sin kipping. Escápulas retraídas al inicio.", "sort_order": 1},
            {"name": "Remo Landmine", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, trapecio, erector espinal", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "Unilateral, codo pegado al cuerpo. Pausa arriba 1s.", "sort_order": 2},
            {"name": "Face pull con cuerda", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior, trapecio superior, rotadores externos", "default_sets": 3, "default_reps": "15", "rir": "4", "notes": "Rotación externa al final del movimiento. Codos altos.", "sort_order": 3},
            {"name": "Curl bíceps barra EZ", "muscle_group": "arms", "muscle_desc": "Bíceps braquial, braquial anterior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Sin swinging. Controlar la fase excéntrica 2-3s.", "sort_order": 4},
            {"name": "Curl martillo mancuernas", "muscle_group": "arms", "muscle_desc": "Braquiorradial, bíceps braquial", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Codos fijos al costado. Movimiento controlado.", "sort_order": 5},
        ],
        "push": [
            {"name": "Press Banca Recto", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, deltoides anterior, tríceps", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "Técnica base. Escápulas retraídas, arco lumbar natural.", "sort_order": 1},
            {"name": "Press Banca Inclinado", "muscle_group": "chest", "muscle_desc": "Pectoral mayor (porción clavicular), deltoides anterior", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "Inclinación 30-45°. Codos a 45° del torso.", "sort_order": 2},
            {"name": "Press Militar Mancuernas", "muscle_group": "shoulders", "muscle_desc": "Deltoides anterior y lateral, tríceps, trapecio superior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Sentado con respaldo. No hiperextender lumbar.", "sort_order": 3},
            {"name": "Elevaciones Laterales", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral", "default_sets": 4, "default_reps": "15", "rir": "3", "notes": "Sin impulso. Ligera flexión de codos, meñique ligeramente arriba.", "sort_order": 4},
            {"name": "Fondos en paralelas", "muscle_group": "chest", "muscle_desc": "Pectoral mayor inferior, tríceps, deltoides anterior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Torso ligeramente inclinado hacia adelante para énfasis pectoral.", "sort_order": 5},
            {"name": "Extensión tríceps cuerda", "muscle_group": "arms", "muscle_desc": "Tríceps (cabeza larga, lateral y medial)", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "Separar la cuerda al final. Codos fijos.", "sort_order": 6},
        ],
        "legs": [
            {"name": "Sentadilla Trasera", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, isquiotibiales, core", "default_sets": 4, "default_reps": "10", "rir": "3-4", "notes": "Profundidad completa. Rodillas en línea con pies.", "sort_order": 1},
            {"name": "Peso Muerto Rumano", "muscle_group": "back", "muscle_desc": "Isquiotibiales, glúteos, erector espinal", "default_sets": 4, "default_reps": "10", "rir": "3-4", "notes": "Hip hinge puro. Barra pegada a las piernas.", "sort_order": 2},
            {"name": "Hip Thrust con barra", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor, isquiotibiales", "default_sets": 4, "default_reps": "12", "rir": "3", "notes": "Isométrico 1s arriba. Chin tucked, mirada al frente.", "sort_order": 3},
            {"name": "Zancada Búlgara", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, isquiotibiales", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Pie trasero elevado en banco. Torso ligeramente inclinado.", "sort_order": 4},
            {"name": "Abductores máquina", "muscle_group": "glutes", "muscle_desc": "Glúteo medio, tensor de la fascia lata", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "Énfasis en glúteo medio. Pausa en posición abierta.", "sort_order": 5},
            {"name": "Curl femoral tumbado", "muscle_group": "legs", "muscle_desc": "Isquiotibiales", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Cadera pegada al banco. Flexión completa.", "sort_order": 6},
        ]
    },
    2: {  # Fase 2 - Acumulación
        "pull": [
            {"name": "Remo Landmine pesado", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, trapecio", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "Carga ↑, técnica intacta.", "sort_order": 1},
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal ancho, bíceps", "default_sets": 4, "default_reps": "6-8", "rir": "2", "notes": "Progresión en lastre.", "sort_order": 2},
            {"name": "Pull-over mancuerna", "muscle_group": "back", "muscle_desc": "Dorsal ancho, serrato anterior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Brazos ligeramente flexionados.", "sort_order": 3},
            {"name": "Face pull + encogimiento", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior, trapecio", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "Combinar tracción con encogimiento.", "sort_order": 4},
            {"name": "Curl bíceps concentrado", "muscle_group": "arms", "muscle_desc": "Bíceps braquial", "default_sets": 4, "default_reps": "12", "rir": "2", "notes": "Máxima contracción.", "sort_order": 5},
        ],
        "push": [
            {"name": "Press Banca Recto", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, tríceps", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "Rampa de activación.", "sort_order": 1},
            {"name": "Press Inclinado Mancuernas", "muscle_group": "chest", "muscle_desc": "Pectoral clavicular", "default_sets": 4, "default_reps": "10", "rir": "2", "notes": "Rango completo.", "sort_order": 2},
            {"name": "Press Militar Barra", "muscle_group": "shoulders", "muscle_desc": "Deltoides, tríceps", "default_sets": 4, "default_reps": "8", "rir": "2", "notes": "De pie preferentemente.", "sort_order": 3},
            {"name": "Elevaciones laterales cable", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral", "default_sets": 4, "default_reps": "15", "rir": "2", "notes": "Tensión constante.", "sort_order": 4},
            {"name": "Fondos lastrados", "muscle_group": "chest", "muscle_desc": "Pectoral inferior, tríceps", "default_sets": 3, "default_reps": "10", "rir": "2", "notes": "Añadir lastre progresivamente.", "sort_order": 5},
            {"name": "Press francés", "muscle_group": "arms", "muscle_desc": "Tríceps", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "Combinar con extensión.", "sort_order": 6},
        ],
        "legs": [
            {"name": "Sentadilla trasera", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "+5-10kg vs Fase 1.", "sort_order": 1},
            {"name": "Peso Muerto Convencional", "muscle_group": "back", "muscle_desc": "Posterior chain", "default_sets": 4, "default_reps": "6-8", "rir": "2-3", "notes": "Alterna con rumano.", "sort_order": 2},
            {"name": "Hip Thrust pesado", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor", "default_sets": 5, "default_reps": "10", "rir": "2", "notes": "Incrementar carga.", "sort_order": 3},
            {"name": "Zancada Búlgara mancuernas", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 3, "default_reps": "10", "rir": "2", "notes": "Añadir carga.", "sort_order": 4},
            {"name": "Abductores + aductores SS", "muscle_group": "glutes", "muscle_desc": "Glúteo medio, aductores", "default_sets": 3, "default_reps": "15", "rir": "2", "notes": "Superserie.", "sort_order": 5},
            {"name": "Curl femoral + extensión", "muscle_group": "legs", "muscle_desc": "Isquiotibiales, cuádriceps", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "Agonista-antagonista.", "sort_order": 6},
        ]
    },
    3: {  # Fase 3 - Intensificación
        "pull": [
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal, bíceps", "default_sets": 5, "default_reps": "5-6", "rir": "1-2", "notes": "Top set pesado.", "sort_order": 1},
            {"name": "Remo Landmine máximo", "muscle_group": "back", "muscle_desc": "Dorsal completo", "default_sets": 4, "default_reps": "6", "rir": "1", "notes": "Rest-pause opcional.", "sort_order": 2},
            {"name": "Face pull eccéntrico", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "3s excéntrico.", "sort_order": 3},
            {"name": "Curl bíceps drop set", "muscle_group": "arms", "muscle_desc": "Bíceps braquial", "default_sets": 3, "default_reps": "10+6", "rir": "1", "notes": "Drop 25%.", "sort_order": 4},
        ],
        "push": [
            {"name": "Press Banca - Top set", "muscle_group": "chest", "muscle_desc": "Pectoral, tríceps", "default_sets": 5, "default_reps": "5-6", "rir": "1", "notes": "Back-off al 80%.", "sort_order": 1},
            {"name": "Press Inclinado pesado", "muscle_group": "chest", "muscle_desc": "Pectoral clavicular", "default_sets": 4, "default_reps": "8", "rir": "1-2", "notes": "Máxima carga.", "sort_order": 2},
            {"name": "Press Militar pesado", "muscle_group": "shoulders", "muscle_desc": "Deltoides, tríceps", "default_sets": 4, "default_reps": "6-8", "rir": "1-2", "notes": "Buscar PR.", "sort_order": 3},
            {"name": "Laterales drop set", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral", "default_sets": 3, "default_reps": "15+8", "rir": "1", "notes": "Drop set.", "sort_order": 4},
            {"name": "Fondos lastrados máx.", "muscle_group": "chest", "muscle_desc": "Pectoral, tríceps", "default_sets": 3, "default_reps": "8", "rir": "1", "notes": "Máximo lastre.", "sort_order": 5},
        ],
        "legs": [
            {"name": "Sentadilla - Top set", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 5, "default_reps": "5", "rir": "1", "notes": "Back-off x3.", "sort_order": 1},
            {"name": "Peso Muerto máximo", "muscle_group": "back", "muscle_desc": "Posterior chain", "default_sets": 4, "default_reps": "5-6", "rir": "1", "notes": "Buscar PR.", "sort_order": 2},
            {"name": "Hip Thrust máximo", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor", "default_sets": 5, "default_reps": "8", "rir": "1", "notes": "Eccéntrico 3s.", "sort_order": 3},
            {"name": "Zancada Búlgara pesada", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 3, "default_reps": "8", "rir": "1-2", "notes": "Mancuernas pesadas.", "sort_order": 4},
        ]
    },
    4: {  # Fase 4 - Resolución (Superseries)
        "pull": [
            {"name": "SS: Dominadas + Curl bíceps", "muscle_group": "back", "muscle_desc": "Dorsal, bíceps", "default_sets": 4, "default_reps": "8+12", "rir": "2", "notes": "60s descanso.", "sort_order": 1},
            {"name": "SS: Remo + Face pull", "muscle_group": "back", "muscle_desc": "Dorsal, deltoides posterior", "default_sets": 4, "default_reps": "10+15", "rir": "2", "notes": "Alta densidad.", "sort_order": 2},
            {"name": "SS: Polea alta + curl martillo", "muscle_group": "back", "muscle_desc": "Dorsal, braquiorradial", "default_sets": 3, "default_reps": "12+12", "rir": "2", "notes": "Finisher.", "sort_order": 3},
        ],
        "push": [
            {"name": "SS: Press banca + Laterales", "muscle_group": "chest", "muscle_desc": "Pectoral, deltoides", "default_sets": 4, "default_reps": "10+15", "rir": "2", "notes": "60s descanso.", "sort_order": 1},
            {"name": "SS: Inclinado + Press militar", "muscle_group": "chest", "muscle_desc": "Pectoral, deltoides", "default_sets": 4, "default_reps": "10+10", "rir": "2", "notes": "Compound.", "sort_order": 2},
            {"name": "SS: Fondos + Tríceps polea", "muscle_group": "chest", "muscle_desc": "Pectoral, tríceps", "default_sets": 3, "default_reps": "10+15", "rir": "2", "notes": "Finisher.", "sort_order": 3},
        ],
        "legs": [
            {"name": "SS: Sentadilla + Hip thrust", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 4, "default_reps": "10+12", "rir": "2", "notes": "60s descanso.", "sort_order": 1},
            {"name": "SS: Peso muerto + Abductores", "muscle_group": "back", "muscle_desc": "Isquiotibiales, glúteo medio", "default_sets": 4, "default_reps": "10+15", "rir": "2", "notes": "Superserie.", "sort_order": 2},
            {"name": "SS: Zancada + Curl femoral", "muscle_group": "legs", "muscle_desc": "Cuádriceps, isquiotibiales", "default_sets": 3, "default_reps": "10+12", "rir": "2", "notes": "Finisher.", "sort_order": 3},
        ]
    }
}


async def seed_phases():
    """Inserta las fases del plan de entrenamiento."""
    async with async_session() as session:
        # Verificar si ya existen fases
        result = await session.execute(select(Phase))
        if result.scalars().first():
            print("⚠️  Las fases ya existen en la base de datos")
            return
        
        print("📋 Insertando fases...")
        for phase_data in PHASES_DATA:
            phase = Phase(**phase_data)
            session.add(phase)
        
        await session.commit()
        print(f"✅ {len(PHASES_DATA)} fases insertadas")


async def seed_exercises():
    """Inserta los ejercicios de cada fase."""
    async with async_session() as session:
        # Verificar si ya existen ejercicios
        result = await session.execute(select(Exercise))
        if result.scalars().first():
            print("⚠️  Los ejercicios ya existen en la base de datos")
            return
        
        # Obtener las fases
        result = await session.execute(select(Phase))
        phases = {p.num: p.id for p in result.scalars().all()}
        
        if not phases:
            print("❌ No hay fases en la base de datos. Ejecuta seed_phases primero.")
            return
        
        print("🏋️ Insertando ejercicios...")
        count = 0
        for phase_num, sessions in EXERCISES_DATA.items():
            phase_id = phases.get(phase_num)
            if not phase_id:
                continue
                
            for session_type, exercises in sessions.items():
                for ex_data in exercises:
                    exercise = Exercise(
                        phase_id=phase_id,
                        session_type=session_type,
                        **ex_data
                    )
                    session.add(exercise)
                    count += 1
        
        await session.commit()
        print(f"✅ {count} ejercicios insertados")


async def seed_test_users():
    """Crea usuarios de prueba."""
    async with async_session() as session:
        # Usuario demo (sin onboarding)
        result = await session.execute(select(User).where(User.username == "demo_user"))
        if not result.scalar_one_or_none():
            demo_user = User(
                username="demo_user",
                email="demo@fitnessown.com",
                password_hash=get_password_hash("demo123"),
                onboarding_completed=False
            )
            session.add(demo_user)
            print("✅ Usuario demo_user creado (password: demo123)")
        
        # Usuario test (con onboarding completado)
        result = await session.execute(select(User).where(User.username == "test_user"))
        if not result.scalar_one_or_none():
            test_user = User(
                username="test_user",
                email="test@fitnessown.com",
                password_hash=get_password_hash("test123"),
                onboarding_completed=True
            )
            session.add(test_user)
            print("✅ Usuario test_user creado (password: test123)")
        
        await session.commit()


async def seed_test_profile():
    """Crea el perfil del usuario de prueba."""
    async with async_session() as session:
        # Buscar el usuario test
        result = await session.execute(select(User).where(User.username == "test_user"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Usuario test_user no encontrado. Ejecuta seed_test_users primero.")
            return
        
        # Verificar si ya tiene perfil
        result = await session.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        if result.scalar_one_or_none():
            print("⚠️  El perfil ya existe")
            return
        
        profile = UserProfile(
            user_id=user.id,
            age=30,
            gender="male",
            height_cm=178.0,
            weight_kg=75.5,
            body_fat_percentage=18.0,
            primary_goal="hypertrophy",
            secondary_goals=["strength", "endurance"],
            target_weight_kg=80.0,
            training_days_per_week=4,
            preferred_days=["monday", "wednesday", "friday", "saturday"],
            session_duration_minutes=60,
            training_period="medium",
            has_gym_access=True,
            has_home_equipment=True,
            home_equipment_list=["Mancuernas", "Barra olímpica", "Banco ajustable"],
            has_bike=True,
            bike_type="gravel",
            has_running_gear=True,
            outdoor_space_available=True,
            fitness_level="intermediate",
            years_training=3.0,
            diet_type="omnivore",
            meals_per_day=4,
            preferred_training_types=["Fuerza/Pesas", "Running", "Ciclismo"],
            onboarding_completed=True,
            onboarding_completed_at=datetime.utcnow()
        )
        session.add(profile)
        await session.commit()
        print("✅ Perfil de test_user creado")


async def seed_workout_logs():
    """Crea logs de entrenamiento de ejemplo."""
    async with async_session() as session:
        # Buscar el usuario test
        result = await session.execute(select(User).where(User.username == "test_user"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Usuario test_user no encontrado")
            return
        
        # Verificar si ya hay logs
        result = await session.execute(select(WorkoutLog).where(WorkoutLog.user_id == user.id))
        if result.scalars().first():
            print("⚠️  Ya existen logs de entrenamiento")
            return
        
        # Obtener algunos ejercicios de fase 1
        result = await session.execute(
            select(Exercise).where(Exercise.phase_id == 1).limit(5)
        )
        exercises = result.scalars().all()
        
        if not exercises:
            print("❌ No hay ejercicios en la base de datos")
            return
        
        print("📝 Insertando logs de entrenamiento...")
        
        # Crear logs para los últimos 14 días
        today = date.today()
        logs_data = [
            {"exercise": "Press Banca Recto", "days_ago": 14, "weight": 60.0, "sets": 4, "reps": "10,10,9,8", "rir": "3"},
            {"exercise": "Press Banca Recto", "days_ago": 10, "weight": 62.5, "sets": 4, "reps": "10,10,10,9", "rir": "2-3"},
            {"exercise": "Press Banca Recto", "days_ago": 6, "weight": 65.0, "sets": 4, "reps": "10,9,9,8", "rir": "2"},
            {"exercise": "Press Banca Recto", "days_ago": 2, "weight": 67.5, "sets": 4, "reps": "10,10,9,9", "rir": "2"},
            {"exercise": "Sentadilla Trasera", "days_ago": 12, "weight": 80.0, "sets": 4, "reps": "8,8,7,7", "rir": "3"},
            {"exercise": "Sentadilla Trasera", "days_ago": 8, "weight": 85.0, "sets": 4, "reps": "8,8,8,7", "rir": "2-3"},
            {"exercise": "Sentadilla Trasera", "days_ago": 4, "weight": 87.5, "sets": 4, "reps": "8,8,7,7", "rir": "2"},
            {"exercise": "Dominadas con lastre", "days_ago": 13, "weight": 10.0, "sets": 4, "reps": "8,7,6,6", "rir": "3"},
            {"exercise": "Dominadas con lastre", "days_ago": 9, "weight": 12.5, "sets": 4, "reps": "8,7,7,6", "rir": "2-3"},
            {"exercise": "Dominadas con lastre", "days_ago": 5, "weight": 15.0, "sets": 4, "reps": "7,7,6,6", "rir": "2"},
        ]
        
        for log_data in logs_data:
            # Buscar el ejercicio
            exercise = next((e for e in exercises if e.name == log_data["exercise"]), None)
            if not exercise:
                continue
                
            log = WorkoutLog(
                user_id=user.id,
                exercise_id=exercise.id,
                log_date=today - timedelta(days=log_data["days_ago"]),
                weight_kg=Decimal(str(log_data["weight"])),
                sets_done=log_data["sets"],
                reps_done=log_data["reps"],
                rir_actual=log_data["rir"],
                notes="Log de prueba"
            )
            session.add(log)
        
        await session.commit()
        print(f"✅ {len(logs_data)} logs de entrenamiento insertados")


async def seed_cardio_logs():
    """Crea logs de cardio de ejemplo."""
    async with async_session() as session:
        # Buscar el usuario test
        result = await session.execute(select(User).where(User.username == "test_user"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Usuario test_user no encontrado")
            return
        
        # Verificar si ya hay logs
        result = await session.execute(select(CardioLog).where(CardioLog.user_id == user.id))
        if result.scalars().first():
            print("⚠️  Ya existen logs de cardio")
            return
        
        print("🚴 Insertando logs de cardio...")
        
        today = date.today()
        cardio_data = [
            {"type": "bici", "days_ago": 11, "duration": 90, "distance": 35.5, "zone": "Z2", "elevation": 450, "notes": "Ruta de montaña"},
            {"type": "trail", "days_ago": 7, "duration": 60, "distance": 10.2, "zone": "Z2-Z3", "elevation": 320, "notes": "Trail suave"},
            {"type": "bici", "days_ago": 4, "duration": 75, "distance": 30.0, "zone": "Z2", "elevation": 380, "notes": "Salida matutina"},
            {"type": "carrera", "days_ago": 2, "duration": 45, "distance": 8.5, "zone": "Z2", "notes": "Rodaje fácil"},
        ]
        
        for log_data in cardio_data:
            log = CardioLog(
                user_id=user.id,
                log_date=today - timedelta(days=log_data["days_ago"]),
                type=log_data["type"],
                duration_min=log_data["duration"],
                distance_km=Decimal(str(log_data["distance"])),
                zone=log_data["zone"],
                elevation_m=log_data.get("elevation"),
                notes=log_data.get("notes")
            )
            session.add(log)
        
        await session.commit()
        print(f"✅ {len(cardio_data)} logs de cardio insertados")


async def seed_all():
    """Ejecuta todos los seeds en orden."""
    print("\n" + "="*50)
    print("🌱 Ejecutando todos los seeds...")
    print("="*50 + "\n")
    
    await seed_phases()
    await seed_exercises()
    await seed_test_users()
    await seed_test_profile()
    await seed_workout_logs()
    await seed_cardio_logs()
    
    print("\n" + "="*50)
    print("✅ Todos los datos de prueba insertados")
    print("="*50)
    print("\nUsuarios de prueba:")
    print("  - demo_user / demo123 (sin onboarding)")
    print("  - test_user / test123 (con onboarding completo)")


def main():
    """Función principal."""
    print("\n" + "="*50)
    print("🌱 FitnessOwn - Seed de Datos de Prueba")
    print("="*50 + "\n")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("Opciones:")
        print("  1. all        - Ejecutar todos los seeds")
        print("  2. phases     - Solo fases")
        print("  3. exercises  - Solo ejercicios")
        print("  4. users      - Solo usuarios de prueba")
        print("  5. profile    - Solo perfil de test_user")
        print("  6. workouts   - Solo logs de entrenamiento")
        print("  7. cardio     - Solo logs de cardio")
        print()
        command = input("Selecciona una opción: ").strip().lower()
    
    if command in ['1', 'all']:
        asyncio.run(seed_all())
    elif command in ['2', 'phases']:
        asyncio.run(seed_phases())
    elif command in ['3', 'exercises']:
        asyncio.run(seed_exercises())
    elif command in ['4', 'users']:
        asyncio.run(seed_test_users())
    elif command in ['5', 'profile']:
        asyncio.run(seed_test_profile())
    elif command in ['6', 'workouts']:
        asyncio.run(seed_workout_logs())
    elif command in ['7', 'cardio']:
        asyncio.run(seed_cardio_logs())
    else:
        print(f"❌ Comando no reconocido: {command}")


if __name__ == "__main__":
    main()
