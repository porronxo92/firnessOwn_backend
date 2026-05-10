# 🚀 Quick Start — Training Tracker

Comandos rápidos para desarrollo y despliegue.

## 📦 Setup Inicial

```bash
# Clonar repositorios
git clone https://github.com/porronxo92/firnessOwn_backend.git backend
git clone https://github.com/porronxo92/firnessOwn_frontend.git frontend

# O si ya los tienes, pull latest
cd backend && git pull origin main
cd ../frontend && git pull origin main
```

## 🐳 Docker (Recomendado para Desarrollo)

```bash
# Desde la raíz del proyecto
docker-compose up --build

# Solo backend + db
docker-compose up backend db

# Solo frontend
docker-compose up frontend

# Acceder:
# Frontend: http://localhost:4200
# Backend: http://localhost:8000/docs
# PostgreSQL: localhost:5432
```

## 🔧 Backend (Sin Docker)

```bash
cd backend

# Setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configurar .env (copiar de .env.example)
cp .env.example .env
# Editar DATABASE_URL, SECRET_KEY, etc.

# Migraciones
alembic upgrade head
python -m app.seed.seed_data

# Ejecutar
uvicorn app.main:app --reload

# Acceder: http://localhost:8000/docs
```

## 🎨 Frontend (Sin Docker)

```bash
cd frontend

# Setup
npm install

# Configurar environment
# Editar src/environments/environment.ts
# Asegurar que apiUrl apunta a tu backend

# Ejecutar
ng serve

# O con más opciones
ng serve --open --port 4200

# Acceder: http://localhost:4200
```

## 🌐 Deploy Rápido

### Backend → Railway

```bash
# Opción 1: CLI
npm i -g @railway/cli
railway login
cd backend
railway init
railway up

# Opción 2: Dashboard
# https://railway.app → New Project → Deploy from GitHub
```

### Frontend → Vercel

```bash
# Opción 1: CLI
npm i -g vercel
cd frontend
vercel login
vercel --prod

# Opción 2: Dashboard
# https://vercel.com → Import Project → Select repo
```

## 🔄 Workflow Git

```bash
# Crear rama
git checkout -b feature/mi-feature

# Hacer cambios y commit
git add .
git commit -m "Add: mi feature"

# Push
git push origin feature/mi-feature

# Merge en GitHub (Pull Request)
# O desde terminal:
git checkout main
git merge feature/mi-feature
git push origin main
```

## 🧪 Testing Rápido

### Backend (API)

```bash
# Con curl
curl http://localhost:8000/api/phases

# Con httpie (más legible)
pip install httpie
http GET http://localhost:8000/api/phases

# Login
http POST http://localhost:8000/api/auth/login username=test password=test123

# O usar FastAPI Docs
# http://localhost:8000/docs (interfaz interactiva)
```

### Frontend

```bash
# Abrir app
ng serve --open

# Verificar build de producción
ng build --configuration production
npx http-server dist/frontend/browser
```

## 📊 Comandos Útiles

### Alembic (Migraciones)

```bash
# Crear migración automática
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

### Git

```bash
# Ver estado
git status

# Ver ramas
git branch -a

# Cambiar de rama
git checkout nombre-rama

# Eliminar rama local
git branch -d nombre-rama

# Ver últimos commits
git log --oneline -10

# Ver cambios sin commit
git diff
```

### Docker

```bash
# Ver contenedores corriendo
docker ps

# Ver logs de un servicio
docker-compose logs backend -f

# Reiniciar un servicio
docker-compose restart backend

# Entrar al shell de un contenedor
docker-compose exec backend bash

# Limpiar todo (⚠️ borra volúmenes)
docker-compose down -v
```

### PostgreSQL

```bash
# Conectar a DB local
psql -U trainer -d training_tracker

# Desde Docker
docker-compose exec db psql -U trainer -d training_tracker

# Comandos SQL útiles:
\dt          # Listar tablas
\d+ phases   # Describir tabla phases
SELECT * FROM phases;
\q           # Salir
```

### Angular

```bash
# Generar componente
ng generate component features/mi-componente

# Generar servicio
ng generate service core/services/mi-servicio

# Actualizar Angular
ng update @angular/cli @angular/core

# Limpiar cache
rm -rf .angular/cache
rm -rf node_modules
npm install
```

## 🐛 Troubleshooting Rápido

### Backend no inicia

```bash
# Verificar puerto
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# Verificar DB
psql -U trainer -d training_tracker -c "SELECT 1"
```

### Frontend no compila

```bash
# Limpiar cache y reinstalar
rm -rf node_modules package-lock.json .angular
npm install

# Verificar versión de Node
node --version  # Debe ser 18+

# Verificar Angular CLI
ng version
```

### Error de CORS

```bash
# Verificar origin en backend/app/main.py
# Agregar URL del frontend en allow_origins

# O usar proxy temporal en frontend:
# Crear proxy.conf.json y ejecutar:
ng serve --proxy-config proxy.conf.json
```

## 📝 Variables de Entorno

### Backend (.env)

```bash
DATABASE_URL=postgresql+asyncpg://trainer:password@localhost:5432/training_tracker
SECRET_KEY=tu_clave_super_secreta_minimo_64_caracteres_generada_aleatoriamente
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_KEY=tu_api_key_opcional
```

### Frontend (environment.ts)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

## 🎯 Primeros Pasos Después del Setup

1. **Backend:** Verificar que `/docs` funciona
2. **Frontend:** Verificar que la app carga
3. **Crear usuario:** POST `/api/auth/register`
4. **Login:** POST `/api/auth/login`
5. **Ver fases:** GET `/api/phases`
6. **Registrar log:** POST `/api/logs`

## 📚 Documentación

- **README Principal:** [README.md](./README.md)
- **Backend:** [backend/README.md](./backend/README.md)
- **Frontend:** [frontend/README.md](./frontend/README.md)
- **Despliegue:** [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Plan Técnico:** [claude.md](./claude.md)

---

**Última actualización:** Mayo 2026
