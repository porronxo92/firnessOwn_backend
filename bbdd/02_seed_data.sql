-- =====================================================
-- FitnessOwn - Datos de Semilla (Seed Data)
-- =====================================================
-- Ejecutar después de 01_create_tables.sql

-- =====================================================
-- 1. FASES DEL PLAN DE ENTRENAMIENTO
-- =====================================================
INSERT INTO phases (num, name, weeks_start, weeks_end, focus, description, series_per_muscle, rep_range, rir_target, rest_seconds_min, rest_seconds_max) VALUES
(1, 'Adaptación', 1, 4, 'Base técnica', 'Fase de adaptación anatómica y aprendizaje de patrones de movimiento. Énfasis en técnica y conexión mente-músculo.', '10-12', '10-15', '3-4', 90, 120),
(2, 'Acumulación', 5, 8, 'Volumen', 'Fase de acumulación de volumen. Incremento progresivo de la carga manteniendo técnica. Mayor número de series efectivas.', '14-18', '8-12', '2-3', 90, 150),
(3, 'Intensificación', 9, 12, 'Intensidad', 'Fase de intensificación. Cargas más pesadas, menor volumen, máxima intensidad. Preparación para PRs.', '12-14', '5-8', '1-2', 120, 180),
(4, 'Resolución', 13, 16, 'Superseries', 'Fase de resolución con superseries y circuitos. Alta densidad, trabajo metabólico, definición y resistencia muscular.', '10-12', '10-15', '2-3', 60, 90)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 2. EJERCICIOS - FASE 1 (Adaptación)
-- =====================================================

-- PULL (Tracción) - Fase 1
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(1, 'pull', 'Dominadas con lastre', 'back', 'Dorsal ancho, romboides, trapecio medio, bíceps', 4, '8', '3-4', 'Rango completo, sin kipping. Escápulas retraídas al inicio.', 1),
(1, 'pull', 'Remo Landmine', 'back', 'Dorsal ancho, romboides, trapecio, erector espinal', 4, '12', '3-4', 'Unilateral, codo pegado al cuerpo. Pausa arriba 1s.', 2),
(1, 'pull', 'Face pull con cuerda', 'shoulders', 'Deltoides posterior, trapecio superior, rotadores externos', 3, '15', '4', 'Rotación externa al final del movimiento. Codos altos.', 3),
(1, 'pull', 'Curl bíceps barra EZ', 'arms', 'Bíceps braquial, braquial anterior', 3, '12', '3', 'Sin swinging. Controlar la fase excéntrica 2-3s.', 4),
(1, 'pull', 'Curl martillo mancuernas', 'arms', 'Braquiorradial, bíceps braquial', 3, '12', '3', 'Codos fijos al costado. Movimiento controlado.', 5)
ON CONFLICT DO NOTHING;

-- PUSH (Empuje) - Fase 1
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(1, 'push', 'Press Banca Recto', 'chest', 'Pectoral mayor, deltoides anterior, tríceps', 4, '12', '3-4', 'Técnica base. Escápulas retraídas, arco lumbar natural.', 1),
(1, 'push', 'Press Banca Inclinado', 'chest', 'Pectoral mayor (porción clavicular), deltoides anterior', 4, '12', '3-4', 'Inclinación 30-45°. Codos a 45° del torso.', 2),
(1, 'push', 'Press Militar Mancuernas', 'shoulders', 'Deltoides anterior y lateral, tríceps, trapecio superior', 3, '12', '3', 'Sentado con respaldo. No hiperextender lumbar.', 3),
(1, 'push', 'Elevaciones Laterales', 'shoulders', 'Deltoides lateral', 4, '15', '3', 'Sin impulso. Ligera flexión de codos, meñique ligeramente arriba.', 4),
(1, 'push', 'Fondos en paralelas', 'chest', 'Pectoral mayor inferior, tríceps, deltoides anterior', 3, '12', '3', 'Torso ligeramente inclinado hacia adelante para énfasis pectoral.', 5),
(1, 'push', 'Extensión tríceps cuerda', 'arms', 'Tríceps (cabeza larga, lateral y medial)', 3, '15', '3', 'Separar la cuerda al final. Codos fijos.', 6)
ON CONFLICT DO NOTHING;

