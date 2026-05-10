import os
import httpx
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


class GeminiService:
    """Servicio para integración con Google Gemini AI"""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL

    async def generate_content(self, prompt: str, force_json: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_KEY no está configurada en las variables de entorno")

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        generation_config: Dict[str, Any] = {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 65536,
        }
        if force_json:
            generation_config["responseMimeType"] = "application/json"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": generation_config
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)

            if response.status_code != 200:
                raise Exception(f"Error en Gemini API: {response.status_code} - {response.text}")

            return response.json()

    def extract_text_response(self, gemini_response: Dict[str, Any]) -> str:
        try:
            return gemini_response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"No se pudo extraer texto de la respuesta: {e}")

    def extract_json_from_response(self, text_response: str) -> Dict[str, Any]:
        """Extrae JSON limpiando posibles bloques markdown."""
        text = text_response.strip()
        if text.startswith("```"):
            # Eliminar apertura: ```json o ```
            text = text.split("\n", 1)[-1]
            # Eliminar cierre ```
            if text.endswith("```"):
                text = text[: text.rfind("```")].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"No se pudo parsear JSON de la respuesta: {e}")

    async def generate_training_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_training_plan_prompt(user_profile)
        # force_json=True → Gemini devuelve JSON puro sin markdown
        response = await self.generate_content(prompt, force_json=True)
        text_response = self.extract_text_response(response)
        plan = self.extract_json_from_response(text_response)
        return {
            "plan": plan,
            "prompt_used": prompt,
            "model_version": GEMINI_MODEL
        }

    def _build_training_plan_prompt(self, profile: Dict[str, Any]) -> str:
        goal_descriptions = {
            "hypertrophy": "hipertrofia muscular (ganar masa muscular)",
            "strength": "ganancia de fuerza máxima",
            "weight_loss": "pérdida de peso y definición",
            "endurance": "resistencia cardiovascular",
            "marathon": "preparación para maratón (42 km)",
            "half_marathon": "preparación para medio maratón (21 km)",
            "bodyweight": "entrenamiento con peso corporal",
            "general_fitness": "fitness general y salud"
        }
        period_weeks = {"short": 8, "medium": 16, "long": 24}
        level_descriptions = {
            "beginner": "principiante (menos de 1 año)",
            "intermediate": "intermedio (1-3 años de experiencia)",
            "advanced": "avanzado (más de 3 años)"
        }

        total_weeks = period_weeks.get(profile.get("training_period", "medium"), 16)

        resources = []
        if profile.get("has_gym_access"):
            resources.append("gimnasio completo")
        if profile.get("has_home_equipment"):
            eq = profile.get("home_equipment_list", [])
            resources.append(f"equipamiento en casa: {', '.join(eq)}" if eq else "equipamiento básico en casa")
        if profile.get("has_bike"):
            resources.append(f"bicicleta ({profile.get('bike_type', 'bici')})")
        if profile.get("has_running_gear"):
            resources.append("equipamiento para correr")
        if profile.get("outdoor_space_available"):
            resources.append("espacio al aire libre")
        if not resources:
            resources = ["sin equipamiento específico"]

        primary_goal = goal_descriptions.get(profile.get("primary_goal", ""), profile.get("primary_goal", "fitness general"))
        secondary_goals = ", ".join(profile.get("secondary_goals", [])) or "ninguno"
        preferred_days = ", ".join(profile.get("preferred_days", [])) or "flexible"
        training_types = ", ".join(profile.get("preferred_training_types", [])) or "variado"
        disliked = ", ".join(profile.get("disliked_exercises", [])) or "ninguno"
        resources_str = "\n".join(f"  - {r}" for r in resources)

        prompt = f"""Eres un entrenador personal profesional. Crea un plan de entrenamiento personalizado en formato JSON.

## PERFIL DEL USUARIO

**Datos físicos:**
- Edad: {profile.get('age', '?')} años | Género: {profile.get('gender', '?')}
- Altura: {profile.get('height_cm', '?')} cm | Peso: {profile.get('weight_kg', '?')} kg
- % grasa corporal: {profile.get('body_fat_percentage', 'no especificado')}%

**Objetivos:**
- Principal: {primary_goal}
- Secundarios: {secondary_goals}
- Peso objetivo: {profile.get('target_weight_kg', 'no especificado')} kg

**Disponibilidad:**
- {profile.get('training_days_per_week', 3)} días/semana
- Días preferidos: {preferred_days}
- Duración por sesión: {profile.get('session_duration_minutes', 60)} min

**Duración del plan:** {total_weeks} semanas
{f"- Evento: {profile.get('target_event_name')} ({profile.get('target_event_date')})" if profile.get('target_event_name') else ""}

**Recursos disponibles:**
{resources_str}

**Experiencia:** {level_descriptions.get(profile.get('fitness_level', 'intermediate'), 'intermedio')}
- Años entrenando: {profile.get('years_training', '?')}
- Lesiones previas: {profile.get('previous_injuries', 'ninguna')}
- Condiciones de salud: {profile.get('health_conditions', 'ninguna')}

**Alimentación:** {profile.get('diet_type', 'omnívora')} | {profile.get('meals_per_day', '?')} comidas/día

**Preferencias:**
- Tipos de entrenamiento: {training_types}
- Ejercicios a evitar: {disliked}
- Favoritos: {", ".join(profile.get("favorite_exercises", [])) or "no especificados"}

---

## INSTRUCCIONES

Genera el plan con las siguientes secciones. Para evitar respuestas demasiado largas, genera **una semana representativa por fase** (no todas las semanas):
- Cada semana representativa tiene 7 días completos
- Usa el campo "progression_notes" para indicar cómo progresar el resto de semanas de esa fase

Estructura del JSON de respuesta:

{{
  "plan_name": "string — nombre descriptivo del plan",
  "overview": "string — descripción general (3-4 párrafos) con el enfoque, metodología y qué esperar",
  "total_weeks": {total_weeks},
  "phases": [
    {{
      "phase_number": 1,
      "name": "string",
      "weeks": [1, 2, 3, 4],
      "focus": "string",
      "description": "string",
      "volume_adjustment": "string (ej: 100%)",
      "intensity_adjustment": "string (ej: Moderada)"
    }}
  ],
  "weeks": [
    {{
      "week_number": 1,
      "phase": "string — nombre de la fase",
      "is_deload": false,
      "focus": "string",
      "progression_notes": "string — cómo progresar el resto de semanas de esta fase",
      "days": [
        {{
          "day_number": 1,
          "day_name": "Lunes",
          "type": "strength | cardio | rest | active_recovery",
          "session_name": "string",
          "duration_minutes": 60,
          "warmup": [
            {{ "name": "string", "duration": "string", "notes": "string" }}
          ],
          "exercises": [
            {{
              "name": "string",
              "muscle_group": "chest | back | shoulders | arms | legs | glutes | core",
              "sets": 4,
              "reps": "string (ej: 10-12)",
              "rir": "string (ej: 2-3)",
              "rest_seconds": 120,
              "notes": "string — clave técnica más importante",
              "alternatives": ["string"]
            }}
          ],
          "cardio": {{
            "type": "string (bici|trail|carrera|otro)",
            "duration_minutes": 45,
            "intensity": "string (Z2|HIIT|etc)",
            "distance_km": 10,
            "notes": "string"
          }},
          "cooldown": [
            {{ "name": "string", "duration": "string", "notes": "string" }}
          ],
          "session_notes": "string"
        }}
      ],
      "weekly_goals": ["string"],
      "weekly_notes": "string"
    }}
  ],
  "nutrition_guidelines": {{
    "daily_calories": 2500,
    "protein_grams": 180,
    "carbs_grams": 300,
    "fat_grams": 80,
    "pre_workout_meal": "string",
    "post_workout_meal": "string",
    "hydration_liters": 3,
    "supplements_suggested": ["string"]
  }},
  "progression_rules": {{
    "strength": "string",
    "cardio": "string",
    "deload_protocol": "string"
  }},
  "important_notes": ["string"]
}}

IMPORTANTE:
- Responde SOLO con el JSON, sin texto antes ni después
- Los campos "cardio" y "exercises" son opcionales según el tipo de día
- Días de tipo "rest" o "active_recovery" solo necesitan day_number, day_name, type, session_name y session_notes
- Adapta TODO al perfil y recursos del usuario
- Genera una semana representativa por fase en el array "weeks" (una entrada por fase, no por semana)
- En "phases", el campo "weeks" debe ser un array con todos los números de semana de esa fase (ej: [1, 2, 3, 4])"""

        return prompt

    async def get_plan_adjustment_suggestions(
        self,
        plan: Dict[str, Any],
        weekly_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Eres un entrenador personal analizando el progreso semanal de un atleta.

## SEMANA {weekly_feedback.get('week_number', 1)} — FEEDBACK

- Sesiones completadas: {weekly_feedback.get('sessions_completed', 0)} de {weekly_feedback.get('sessions_planned', 0)}
- Energía (1-10): {weekly_feedback.get('energy_level', 5)}
- Agujetas/dolor (1-10): {weekly_feedback.get('soreness_level', 5)}
- Motivación (1-10): {weekly_feedback.get('motivation_level', 5)}
- Notas: {weekly_feedback.get('user_notes', 'Sin notas')}

Proporciona sugerencias de ajuste para la próxima semana en JSON válido:

{{
  "analysis": "string",
  "adjustments": [
    {{ "type": "string", "suggestion": "string", "reason": "string" }}
  ],
  "motivation_message": "string",
  "warnings": ["string"],
  "next_week_focus": "string"
}}"""

        response = await self.generate_content(prompt, force_json=True)
        text_response = self.extract_text_response(response)
        return self.extract_json_from_response(text_response)


# Instancia singleton del servicio
gemini_service = GeminiService()
