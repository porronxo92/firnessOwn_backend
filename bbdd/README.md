# 📁 FitnessOwn - Scripts de Base de Datos

Este directorio contiene los scripts para gestionar la base de datos de FitnessOwn.

## 📋 Archivos

| Archivo | Descripción |
|---------|-------------|
| `01_create_tables.sql` | Script SQL para crear todas las tablas |
| `02_seed_data.sql` | Script SQL con datos de semilla (fases, ejercicios, usuarios) |
| `init_db.py` | Script Python para gestionar tablas vía SQLAlchemy |
| `seed_mock_data.py` | Script Python para insertar datos de prueba |

## 🚀 Uso Rápido

### Opción 1: Usando Python (Recomendado)

```bash
# Desde el directorio backend/
cd backend

# 1. Crear las tablas
python -m bbdd.init_db create

# 2. Insertar datos de prueba
python -m bbdd.seed_mock_data all
```

### Opción 2: Usando SQL directo

Si prefieres ejecutar SQL directamente en Supabase/PostgreSQL:

1. Ve al **SQL Editor** de Supabase
2. Copia y pega el contenido de `01_create_tables.sql`
3. Ejecuta el script
4. Luego copia y pega `02_seed_data.sql`
5. Ejecuta el script

## 🛠️ Comandos Disponibles

### init_db.py

```bash
# Verificar conexión
python -m bbdd.init_db check

# Crear tablas
python -m bbdd.init_db create

# Eliminar tablas (¡CUIDADO!)
python -m bbdd.init_db drop

# Resetear (drop + create)
python -m bbdd.init_db reset
```

### seed_mock_data.py

```bash
# Ejecutar todo
python -m bbdd.seed_mock_data all

# Ejecutar solo partes específicas
python -m bbdd.seed_mock_data phases     # Solo fases
python -m bbdd.seed_mock_data exercises  # Solo ejercicios
python -m bbdd.seed_mock_data users      # Solo usuarios
python -m bbdd.seed_mock_data profile    # Solo perfil
python -m bbdd.seed_mock_data workouts   # Solo logs de fuerza
python -m bbdd.seed_mock_data cardio     # Solo logs de cardio
```

## 👤 Usuarios de Prueba

| Usuario | Password | Estado |
|---------|----------|--------|
| `demo_user` | `demo123` | Sin onboarding (nuevo) |
| `test_user` | `test123` | Con onboarding completo |

## 📊 Estructura de Datos

### Fases del Plan (4)
- Adaptación (semanas 1-4)
- Acumulación (semanas 5-8)
- Intensificación (semanas 9-12)
- Resolución (semanas 13-16)

### Ejercicios (~50)
Distribuidos por fase y tipo de sesión:
- Pull (Tracción): 4-5 ejercicios por fase
- Push (Empuje): 5-6 ejercicios por fase
- Legs (Pierna): 4-6 ejercicios por fase

### Logs de Ejemplo
- ~10 workout logs para test_user
- ~4 cardio logs para test_user

## ⚙️ Variables de Entorno

Asegúrate de tener configurado el archivo `.env`:

```env
DATABASE_URL=postgresql://postgres:${PASSWORD_BBDD}@db.vjlxxjulhzvshcegctgo.supabase.co:5432/postgres
PASSWORD_BBDD=tu_password_de_supabase
```

## 🔧 Troubleshooting

### Error de conexión
- Verifica que `PASSWORD_BBDD` esté configurado
- Comprueba que la URL de Supabase sea correcta

### Error "tabla ya existe"
- Usa `init_db.py reset` para recrear las tablas
- O ejecuta `DROP TABLE IF EXISTS ...` antes del create

### Error de imports
Asegúrate de ejecutar desde el directorio `backend/`:
```bash
cd backend
python -m bbdd.init_db
```