-- LEGS (Pierna) - Fase 1
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(1, 'legs', 'Sentadilla Trasera', 'legs', 'Cuádriceps, glúteos, isquiotibiales, core', 4, '10', '3-4', 'Profundidad completa. Rodillas en línea con pies.', 1),
(1, 'legs', 'Peso Muerto Rumano', 'back', 'Isquiotibiales, glúteos, erector espinal', 4, '10', '3-4', 'Hip hinge puro. Barra pegada a las piernas.', 2),
(1, 'legs', 'Hip Thrust con barra', 'glutes', 'Glúteo mayor, isquiotibiales', 4, '12', '3', 'Isométrico 1s arriba. Chin tucked, mirada al frente.', 3),
(1, 'legs', 'Zancada Búlgara', 'legs', 'Cuádriceps, glúteos, isquiotibiales', 3, '12', '3', 'Pie trasero elevado en banco. Torso ligeramente inclinado.', 4),
(1, 'legs', 'Abductores máquina', 'glutes', 'Glúteo medio, tensor de la fascia lata', 3, '15', '3', 'Énfasis en glúteo medio. Pausa en posición abierta.', 5),
(1, 'legs', 'Curl femoral tumbado', 'legs', 'Isquiotibiales', 3, '12', '3', 'Cadera pegada al banco. Flexión completa.', 6)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 3. EJERCICIOS - FASE 2 (Acumulación)
-- =====================================================

-- PULL - Fase 2
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(2, 'pull', 'Remo Landmine pesado', 'back', 'Dorsal ancho, romboides, trapecio', 5, '8', '2-3', 'Carga ↑, técnica intacta. Rest-pause si es necesario.', 1),
(2, 'pull', 'Dominadas con lastre', 'back', 'Dorsal ancho, bíceps, romboides', 4, '6-8', '2', 'Progresión en lastre. Full ROM.', 2),
(2, 'pull', 'Pull-over mancuerna', 'back', 'Dorsal ancho, serrato anterior, pectoral', 3, '12', '3', 'Banco plano, brazos ligeramente flexionados.', 3),
(2, 'pull', 'Face pull + encogimiento', 'shoulders', 'Deltoides posterior, trapecio superior', 3, '15', '3', 'Combinar tracción con encogimiento al final.', 4),
(2, 'pull', 'Curl bíceps concentrado', 'arms', 'Bíceps braquial', 4, '12', '2', 'Máxima contracción. Supinación al subir.', 5)
ON CONFLICT DO NOTHING;

-- PUSH - Fase 2
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(2, 'push', 'Press Banca Recto', 'chest', 'Pectoral mayor, deltoides anterior, tríceps', 5, '8', '2-3', 'Rampa de activación. Aumentar carga progresivamente.', 1),
(2, 'push', 'Press Inclinado Mancuernas', 'chest', 'Pectoral mayor clavicular, deltoides', 4, '10', '2', 'Rango completo. Juntar mancuernas arriba.', 2),
(2, 'push', 'Press Militar Barra', 'shoulders', 'Deltoides, tríceps, trapecio superior', 4, '8', '2', 'De pie preferentemente. Core activado.', 3),
(2, 'push', 'Elevaciones laterales cable', 'shoulders', 'Deltoides lateral', 4, '15', '2', 'Tensión constante. Polea a la cadera.', 4),
(2, 'push', 'Fondos lastrados', 'chest', 'Pectoral inferior, tríceps', 3, '10', '2', 'Añadir lastre progresivamente.', 5),
(2, 'push', 'Press francés + extensión', 'arms', 'Tríceps (énfasis cabeza larga)', 3, '12', '2', 'Combinar press francés con extensión overhead.', 6)
ON CONFLICT DO NOTHING;

-- LEGS - Fase 2
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(2, 'legs', 'Sentadilla trasera', 'legs', 'Cuádriceps, glúteos, core', 5, '8', '2-3', '+5-10kg vs Fase 1. Mantener técnica.', 1),
(2, 'legs', 'Peso Muerto Convencional', 'back', 'Posterior chain completa', 4, '6-8', '2-3', 'Alterna con rumano cada semana.', 2),
(2, 'legs', 'Hip Thrust pesado', 'glutes', 'Glúteo mayor', 5, '10', '2', 'Incrementar carga. Pausa arriba.', 3),
(2, 'legs', 'Zancada Búlgara mancuernas', 'legs', 'Cuádriceps, glúteos', 3, '10', '2', 'Añadir carga con mancuernas.', 4),
(2, 'legs', 'Abductores + aductores SS', 'glutes', 'Glúteo medio, aductores', 3, '15', '2', 'Superserie sin descanso entre ambos.', 5),
(2, 'legs', 'Curl femoral + extensión', 'legs', 'Isquiotibiales, cuádriceps', 3, '12', '2', 'Agonista-antagonista.', 6)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 4. EJERCICIOS - FASE 3 (Intensificación)
-- =====================================================

