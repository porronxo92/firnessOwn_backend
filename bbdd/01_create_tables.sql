-- =====================================================
-- FitnessOwn - Script de Creación de Base de Datos
-- =====================================================
-- Ejecutar en orden sobre una base de datos PostgreSQL limpia

-- Extensión para UUIDs (opcional, por si se necesita en el futuro)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. TABLA: users (Usuarios)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- 2. TABLA: phases (Fases del plan de entrenamiento)
-- =====================================================
CREATE TABLE IF NOT EXISTS phases (
    id SERIAL PRIMARY KEY,
    num SMALLINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    weeks_start SMALLINT NOT NULL,
    weeks_end SMALLINT NOT NULL,
    focus TEXT,
    description TEXT,
    series_per_muscle VARCHAR(20),
    rep_range VARCHAR(20),
    rir_target VARCHAR(10),
    rest_seconds_min SMALLINT,
    rest_seconds_max SMALLINT
);

-- =====================================================
-- 3. TABLA: exercises (Ejercicios base del plan)
-- =====================================================
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    phase_id INTEGER REFERENCES phases(id) ON DELETE SET NULL,
    session_type VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    muscle_group VARCHAR(50),
    muscle_desc TEXT,
    default_sets SMALLINT,
    default_reps VARCHAR(20),
    rir VARCHAR(10),
    notes TEXT,
    sort_order SMALLINT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_exercises_phase ON exercises(phase_id);
CREATE INDEX IF NOT EXISTS idx_exercises_session ON exercises(session_type);

-- =====================================================
-- 4. TABLA: custom_exercises (Ejercicios personalizados)
-- =====================================================
CREATE TABLE IF NOT EXISTS custom_exercises (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    phase_id INTEGER REFERENCES phases(id) ON DELETE SET NULL,
    session_type VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    muscle_group VARCHAR(50),
    default_sets SMALLINT,
    default_reps VARCHAR(20),
    rir VARCHAR(10),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_custom_exercises_user ON custom_exercises(user_id);

-- =====================================================
-- 5. TABLA: workout_logs (Registro de entrenamientos)
-- =====================================================
CREATE TABLE IF NOT EXISTS workout_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    custom_exercise_id INTEGER REFERENCES custom_exercises(id) ON DELETE SET NULL,
    log_date DATE NOT NULL,
    weight_kg NUMERIC(6,2),
    sets_done SMALLINT,
    reps_done VARCHAR(20),
    rir_actual VARCHAR(10),
    rpe NUMERIC(3,1),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_exercise CHECK (
        (exercise_id IS NOT NULL AND custom_exercise_id IS NULL) OR
        (exercise_id IS NULL AND custom_exercise_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON workout_logs(user_id, log_date DESC);
CREATE INDEX IF NOT EXISTS idx_workout_logs_exercise ON workout_logs(exercise_id, user_id);

-- =====================================================
-- 6. TABLA: cardio_logs (Registro de cardio)
-- =====================================================
CREATE TABLE IF NOT EXISTS cardio_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    type VARCHAR(20) NOT NULL,
    duration_min SMALLINT,
    distance_km NUMERIC(6,2),
    zone VARCHAR(10),
    elevation_m SMALLINT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cardio_logs_user_date ON cardio_logs(user_id, log_date DESC);

-- =====================================================
-- 7. TABLA: user_profiles (Perfil completo del usuario)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Datos físicos
    age INTEGER,
    gender VARCHAR(20),
    height_cm FLOAT,
    weight_kg FLOAT,
    body_fat_percentage FLOAT,
    
    -- Objetivos
    primary_goal VARCHAR(50),
    secondary_goals JSONB,
    target_weight_kg FLOAT,
    
    -- Disponibilidad
    training_days_per_week INTEGER,
    preferred_days JSONB,
    session_duration_minutes INTEGER,
    
    -- Periodo de entrenamiento
    training_period VARCHAR(20),
    start_date TIMESTAMP WITH TIME ZONE,
    target_event_date TIMESTAMP WITH TIME ZONE,
    target_event_name VARCHAR(200),
    
    -- Recursos disponibles
    has_gym_access BOOLEAN DEFAULT FALSE,
    has_home_equipment BOOLEAN DEFAULT FALSE,
    home_equipment_list JSONB,
    has_bike BOOLEAN DEFAULT FALSE,
    bike_type VARCHAR(50),
    has_running_gear BOOLEAN DEFAULT TRUE,
    outdoor_space_available BOOLEAN DEFAULT FALSE,
    pool_access BOOLEAN DEFAULT FALSE,
    
    -- Experiencia y nivel
    fitness_level VARCHAR(20),
    years_training FLOAT,
    previous_injuries TEXT,
    health_conditions TEXT,
    
    -- Alimentación
    diet_type VARCHAR(50),
    meals_per_day INTEGER,
    tracks_calories BOOLEAN DEFAULT FALSE,
    daily_calorie_target INTEGER,
    protein_target_grams INTEGER,
    
    -- Preferencias de entrenamiento
    preferred_training_types JSONB,
    disliked_exercises JSONB,
    favorite_exercises JSONB,
    
    -- Metadata
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id);

-- =====================================================
-- 8. TABLA: generated_plans (Planes generados por IA)
-- =====================================================
CREATE TABLE IF NOT EXISTS generated_plans (
    id SERIAL PRIMARY KEY,
    user_profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Metadata del plan
    name VARCHAR(200) NOT NULL,
    description TEXT,
    total_weeks INTEGER NOT NULL,
    current_week INTEGER DEFAULT 1,
    
    -- Tipo y enfoque
    plan_type VARCHAR(50) NOT NULL,
    primary_focus VARCHAR(100),
    
    -- Contenido del plan (estructura completa generada por Gemini)
    plan_structure JSONB NOT NULL,
    
    -- Estado del plan
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Información de generación
    gemini_prompt_used TEXT,
    gemini_model_version VARCHAR(50),
    generation_tokens INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_generated_plans_profile ON generated_plans(user_profile_id);
CREATE INDEX IF NOT EXISTS idx_generated_plans_active ON generated_plans(is_active) WHERE is_active = TRUE;

-- =====================================================
-- 9. TABLA: weekly_progress (Progreso semanal del plan)
-- =====================================================
CREATE TABLE IF NOT EXISTS weekly_progress (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES generated_plans(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    
    -- Sesiones completadas
    sessions_planned INTEGER DEFAULT 0,
    sessions_completed INTEGER DEFAULT 0,
    
    -- Notas y feedback
    user_notes TEXT,
    energy_level INTEGER,
    soreness_level INTEGER,
    motivation_level INTEGER,
    
    -- Ajustes sugeridos por Gemini
    ai_feedback TEXT,
    suggested_adjustments JSONB,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weekly_progress_plan ON weekly_progress(plan_id);
CREATE INDEX IF NOT EXISTS idx_weekly_progress_week ON weekly_progress(plan_id, week_number);

-- =====================================================
-- Confirmación
-- =====================================================
SELECT 'Todas las tablas creadas correctamente' AS status;
