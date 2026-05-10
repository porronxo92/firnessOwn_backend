# 🔧 Training Tracker — Backend API

API REST con FastAPI para el sistema de seguimiento de entrenamiento personal. Gestiona usuarios, planes de entrenamiento, ejercicios, logs y estadísticas de progresión.

## 🛠 Stack Tecnológico

- **FastAPI** 0.110+ — Framework web async
- **SQLAlchemy** 2.0+ — ORM async con PostgreSQL
- **Alembic** — Migraciones de base de datos
- **Pydantic** v2 — Validación y serialización
- **python-jose** — JWT tokens
- **Passlib** — Hashing de contraseñas (bcrypt)
- **asyncpg** — Driver PostgreSQL asíncrono

## 📦 Instalación

### Requisitos
- Python 3.11 o superior
- PostgreSQL 14+ (o Docker)

### Setup Local

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows PowerShell:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

Crear archivo `.env` en la raíz del directorio backend:

```env
# Database
DATABASE_URL=postgresql+asyncpg://trainer:trainer_local@localhost:5432/training_tracker

# JWT
SECRET_KEY=tu_clave_secreta_muy_larga_cambiar_en_produccion_min_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (opcional)
CORS_ORIGINS=http://localhost:4200,https://tudominio.com
```

⚠️ **IMPORTANTE:** Cambiar `SECRET_KEY` en producción. Generar con:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Base de Datos

#### Con Docker (Recomendado para desarrollo)

```bash
# Desde la raíz del proyecto
docker-compose up -d db
```

#### Sin Docker

```bash
# Crear base de datos PostgreSQL
psql -U postgres
CREATE DATABASE training_tracker;
CREATE USER trainer WITH PASSWORD 'trainer_local';
GRANT ALL PRIVILEGES ON DATABASE training_tracker TO trainer;
\q
```

### Ejecutar Migraciones

```bash
# Aplicar migraciones
alembic upgrade head

# Poblar base de datos con seed data (4 fases + ejercicios)
python -m app.seed.seed_data
```

## 🚀 Ejecución

### Desarrollo

```bash
# Con recarga automática
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acceder a:
- **API:** http://localhost:8000
- **Docs interactivos:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Producción

```bash
# Con Gunicorn + Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                 # Entry point FastAPI
│   ├── database.py             # Configuración DB y session
│   ├── auth.py                 # Utilidades JWT y password hashing
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── user.py             # Usuario (auth)
│   │   ├── phase.py            # Fases del plan (4 fases)
│   │   ├── exercise.py         # Ejercicios base del plan
│   │   ├── custom_exercise.py  # Ejercicios personalizados
│   │   ├── workout_log.py      # Logs de entrenamiento
│   │   └── ...
│   │
│   ├── schemas/                # Schemas Pydantic (request/response)
│   │   ├── user.py
│   │   ├── phase.py
│   │   ├── exercise.py
│   │   ├── workout_log.py
│   │   └── ...
│   │
│   ├── routers/                # Endpoints API
│   │   ├── auth.py             # POST /register, /login, GET /me
│   │   ├── phases.py           # GET /phases, /phases/{id}
│   │   ├── exercises.py        # GET /exercises, /exercises/{id}
│   │   ├── logs.py             # CRUD de workout_logs
│   │   ├── custom_exercises.py # CRUD de ejercicios custom
│   │   ├── stats.py            # Estadísticas y progresión
│   │   └── ...
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── stats_service.py    # Cálculos de progreso, 1RM, PRs
│   │   └── progression_service.py  # Algoritmo de sobrecarga
│   │
│   └── seed/
│       └── seed_data.py        # Script para poblar DB inicial
│
├── alembic/                    # Migraciones de base de datos
│   ├── versions/
│   └── env.py
│
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Imagen Docker
└── README.md                   # Este archivo
```

## 🔌 API Endpoints

### Autenticación

```http
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me             # Requiere JWT
```

**Ejemplo Login:**
```json
POST /api/auth/login
Content-Type: application/json

