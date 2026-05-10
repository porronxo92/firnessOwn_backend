"""
Seed data for the Training Tracker application.
Run: python -m app.seed.seed_data
"""
import asyncio
from sqlalchemy import select
from app.database import engine, async_session, Base
from app.models.phase import Phase
from app.models.exercise import Exercise


PHASES_DATA = [
    {
        "num": 1,
        "name": "Adaptación",
        "weeks_start": 1,
        "weeks_end": 4,
        "focus": "Base técnica y neurológica",
        "description": "Establecer patrones motores correctos con cargas moderadas. RIR alto para evitar fatiga excesiva.",
        "series_per_muscle": "10-12",
        "rep_range": "10-15",
        "rir_target": "3-4",
        "rest_seconds_min": 90,
        "rest_seconds_max": 120,
    },
    {
        "num": 2,
        "name": "Acumulación",
        "weeks_start": 5,
        "weeks_end": 8,
        "focus": "Volumen e hipertrofia",
        "description": "Incrementar volumen total y cargas. Más series por grupo muscular, RIR reducido.",
        "series_per_muscle": "12-16",
        "rep_range": "8-12",
        "rir_target": "2-3",
        "rest_seconds_min": 90,
        "rest_seconds_max": 150,
    },
    {
        "num": 3,
        "name": "Intensificación",
        "weeks_start": 9,
        "weeks_end": 12,
        "focus": "Fuerza máxima",
        "description": "Cargas pesadas, baja repetición, técnicas avanzadas (drop sets, rest-pause).",
        "series_per_muscle": "10-14",
        "rep_range": "5-8",
        "rir_target": "1-2",
        "rest_seconds_min": 120,
        "rest_seconds_max": 180,
    },
    {
        "num": 4,
        "name": "Resolución",
        "weeks_start": 13,
        "weeks_end": 16,
        "focus": "Densidad y superseries",
        "description": "Superseries con descansos cortos. Mantener fuerza, maximizar densidad de entrenamiento.",
        "series_per_muscle": "12-16",
        "rep_range": "8-15",
        "rir_target": "2-3",
        "rest_seconds_min": 60,
        "rest_seconds_max": 90,
    },
]

