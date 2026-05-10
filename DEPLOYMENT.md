# 🚀 Guía de Despliegue — Training Tracker

Instrucciones completas para desplegar el backend y frontend en producción.

## 📋 Resumen Rápido

| Componente | Plataforma Recomendada | Alternativas |
|------------|------------------------|--------------|
| **Backend** | Railway / Render | Heroku, AWS, DigitalOcean |
| **Frontend** | Vercel | Netlify, Firebase Hosting |
| **Base de Datos** | Neon (PostgreSQL) | Render PostgreSQL, Railway DB |

---

## 🔧 Backend — Despliegue en Railway

### 1. Preparación

Asegúrate de tener tu código en GitHub:
```bash
# Ya hecho en este proyecto
git remote -v
# origin  https://github.com/porronxo92/firnessOwn_backend.git
```

### 2. Deploy en Railway

#### Opción A: Desde Dashboard (Recomendado)

1. **Crear cuenta:** https://railway.app (login con GitHub)

2. **Nuevo Proyecto:**
   - Click en "New Project"
   - Seleccionar "Deploy from GitHub repo"
   - Autorizar Railway y seleccionar `firnessOwn_backend`

3. **Configurar Variables de Entorno:**
   - En el dashboard del proyecto → "Variables"
   - Agregar:
     ```
     SECRET_KEY=<generar_clave_segura_64_caracteres>
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=10080
     GEMINI_KEY=<tu_api_key_si_la_tienes>
     ```
   - Generar SECRET_KEY:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(48))"
     ```

4. **Agregar PostgreSQL:**
   - En el proyecto → "New" → "Database" → "Add PostgreSQL"
   - Railway creará automáticamente la variable `DATABASE_URL`
   - ⚠️ **Importante:** Cambiar el formato de la URL de `postgresql://` a `postgresql+asyncpg://`
   - Editar la variable `DATABASE_URL` y reemplazar:
     ```
     # De:
     postgresql://user:pass@host:port/dbname
     # A:
     postgresql+asyncpg://user:pass@host:port/dbname
     ```

5. **Ejecutar Migraciones (Seed Data):**
   - Una vez desplegado, ir a "Deployments" → último deployment
   - Click en "View Logs"
   - Abrir terminal (ícono de terminal en la esquina)
   - Ejecutar:
     ```bash
     alembic upgrade head
     python -m app.seed.seed_data
     ```

6. **Verificar:**
   - Railway te dará una URL pública: `https://tu-proyecto.railway.app`
   - Probar: `https://tu-proyecto.railway.app/docs`
   - Deberías ver la documentación de FastAPI

#### Opción B: Desde CLI

```bash
# Instalar Railway CLI
npm i -g @railway/cli
# O en Windows con Scoop:
scoop install railway

# Login
railway login

# En el directorio backend/
cd backend
railway init
railway link  # Seleccionar tu proyecto

# Deploy
railway up

# Agregar PostgreSQL
railway add --database postgresql

# Ver variables
railway variables

# Abrir dashboard
railway open
```

### 3. Comandos Post-Deploy (Railway)

```bash
# Conectar al proyecto
railway link

# Ver logs en tiempo real
railway logs

# Ejecutar comando en producción
railway run alembic upgrade head
railway run python -m app.seed.seed_data

# Abrir shell en producción
railway shell
```

---

## 🔧 Backend — Despliegue en Render

### 1. Preparación

Igual que Railway, necesitas el código en GitHub.

### 2. Deploy en Render

1. **Crear cuenta:** https://render.com (login con GitHub)

2. **Nuevo Web Service:**
   - Dashboard → "New +" → "Web Service"
   - Conectar repositorio `firnessOwn_backend`
   - Configuración:
     ```
     Name: training-tracker-backend
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Agregar PostgreSQL:**
   - Dashboard → "New +" → "PostgreSQL"
   - Nombre: `training-tracker-db`
   - Plan: Free (limitado) o Starter ($7/mes)
   - Una vez creado, copiar la "Internal Database URL"

4. **Variables de Entorno:**
   - En el Web Service → "Environment"
   - Agregar:
     ```
     DATABASE_URL=<internal_database_url_modificada>
     SECRET_KEY=<generar_clave_segura>
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=10080
     GEMINI_KEY=<opcional>
     ```
   - ⚠️ **Cambiar DATABASE_URL:**
     - Reemplazar `postgresql://` por `postgresql+asyncpg://`