-- PULL - Fase 3
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(3, 'pull', 'Dominadas con lastre', 'back', 'Dorsal ancho, bíceps', 5, '5-6', '1-2', 'Top set pesado. Buscar PR.', 1),
(3, 'pull', 'Remo Landmine máximo', 'back', 'Dorsal completo', 4, '6', '1', 'Rest-pause opcional en última serie.', 2),
(3, 'pull', 'Face pull eccéntrico', 'shoulders', 'Deltoides posterior, rotadores', 3, '12', '2', '3s excéntrico controlado.', 3),
(3, 'pull', 'Curl bíceps drop set', 'arms', 'Bíceps braquial', 3, '10+6', '1', 'Drop 25% inmediatamente después.', 4)
ON CONFLICT DO NOTHING;

-- PUSH - Fase 3
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(3, 'push', 'Press Banca - Top set', 'chest', 'Pectoral mayor, tríceps', 5, '5-6', '1', 'Back-off sets al 80% después.', 1),
(3, 'push', 'Press Inclinado pesado', 'chest', 'Pectoral clavicular', 4, '8', '1-2', 'Máxima carga controlable.', 2),
(3, 'push', 'Press Militar pesado', 'shoulders', 'Deltoides, tríceps', 4, '6-8', '1-2', 'Buscar PR en press militar.', 3),
(3, 'push', 'Laterales drop set', 'shoulders', 'Deltoides lateral', 3, '15+8', '1', 'Drop set para bombeo máximo.', 4),
(3, 'push', 'Fondos lastrados máx.', 'chest', 'Pectoral inferior, tríceps', 3, '8', '1', 'Máximo lastre posible.', 5)
ON CONFLICT DO NOTHING;

-- LEGS - Fase 3
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(3, 'legs', 'Sentadilla - Top set', 'legs', 'Cuádriceps, glúteos', 5, '5', '1', 'Back-off x3 al 80%.', 1),
(3, 'legs', 'Peso Muerto máximo', 'back', 'Posterior chain', 4, '5-6', '1', 'Buscar PR semanal.', 2),
(3, 'legs', 'Hip Thrust máximo', 'glutes', 'Glúteo mayor', 5, '8', '1', 'Eccéntrico 3s. Máxima carga.', 3),
(3, 'legs', 'Zancada Búlgara pesada', 'legs', 'Cuádriceps, glúteos', 3, '8', '1-2', 'Mancuernas pesadas.', 4)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 5. EJERCICIOS - FASE 4 (Resolución - Superseries)
-- =====================================================

-- PULL - Fase 4
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(4, 'pull', 'SS: Dominadas + Curl bíceps', 'back', 'Dorsal, bíceps', 4, '8+12', '2', 'Superserie A. 60s descanso entre rondas.', 1),
(4, 'pull', 'SS: Remo + Face pull', 'back', 'Dorsal, deltoides posterior', 4, '10+15', '2', 'Superserie B. Alta densidad.', 2),
(4, 'pull', 'SS: Polea alta + curl martillo', 'back', 'Dorsal, braquiorradial', 3, '12+12', '2', 'Superserie C. Finisher.', 3)
ON CONFLICT DO NOTHING;

-- PUSH - Fase 4
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(4, 'push', 'SS: Press banca + Laterales', 'chest', 'Pectoral, deltoides lateral', 4, '10+15', '2', 'Superserie A. 60s descanso.', 1),
(4, 'push', 'SS: Inclinado + Press militar', 'chest', 'Pectoral clavicular, deltoides', 4, '10+10', '2', 'Superserie B. Compound movement.', 2),
(4, 'push', 'SS: Fondos + Tríceps polea', 'chest', 'Pectoral inferior, tríceps', 3, '10+15', '2', 'Superserie C. Finisher.', 3)
ON CONFLICT DO NOTHING;

-- LEGS - Fase 4
INSERT INTO exercises (phase_id, session_type, name, muscle_group, muscle_desc, default_sets, default_reps, rir, notes, sort_order) VALUES
(4, 'legs', 'SS: Sentadilla + Hip thrust', 'legs', 'Cuádriceps, glúteos', 4, '10+12', '2', 'Superserie A. 60s descanso.', 1),
(4, 'legs', 'SS: Peso muerto + Abductores', 'back', 'Isquiotibiales, glúteo medio', 4, '10+15', '2', 'Superserie B.', 2),
(4, 'legs', 'SS: Zancada + Curl femoral', 'legs', 'Cuádriceps, isquiotibiales', 3, '10+12', '2', 'Superserie C. Finisher.', 3)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 6. USUARIO DE PRUEBA (password: test123)
-- =====================================================
-- Nota: El hash es para 'test123' con bcrypt
INSERT INTO users (username, email, password_hash, onboarding_completed) VALUES
('demo_user', 'demo@fitnessown.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.AjXMnL.0Xm.Kye', false),
('test_user', 'test@fitnessown.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.AjXMnL.0Xm.Kye', true)
ON CONFLICT (username) DO NOTHING;

