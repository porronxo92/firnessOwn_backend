-- ============================================================
-- Migration: Plan Tracking Tables
-- Adds structured tracking for AI-generated plan exercises
-- ============================================================

-- 1. plan_weeks — Semanas del plan (normalizadas del JSON)
CREATE TABLE IF NOT EXISTS plan_weeks (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES generated_plans(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    phase_name VARCHAR(100),
    is_deload BOOLEAN DEFAULT FALSE,
    focus TEXT,
    progression_notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_plan_weeks_plan_week UNIQUE (plan_id, week_number)
);

CREATE INDEX IF NOT EXISTS idx_plan_weeks_plan_week ON plan_weeks(plan_id, week_number);

-- 2. plan_days — Días de cada semana
CREATE TABLE IF NOT EXISTS plan_days (
    id SERIAL PRIMARY KEY,
    week_id INTEGER NOT NULL REFERENCES plan_weeks(id) ON DELETE CASCADE,
    day_number SMALLINT NOT NULL,  -- 1-7
    day_name VARCHAR(20) NOT NULL,
    type VARCHAR(30) NOT NULL,  -- strength, cardio, rest, active_recovery, hybrid
    session_name VARCHAR(200),
    duration_minutes SMALLINT,
    session_notes TEXT,
    cardio_type VARCHAR(50),
    cardio_duration_min SMALLINT,
    cardio_intensity VARCHAR(20),
    cardio_distance_km NUMERIC(6,2),
    cardio_notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, completed, skipped
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_plan_days_week_day UNIQUE (week_id, day_number)
);

CREATE INDEX IF NOT EXISTS idx_plan_days_week_day ON plan_days(week_id, day_number);

-- 3. plan_exercises — Ejercicios planificados por día
CREATE TABLE IF NOT EXISTS plan_exercises (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES plan_days(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    muscle_group VARCHAR(50),
    sets SMALLINT NOT NULL DEFAULT 3,
    reps VARCHAR(30) NOT NULL DEFAULT '10',
    rir VARCHAR(20),
    rest_seconds SMALLINT,
    tempo VARCHAR(20),
    notes TEXT,
    alternatives TEXT,  -- comma-separated
    sort_order SMALLINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plan_exercises_day ON plan_exercises(day_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_plan_exercises_name ON plan_exercises(name);

-- 4. exercise_logs — Registros reales de series ejecutadas
CREATE TABLE IF NOT EXISTS exercise_logs (
    id SERIAL PRIMARY KEY,
    plan_exercise_id INTEGER NOT NULL REFERENCES plan_exercises(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    set_number SMALLINT NOT NULL,  -- 1, 2, 3...
    weight_kg NUMERIC(6,2),
    reps_done SMALLINT,
    rir_actual VARCHAR(10),
    rpe NUMERIC(3,1),
    completed BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exercise_logs_exercise ON exercise_logs(plan_exercise_id, created_at);
CREATE INDEX IF NOT EXISTS idx_exercise_logs_user ON exercise_logs(user_id, created_at);

-- ============================================================
-- Useful views for querying progression
-- ============================================================

-- Vista: Progresión por ejercicio (peso máximo por semana)
CREATE OR REPLACE VIEW v_exercise_progression AS
SELECT 
    pe.name AS exercise_name,
    pw.plan_id,
    pw.week_number,
    pw.phase_name,
    pe.id AS plan_exercise_id,
    MAX(el.weight_kg) AS max_weight,
    AVG(el.weight_kg) AS avg_weight,
    MAX(el.reps_done) AS max_reps,
    AVG(el.reps_done) AS avg_reps,
    COUNT(el.id) AS total_sets_logged,
    MAX(el.weight_kg * (1 + el.reps_done::numeric / 30)) AS estimated_1rm
FROM plan_exercises pe
JOIN plan_days pd ON pd.id = pe.day_id
JOIN plan_weeks pw ON pw.id = pd.week_id
LEFT JOIN exercise_logs el ON el.plan_exercise_id = pe.id
GROUP BY pe.name, pw.plan_id, pw.week_number, pw.phase_name, pe.id;