5. **Deploy Automático:**
   - Render detecta cambios en `main` y redeploy automáticamente
   - Primera vez tarda ~5-10 minutos

6. **Ejecutar Migraciones:**
   - Opción 1: Desde Shell en Render
     - Dashboard → tu servicio → "Shell"
     ```bash
     alembic upgrade head
     python -m app.seed.seed_data
     ```
   - Opción 2: Crear un script de inicio
     - Crear `backend/start.sh`:
       ```bash
       #!/bin/bash
       alembic upgrade head
       python -m app.seed.seed_data
       uvicorn app.main:app --host 0.0.0.0 --port $PORT
       ```
     - Cambiar "Start Command" a: `bash start.sh`

7. **Verificar:**
   - URL: `https://tu-servicio.onrender.com/docs`

---

## 🎨 Frontend — Despliegue en Vercel

### 1. Preparación

```bash
# Ya hecho en este proyecto
cd frontend
git remote -v
# origin  https://github.com/porronxo92/firnessOwn_frontend.git
```

### 2. Deploy en Vercel

#### Opción A: Desde Dashboard (Recomendado)

1. **Crear cuenta:** https://vercel.com (login con GitHub)

2. **Importar Proyecto:**
   - Dashboard → "Add New..." → "Project"
   - Seleccionar `firnessOwn_frontend`
   - Configuración:
     ```
     Framework Preset: Angular
     Root Directory: ./
     Build Command: npm run build:prod
     Output Directory: dist/frontend/browser
     Install Command: npm install
     ```

3. **Variables de Entorno:**
   - En "Environment Variables" agregar:
     ```
     API_URL=https://tu-backend.railway.app/api
     ```
   - O si usaste Render:
     ```
     API_URL=https://tu-backend.onrender.com/api
     ```

4. **Deploy:**
   - Click "Deploy"
   - Vercel buildea y despliega automáticamente
   - Te dará una URL: `https://tu-proyecto.vercel.app`

5. **Dominio Custom (Opcional):**
   - Settings → Domains → Add Domain
   - Seguir instrucciones para configurar DNS

#### Opción B: Desde CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy desde directorio frontend/
cd frontend
vercel

# Configurar variables (interactivo)
# Luego deploy a producción:
vercel --prod
```

### 3. Configurar Environment

Editar `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-backend.railway.app/api'  // Cambiar por tu URL de backend
};
```

**Commit y push:**
```bash
cd frontend
git add src/environments/environment.prod.ts
git commit -m "Update production API URL"
git push origin main
```

Vercel detectará el cambio y redeployará automáticamente.

---

## 🎨 Frontend — Despliegue en Netlify (Alternativa)

### 1. Preparación

Igual que Vercel, código en GitHub.

### 2. Deploy en Netlify

1. **Crear cuenta:** https://netlify.com (login con GitHub)

2. **Nuevo Site:**
   - "Add new site" → "Import an existing project"
   - Seleccionar `firnessOwn_frontend`
   - Configuración:
     ```
     Build command: npm run build:prod
     Publish directory: dist/frontend/browser
     ```

3. **Variables de Entorno:**
   - Site settings → "Environment variables"
   - Agregar:
     ```
     API_URL=https://tu-backend.railway.app/api
     ```

4. **Deploy:**
   - Netlify buildea automáticamente
   - URL: `https://tu-proyecto.netlify.app`

---

## 🗄 Base de Datos — Neon (PostgreSQL Serverless)

### Alternativa a Railway/Render DB

1. **Crear cuenta:** https://neon.tech (gratis)

2. **Crear Proyecto:**
   - New Project → Nombre: `training-tracker`
   - Region: Europe (más cercano)

3. **Obtener Connection String:**
   - Dashboard → Connection Details
   - Copiar "Connection string"
   - Ejemplo: `postgresql://user:pass@ep-xyz.eu-central-1.aws.neon.tech/training_tracker`

4. **Modificar para asyncpg:**
   ```
   # De:
   postgresql://...
   # A:
   postgresql+asyncpg://...
   ```

5. **Configurar en Backend:**
   - Railway/Render: Agregar variable `DATABASE_URL` con el string de Neon