-- =====================================================
-- 7. PERFIL DE USUARIO DE PRUEBA
-- =====================================================
INSERT INTO user_profiles (
    user_id, age, gender, height_cm, weight_kg, body_fat_percentage,
    primary_goal, secondary_goals, target_weight_kg,
    training_days_per_week, preferred_days, session_duration_minutes,
    training_period, has_gym_access, has_home_equipment, home_equipment_list,
    has_bike, bike_type, has_running_gear, outdoor_space_available,
    fitness_level, years_training, diet_type, meals_per_day,
    preferred_training_types, onboarding_completed
) 
SELECT 
    u.id, 30, 'male', 178, 75.5, 18.0,
    'hypertrophy', '["strength", "endurance"]'::jsonb, 80.0,
    4, '["monday", "wednesday", "friday", "saturday"]'::jsonb, 60,
    'medium', true, true, '["Mancuernas", "Barra olímpica", "Banco ajustable"]'::jsonb,
    true, 'gravel', true, true,
    'intermediate', 3.0, 'omnivore', 4,
    '["Fuerza/Pesas", "Running", "Ciclismo"]'::jsonb, true
FROM users u WHERE u.username = 'test_user'
ON CONFLICT (user_id) DO NOTHING;

-- =====================================================
-- 8. LOGS DE ENTRENAMIENTO DE MUESTRA
-- =====================================================
INSERT INTO workout_logs (user_id, exercise_id, log_date, weight_kg, sets_done, reps_done, rir_actual, notes)
SELECT 
    u.id, e.id, CURRENT_DATE - interval '7 days', 60.0, 4, '10,10,9,8', '3', 'Primera sesión del plan'
FROM users u, exercises e 
WHERE u.username = 'test_user' AND e.name = 'Press Banca Recto' AND e.phase_id = 1
LIMIT 1;

INSERT INTO workout_logs (user_id, exercise_id, log_date, weight_kg, sets_done, reps_done, rir_actual, notes)
SELECT 
    u.id, e.id, CURRENT_DATE - interval '5 days', 62.5, 4, '10,10,10,9', '2-3', 'Subida de peso'
FROM users u, exercises e 
WHERE u.username = 'test_user' AND e.name = 'Press Banca Recto' AND e.phase_id = 1
LIMIT 1;

INSERT INTO workout_logs (user_id, exercise_id, log_date, weight_kg, sets_done, reps_done, rir_actual, notes)
SELECT 
    u.id, e.id, CURRENT_DATE - interval '7 days', 80.0, 4, '8,8,7,7', '3', 'Buenas sensaciones'
FROM users u, exercises e 
WHERE u.username = 'test_user' AND e.name = 'Sentadilla Trasera' AND e.phase_id = 1
LIMIT 1;

INSERT INTO workout_logs (user_id, exercise_id, log_date, weight_kg, sets_done, reps_done, rir_actual, notes)
SELECT 
    u.id, e.id, CURRENT_DATE - interval '7 days', 10.0, 4, '8,7,6,6', '3', 'Con lastre de 10kg'
FROM users u, exercises e 
WHERE u.username = 'test_user' AND e.name = 'Dominadas con lastre' AND e.phase_id = 1
LIMIT 1;

-- =====================================================
-- 9. LOGS DE CARDIO DE MUESTRA
-- =====================================================
INSERT INTO cardio_logs (user_id, log_date, type, duration_min, distance_km, zone, elevation_m, notes)
SELECT 
    u.id, CURRENT_DATE - interval '4 days', 'bici', 90, 35.5, 'Z2', 450, 'Ruta de montaña, buen ritmo'
FROM users u WHERE u.username = 'test_user';

INSERT INTO cardio_logs (user_id, log_date, type, duration_min, distance_km, zone, notes)
SELECT 
    u.id, CURRENT_DATE - interval '1 day', 'trail', 60, 10.2, 'Z2-Z3', 'Trail suave, recuperación activa'
FROM users u WHERE u.username = 'test_user';

-- =====================================================
-- Confirmación
-- =====================================================
SELECT 'Datos de semilla insertados correctamente' AS status;
SELECT 
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM phases) as phases_count,
    (SELECT COUNT(*) FROM exercises) as exercises_count,
    (SELECT COUNT(*) FROM user_profiles) as profiles_count,
    (SELECT COUNT(*) FROM workout_logs) as workout_logs_count,
    (SELECT COUNT(*) FROM cardio_logs) as cardio_logs_count;