{
  "username": "usuario",
  "password": "password123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Fases y Ejercicios

```http
GET    /api/phases
GET    /api/phases/{id}
GET    /api/phases/{id}/exercises?session_type=pull
GET    /api/exercises/{id}
GET    /api/exercises?phase_id=1&session_type=push
```

**Ejemplo Ejercicios de una Fase:**
```json
GET /api/phases/1/exercises?session_type=pull

Response 200:
{
  "pull": [
    {
      "id": 1,
      "name": "Dominadas con lastre",
      "muscle_group": "back",
      "default_sets": 4,
      "default_reps": "8",
      "rir": "3-4",
      "notes": "Rango completo, sin kipping"
    },
    ...
  ]
}
```

### Logs de Entrenamiento

```http
GET    /api/logs                # Filtros: exercise_id, date_from, limit
POST   /api/logs
PUT    /api/logs/{id}
DELETE /api/logs/{id}
GET    /api/logs/today
GET    /api/logs/recent?days=7
```

**Ejemplo Crear Log:**
```json
POST /api/logs
Authorization: Bearer {token}
Content-Type: application/json

{
  "exercise_id": 1,
  "log_date": "2026-05-10",
  "weight_kg": 75.5,
  "sets_done": 4,
  "reps_done": "8,8,7,7",
  "rir_actual": "2",
  "notes": "Buen día, subir peso próxima vez"
}

Response 201:
{
  "id": 42,
  "exercise_id": 1,
  "user_id": 1,
  "log_date": "2026-05-10",
  "weight_kg": 75.5,
  ...
}
```

### Ejercicios Personalizados

```http
GET    /api/custom-exercises?phase_id=1&session_type=pull
POST   /api/custom-exercises
PUT    /api/custom-exercises/{id}
DELETE /api/custom-exercises/{id}
```

### Estadísticas y Progreso

```http
GET    /api/stats/progress/{exercise_id}?limit=10
GET    /api/stats/maxes          # PRs por ejercicio
GET    /api/stats/volume?week=5  # Volumen semanal
GET    /api/stats/summary         # Resumen general
```

**Ejemplo Progreso:**
```json
GET /api/stats/progress/1?limit=5

Response 200:
{
  "exercise_id": 1,
  "exercise_name": "Dominadas con lastre",
  "points": [
    {
      "log_date": "2026-05-10",
      "weight_kg": 75.5,
      "sets_done": 4,
      "reps_done": "8,8,7,7",
      "estimated_1rm": 95.2
    },
    ...
  ],
  "max_weight": 75.5,
  "first_weight": 60.0,
  "delta_kg": 15.5,
  "trend": "up"
}
```

## 🗄 Modelos de Base de Datos

### Tablas Principales

- **users:** Usuarios de la app
- **phases:** 4 fases del plan (seed data)
- **exercises:** Ejercicios base por fase (seed data)
- **custom_exercises:** Ejercicios añadidos por usuario
- **workout_logs:** Registro de pesos, series, reps por sesión
- **cardio_logs:** Sesiones de cardio (bici, trail, etc.)

### Relaciones

```
users 1:N workout_logs
users 1:N custom_exercises
phases 1:N exercises
exercises 1:N workout_logs
custom_exercises 1:N workout_logs
```

Ver [modelos SQLAlchemy](./app/models/) para esquema completo.

## 🧪 Testing (TODO)

```bash
# Instalar dependencias de test
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest tests/ -v
```

## 🐳 Docker

### Build

```bash
docker build -t training-tracker-backend .
```

### Run

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e SECRET_KEY="..." \
  training-tracker-backend
```

O usar `docker-compose.yml` desde la raíz del proyecto:

```bash
docker-compose up backend
```

## 🌐 Despliegue

### Railway

1. Conectar repositorio GitHub
2. Añadir servicio PostgreSQL desde el dashboard
3. Variables de entorno:
   - `DATABASE_URL` (auto-generada por Railway)
   - `SECRET_KEY` (generada manualmente)
   - `ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=10080`

4. Build y Deploy automático desde `main`

### Render

1. Tipo: **Web Service**
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Añadir PostgreSQL desde Add-ons
5. Configurar Environment Variables (igual que Railway)
6. Después del primer deploy, ejecutar seed:
   ```bash
   render shell
   python -m app.seed.seed_data
   ```

## 🔒 Seguridad

- ✅ Passwords hasheados con bcrypt
- ✅ JWT tokens con expiración configurable
- ✅ CORS configurado (ver `main.py`)
- ✅ Validación de input con Pydantic
- ✅ SQL Injection protegido (SQLAlchemy ORM)
- ⚠️ Cambiar `SECRET_KEY` en producción
- ⚠️ Usar HTTPS en producción
- ⚠️ Rate limiting recomendado (TODO)

## 📝 Migraciones

### Crear nueva migración

```bash
# Auto-generar desde cambios en modelos
alembic revision --autogenerate -m "Descripción del cambio"

# Crear migración vacía
alembic revision -m "Descripción"
```

### Aplicar migraciones

```bash
# Upgrade a última versión
alembic upgrade head

# Downgrade una versión
alembic downgrade -1

# Ver historial
alembic history
```

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solución:**
- Verificar que PostgreSQL esté corriendo: `docker ps` o `systemctl status postgresql`
- Verificar `DATABASE_URL` en `.env`
- Probar conexión: `psql -h localhost -U trainer -d training_tracker`

### Alembic no detecta cambios

```bash
# Limpiar cache Python
find . -type d -name __pycache__ -exec rm -r {} +

# Regenerar migración
alembic revision --autogenerate -m "cambios"
```

### ImportError al ejecutar seed

```
ModuleNotFoundError: No module named 'app'
```

**Solución:**
```bash
# Ejecutar desde directorio backend/, no desde backend/app/
cd backend
python -m app.seed.seed_data
```

## 📄 Licencia

Proyecto personal de uso privado.

## 👤 Autor

Backend desarrollado para Training Tracker — Plan de Fuerza Personal.

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 2026