6. **Ejecutar Migraciones:**
   ```bash
   # Localmente, conectando a Neon
   export DATABASE_URL="postgresql+asyncpg://..."
   alembic upgrade head
   python -m app.seed.seed_data
   ```

---

## ✅ Checklist Post-Deploy

### Backend
- [ ] API responde en `/docs`
- [ ] Endpoint `/api/phases` devuelve 4 fases
- [ ] Login funciona (`POST /api/auth/login`)
- [ ] Base de datos tiene seed data (fases + ejercicios)
- [ ] Variables de entorno configuradas
- [ ] CORS permite el dominio del frontend

### Frontend
- [ ] App carga en la URL de Vercel/Netlify
- [ ] Login redirige correctamente
- [ ] API_URL apunta al backend correcto
- [ ] No hay errores de CORS en consola
- [ ] Se pueden registrar logs de entrenamiento

---

## 🔄 Workflow de Desarrollo

### Backend

```bash
# Desarrollo local
cd backend
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git add .
git commit -m "Add: nueva funcionalidad"
git push origin feature/nueva-funcionalidad
# Crear Pull Request en GitHub
# Merge a main → Railway/Render redeploy automático
```

### Frontend

```bash
# Desarrollo local
cd frontend
git checkout -b feature/nueva-vista
# ... hacer cambios ...
git add .
git commit -m "Add: nueva vista"
git push origin feature/nueva-vista
# Crear Pull Request en GitHub
# Merge a main → Vercel/Netlify redeploy automático
```

---

## 🐛 Troubleshooting

### Error: "Application failed to respond"

**Backend en Railway/Render:**
- Verificar logs: `railway logs` o Render dashboard
- Asegurarse de que el puerto está configurado:
  ```python
  # app/main.py
  if __name__ == "__main__":
      import uvicorn
      port = int(os.getenv("PORT", 8000))
      uvicorn.run("app.main:app", host="0.0.0.0", port=port)
  ```

### Error: CORS en Frontend

**Solución:**
- Verificar que el backend tenga configurado el dominio del frontend en CORS:
  ```python
  # app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://tu-frontend.vercel.app"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### Error: "No such table" en producción

**Solución:**
- Ejecutar migraciones en producción:
  ```bash
  # Railway
  railway run alembic upgrade head
  railway run python -m app.seed.seed_data
  
  # Render
  # Desde el Shell en dashboard
  alembic upgrade head
  python -m app.seed.seed_data
  ```

### Error: "Invalid credentials" en login

**Solución:**
- Verificar que el usuario existe en la base de datos de producción
- Registrar un nuevo usuario desde `/docs` o crear endpoint de seed de usuario

---

## 📊 Costos Estimados

### Plan Gratuito (Hobby)

| Servicio | Plan | Límite | Costo |
|----------|------|--------|-------|
| Railway | Trial | $5 crédito/mes | Gratis → $5/mes |
| Render | Free | 750h/mes, hiberna | Gratis |
| Vercel | Hobby | 100GB bandwidth | Gratis |
| Netlify | Free | 100GB bandwidth | Gratis |
| Neon | Free | 0.5GB storage | Gratis |

### Plan Producción (Recomendado)

| Servicio | Plan | Costo/mes |
|----------|------|-----------|
| Railway | Developer | $5 + uso |
| Render | Starter | $7 (DB) + $7 (Web) = $14 |
| Vercel | Pro | $20 |
| Neon | Launch | $19 |

**Total estimado:** $15-20/mes para app personal en producción.

---

## 🔐 Seguridad en Producción

### Checklist de Seguridad

- [ ] `SECRET_KEY` única y segura (min 64 caracteres)
- [ ] No commitear archivos `.env` (ya en `.gitignore`)
- [ ] HTTPS habilitado (automático en Railway/Render/Vercel)
- [ ] CORS restringido a dominio específico
- [ ] Rate limiting habilitado (TODO)
- [ ] Contraseñas hasheadas con bcrypt
- [ ] JWT con expiración configurada
- [ ] Variables sensibles en environment variables, no hardcoded

---

## 📚 Recursos Adicionales

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Netlify Docs:** https://docs.netlify.com
- **FastAPI Deploy:** https://fastapi.tiangolo.com/deployment/
- **Angular Deploy:** https://angular.io/guide/deployment

---

**Última actualización:** Mayo 2026  
**Versión:** 1.0.0