EXERCISES_DATA = {
    # Phase 1 - Adaptación
    1: {
        "pull": [
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, bíceps braquial, braquiorradial", "default_sets": 4, "default_reps": "8", "rir": "3-4", "notes": "Rango completo, sin kipping", "sort_order": 1},
            {"name": "Remo Landmine", "muscle_group": "back", "muscle_desc": "Dorsal ancho, trapecio medio, romboides, bíceps", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "Unilateral, codo al cuerpo", "sort_order": 2},
            {"name": "Face pull con cuerda", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior, trapecio, infraespinoso, redondo menor", "default_sets": 3, "default_reps": "15", "rir": "4", "notes": "Rotación externa", "sort_order": 3},
            {"name": "Curl bíceps barra EZ", "muscle_group": "arms", "muscle_desc": "Bíceps braquial, braquial anterior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Sin swinging", "sort_order": 4},
            {"name": "Curl martillo mancuernas", "muscle_group": "arms", "muscle_desc": "Braquiorradial, bíceps braquial", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "Codos fijos", "sort_order": 5},
        ],
        "push": [
            {"name": "Press Banca Recto", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, deltoides anterior, tríceps", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "Técnica base", "sort_order": 1},
            {"name": "Press Banca Inclinado", "muscle_group": "chest", "muscle_desc": "Pectoral superior, deltoides anterior, tríceps", "default_sets": 4, "default_reps": "12", "rir": "3-4", "notes": "30-45°", "sort_order": 2},
            {"name": "Press Militar Mancuernas", "muscle_group": "shoulders", "muscle_desc": "Deltoides anterior y lateral, tríceps, trapecio superior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "", "sort_order": 3},
            {"name": "Elevaciones Laterales", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral, supraespinoso", "default_sets": 4, "default_reps": "15", "rir": "3", "notes": "Sin impulso", "sort_order": 4},
            {"name": "Fondos en paralelas", "muscle_group": "chest", "muscle_desc": "Pectoral inferior, tríceps, deltoides anterior", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "", "sort_order": 5},
            {"name": "Extensión tríceps cuerda", "muscle_group": "arms", "muscle_desc": "Tríceps (cabeza lateral y larga)", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "", "sort_order": 6},
        ],
        "legs": [
            {"name": "Sentadilla Trasera", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, isquiotibiales, core", "default_sets": 4, "default_reps": "10", "rir": "3-4", "notes": "Profundidad completa", "sort_order": 1},
            {"name": "Peso Muerto Rumano", "muscle_group": "back", "muscle_desc": "Isquiotibiales, glúteos, erectores espinales", "default_sets": 4, "default_reps": "10", "rir": "3-4", "notes": "Hip hinge", "sort_order": 2},
            {"name": "Hip Thrust con barra", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor, isquiotibiales", "default_sets": 4, "default_reps": "12", "rir": "3", "notes": "Isométrico 1s arriba", "sort_order": 3},
            {"name": "Zancada Búlgara", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, estabilizadores de cadera", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "", "sort_order": 4},
            {"name": "Abductores máquina", "muscle_group": "glutes", "muscle_desc": "Glúteo medio, tensor fascia lata", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "Glúteo medio", "sort_order": 5},
            {"name": "Curl femoral tumbado", "muscle_group": "legs", "muscle_desc": "Isquiotibiales (bíceps femoral, semitendinoso)", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "", "sort_order": 6},
        ],
    },
    # Phase 2 - Acumulación
    2: {
        "pull": [
            {"name": "Remo Landmine pesado", "muscle_group": "back", "muscle_desc": "Dorsal ancho, trapecio medio, romboides", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "Carga ↑, técnica intacta", "sort_order": 1},
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, bíceps", "default_sets": 4, "default_reps": "6-8", "rir": "2", "notes": "", "sort_order": 2},
            {"name": "Pull-over mancuerna", "muscle_group": "back", "muscle_desc": "Dorsal ancho, serrato anterior, pectoral", "default_sets": 3, "default_reps": "12", "rir": "3", "notes": "", "sort_order": 3},
            {"name": "Face pull + encogimiento", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior, trapecio superior y medio", "default_sets": 3, "default_reps": "15", "rir": "3", "notes": "", "sort_order": 4},
            {"name": "Curl bíceps concentrado", "muscle_group": "arms", "muscle_desc": "Bíceps braquial (pico), braquial anterior", "default_sets": 4, "default_reps": "12", "rir": "2", "notes": "", "sort_order": 5},
        ],
        "push": [
            {"name": "Press Banca Recto", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, deltoides anterior, tríceps", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "Rampa de activación", "sort_order": 1},
            {"name": "Press Inclinado Mancuernas", "muscle_group": "chest", "muscle_desc": "Pectoral superior, deltoides anterior", "default_sets": 4, "default_reps": "10", "rir": "2", "notes": "", "sort_order": 2},
            {"name": "Press Militar Barra", "muscle_group": "shoulders", "muscle_desc": "Deltoides anterior y lateral, tríceps, trapecio", "default_sets": 4, "default_reps": "8", "rir": "2", "notes": "", "sort_order": 3},
            {"name": "Elevaciones laterales cable", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral", "default_sets": 4, "default_reps": "15", "rir": "2", "notes": "", "sort_order": 4},
            {"name": "Fondos lastrados", "muscle_group": "chest", "muscle_desc": "Pectoral inferior, tríceps, deltoides anterior", "default_sets": 3, "default_reps": "10", "rir": "2", "notes": "", "sort_order": 5},
            {"name": "Press francés + extensión", "muscle_group": "arms", "muscle_desc": "Tríceps (cabeza larga y lateral)", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "", "sort_order": 6},
        ],
        "legs": [
            {"name": "Sentadilla trasera", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, isquiotibiales, core", "default_sets": 5, "default_reps": "8", "rir": "2-3", "notes": "+5-10kg vs Fase 1", "sort_order": 1},
            {"name": "Peso Muerto Convencional", "muscle_group": "back", "muscle_desc": "Cadena posterior completa, erectores, core", "default_sets": 4, "default_reps": "6-8", "rir": "2-3", "notes": "Alterna con rumano", "sort_order": 2},
            {"name": "Hip Thrust pesado", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor, isquiotibiales", "default_sets": 5, "default_reps": "10", "rir": "2", "notes": "", "sort_order": 3},
            {"name": "Zancada Búlgara mancuernas", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, estabilizadores", "default_sets": 3, "default_reps": "10", "rir": "2", "notes": "", "sort_order": 4},
            {"name": "Abductores + aductores SS", "muscle_group": "glutes", "muscle_desc": "Glúteo medio, aductores", "default_sets": 3, "default_reps": "15", "rir": "2", "notes": "", "sort_order": 5},
            {"name": "Curl femoral + extensión", "muscle_group": "legs", "muscle_desc": "Isquiotibiales, cuádriceps", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "", "sort_order": 6},
        ],
    },
    # Phase 3 - Intensificación
    3: {
        "pull": [
            {"name": "Dominadas con lastre", "muscle_group": "back", "muscle_desc": "Dorsal ancho, romboides, bíceps", "default_sets": 5, "default_reps": "5-6", "rir": "1-2", "notes": "Top set pesado", "sort_order": 1},
            {"name": "Remo Landmine máximo", "muscle_group": "back", "muscle_desc": "Dorsal ancho, trapecio, romboides", "default_sets": 4, "default_reps": "6", "rir": "1", "notes": "Rest-pause opcional", "sort_order": 2},
            {"name": "Face pull eccéntrico", "muscle_group": "shoulders", "muscle_desc": "Deltoides posterior, trapecio, infraespinoso", "default_sets": 3, "default_reps": "12", "rir": "2", "notes": "3s excéntrico", "sort_order": 3},
            {"name": "Curl bíceps drop set", "muscle_group": "arms", "muscle_desc": "Bíceps braquial, braquial anterior", "default_sets": 3, "default_reps": "10+6", "rir": "1", "notes": "Drop 25%", "sort_order": 4},
        ],
        "push": [
            {"name": "Press Banca — Top set", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, deltoides anterior, tríceps", "default_sets": 5, "default_reps": "5-6", "rir": "1", "notes": "Back-off 80%", "sort_order": 1},
            {"name": "Press Inclinado pesado", "muscle_group": "chest", "muscle_desc": "Pectoral superior, deltoides anterior", "default_sets": 4, "default_reps": "8", "rir": "1-2", "notes": "", "sort_order": 2},
            {"name": "Press Militar pesado", "muscle_group": "shoulders", "muscle_desc": "Deltoides anterior y lateral, tríceps", "default_sets": 4, "default_reps": "6-8", "rir": "1-2", "notes": "", "sort_order": 3},
            {"name": "Laterales drop set", "muscle_group": "shoulders", "muscle_desc": "Deltoides lateral", "default_sets": 3, "default_reps": "15+8", "rir": "1", "notes": "", "sort_order": 4},
            {"name": "Fondos lastrados máx.", "muscle_group": "chest", "muscle_desc": "Pectoral inferior, tríceps", "default_sets": 3, "default_reps": "8", "rir": "1", "notes": "", "sort_order": 5},
        ],
        "legs": [
            {"name": "Sentadilla — Top set", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos, core", "default_sets": 5, "default_reps": "5", "rir": "1", "notes": "Back-off x3", "sort_order": 1},
            {"name": "Peso Muerto máximo", "muscle_group": "back", "muscle_desc": "Cadena posterior completa", "default_sets": 4, "default_reps": "5-6", "rir": "1", "notes": "", "sort_order": 2},
            {"name": "Hip Thrust máximo", "muscle_group": "glutes", "muscle_desc": "Glúteo mayor, isquiotibiales", "default_sets": 5, "default_reps": "8", "rir": "1", "notes": "Eccéntrico 3s", "sort_order": 3},
            {"name": "Zancada Búlgara pesada", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteos", "default_sets": 3, "default_reps": "8", "rir": "1-2", "notes": "", "sort_order": 4},
        ],
    },
    # Phase 4 - Resolución (Superseries)
    4: {
        "pull": [
            {"name": "SS-A: Dominadas + Curl bíceps", "muscle_group": "back", "muscle_desc": "Dorsal ancho, bíceps braquial", "default_sets": 4, "default_reps": "8+12", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 1},
            {"name": "SS-B: Remo + Face pull", "muscle_group": "back", "muscle_desc": "Dorsal ancho, deltoides posterior, trapecio", "default_sets": 4, "default_reps": "10+15", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 2},
            {"name": "SS-C: Polea alta + Curl martillo", "muscle_group": "back", "muscle_desc": "Dorsal ancho, braquiorradial, bíceps", "default_sets": 3, "default_reps": "12+12", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 3},
        ],
        "push": [
            {"name": "SS-A: Press banca + Laterales", "muscle_group": "chest", "muscle_desc": "Pectoral mayor, deltoides lateral", "default_sets": 4, "default_reps": "10+15", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 1},
            {"name": "SS-B: Inclinado + Press militar", "muscle_group": "chest", "muscle_desc": "Pectoral superior, deltoides anterior", "default_sets": 4, "default_reps": "10+10", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 2},
            {"name": "SS-C: Fondos + Tríceps polea", "muscle_group": "chest", "muscle_desc": "Pectoral inferior, tríceps", "default_sets": 3, "default_reps": "10+15", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 3},
        ],
        "legs": [
            {"name": "SS-A: Sentadilla + Hip thrust", "muscle_group": "legs", "muscle_desc": "Cuádriceps, glúteo mayor", "default_sets": 4, "default_reps": "10+12", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 1},
            {"name": "SS-B: Peso muerto + Abductores", "muscle_group": "back", "muscle_desc": "Cadena posterior, glúteo medio", "default_sets": 4, "default_reps": "10+15", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 2},
            {"name": "SS-C: Zancada + Curl femoral", "muscle_group": "legs", "muscle_desc": "Cuádriceps, isquiotibiales", "default_sets": 3, "default_reps": "10+12", "rir": "2-3", "notes": "Superserie, 60s descanso", "sort_order": 3},
        ],
    },
}


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Phase))
        if result.scalars().first():
            print("Database already seeded. Skipping.")
            return

        # Insert phases
        phase_map = {}
        for phase_data in PHASES_DATA:
            phase = Phase(**phase_data)
            session.add(phase)
            await session.flush()
            phase_map[phase.num] = phase.id
            print(f"  ✓ Phase {phase.num}: {phase.name}")

        # Insert exercises
        for phase_num, sessions in EXERCISES_DATA.items():
            phase_id = phase_map[phase_num]
            for session_type, exercises in sessions.items():
                for ex_data in exercises:
                    exercise = Exercise(
                        phase_id=phase_id,
                        session_type=session_type,
                        **ex_data
                    )
                    session.add(exercise)
                print(f"  ✓ Phase {phase_num} / {session_type}: {len(exercises)} exercises")

        await session.commit()
        print("\n✅ Seed data inserted successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
