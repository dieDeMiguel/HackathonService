# 🔄 Proceso de Sincronización: Archivos Locales → Railway → Qdrant Cloud

Este documento explica el flujo completo para sincronizar cambios en los archivos de datos locales con el sistema RAG desplegado en Railway y Qdrant Cloud.

## 📋 Resumen del Flujo

```
Archivos Locales (.md) → Git Push → Railway Deploy → RAG API → Qdrant Cloud
```

## 🗂️ Archivos Involucrados

### **Archivos de Datos Locales:**
- `src/ragger/system_prompt_data.md` - Base de conocimiento principal
- `src/ragger/test_data.md` - Datos de prueba y tickets
- `system-prompt.ts` - Prompt del sistema (Next.js)

### **Archivos de Configuración:**
- `src/ragger/api.py` - API FastAPI con endpoints
- `src/ragger/embed.py` - Lógica de embeddings
- `Dockerfile` - Configuración de contenedor
- `pyproject.toml` - Dependencias Python

## 🚀 Proceso de Sincronización Paso a Paso

### **Paso 1: Modificar Archivos Locales**

1. **Editar archivos de datos:**
   ```bash
   # Editar el archivo principal de conocimiento
   vim src/ragger/system_prompt_data.md
   
   # O editar datos de prueba
   vim src/ragger/test_data.md
   ```

2. **Verificar cambios:**
   ```bash
   git status
   git diff src/ragger/system_prompt_data.md
   ```

### **Paso 2: Commit y Push a Git**

```bash
# Agregar archivos modificados
git add .

# Commit con mensaje descriptivo
git commit -m "Update qualification data with current qualified teams"

# Push a GitHub
git push origin master
```

### **Paso 3: Railway Auto-Deploy**

Railway detecta automáticamente el push y inicia el despliegue:

1. **Railway detecta cambios** en el repositorio conectado
2. **Construye nueva imagen Docker** usando el `Dockerfile`
3. **Despliega el nuevo contenedor** con los archivos actualizados
4. **El servicio queda disponible** en `https://hackathonservice-production.up.railway.app`

**Tiempo estimado:** 2-5 minutos

### **Paso 4: Repoblar Base de Datos RAG**

Una vez que Railway termina el despliegue, necesitas repoblar Qdrant Cloud:

```bash
# Esperar a que Railway termine el despliegue (2-5 min)
sleep 180

# Repoblar la base de datos
curl -X POST https://hackathonservice-production.up.railway.app/populate
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Successfully populated collection with 56 chunks",
  "chunks_processed": 56,
  "files_processed": ["test_data.md", "system_prompt_data.md"]
}
```

### **Paso 5: Verificar Sincronización**

```bash
# Verificar que el servicio está funcionando
curl https://hackathonservice-production.up.railway.app/health

# Probar búsqueda con nueva información
curl -X POST https://hackathonservice-production.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{"query": "nueva información agregada", "limit": 3}'
```

## 🔧 Configuración de Servicios

### **Railway Configuration**

**Variables de entorno en Railway:**
- `OPENAI_API_KEY` - Tu clave de OpenAI
- `QDRANT_URL` - URL de Qdrant Cloud
- `QDRANT_API_KEY` - API key de Qdrant Cloud

**Start Command:** Vacío (usa CMD del Dockerfile)

### **Qdrant Cloud Configuration**

**URL del cluster:** `https://d91bd0b9-c062-4a6e-b289-0362da2b6782.eu-central-1-0.aws.cloud.qdrant.io:6333`

**API Key:** Configurada en Railway como variable de entorno

## 📊 Monitoreo y Verificación

### **Endpoints de Verificación**

1. **Health Check:**
   ```bash
   curl https://hackathonservice-production.up.railway.app/health
   ```

2. **Info de Colección:**
   ```bash
   curl https://hackathonservice-production.up.railway.app/collection/info
   ```

3. **Búsqueda de Prueba:**
   ```bash
   curl -X POST https://hackathonservice-production.up.railway.app/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "limit": 3}'
   ```

### **Logs de Railway**

Para verificar el estado del despliegue:
1. Ve a [Railway Dashboard](https://railway.app)
2. Selecciona tu proyecto
3. Ve a la pestaña "Deployments"
4. Revisa los logs del último despliegue

## ⚠️ Troubleshooting

### **Problema: Railway no despliega automáticamente**

**Solución:**
```bash
# Verificar que el push fue exitoso
git log --oneline -5

# Forzar redeploy en Railway (si es necesario)
# Ve a Railway Dashboard → Deployments → Redeploy
```

### **Problema: Error en /populate**

**Posibles causas:**
1. **Railway aún desplegando:** Esperar 2-5 minutos más
2. **Variables de entorno incorrectas:** Verificar en Railway Dashboard
3. **Qdrant Cloud inaccesible:** Verificar API key y URL

**Solución:**
```bash
# Verificar health check primero
curl https://hackathonservice-production.up.railway.app/health

# Si falla, revisar variables de entorno en Railway
```

### **Problema: Búsquedas no encuentran nueva información**

**Solución:**
```bash
# Verificar que /populate fue exitoso
curl -X POST https://hackathonservice-production.up.railway.app/populate

# Probar búsqueda con términos específicos del archivo actualizado
curl -X POST https://hackathonservice-production.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{"query": "término específico agregado", "limit": 5}'
```

## 🔄 Flujo de Trabajo Recomendado

### **Para Actualizaciones Menores:**
1. Editar archivo local
2. `git add . && git commit -m "descripción" && git push`
3. Esperar 3-5 minutos
4. `curl -X POST https://hackathonservice-production.up.railway.app/populate`
5. Verificar con búsqueda de prueba

### **Para Actualizaciones Mayores:**
1. Editar archivos locales
2. Probar localmente (opcional)
3. `git add . && git commit -m "descripción detallada" && git push`
4. Monitorear Railway Dashboard
5. Esperar confirmación de despliegue exitoso
6. Repoblar base de datos
7. Ejecutar suite de pruebas de búsqueda

## 📝 Notas Importantes

- **Railway auto-deploy:** Se activa automáticamente con cada push
- **Qdrant Cloud:** Requiere repoblación manual después de cada cambio
- **Tiempo total:** 5-10 minutos para sincronización completa
- **Backup:** Qdrant Cloud mantiene versiones anteriores automáticamente
- **Rollback:** Usar `git revert` y push para deshacer cambios

## 🎯 Integración con Next.js

Una vez sincronizado, tu aplicación Next.js puede usar:

```javascript
const RAG_API_URL = 'https://hackathonservice-production.up.railway.app';

// Búsqueda RAG
const response = await fetch(`${RAG_API_URL}/search`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "user query",
    limit: 5,
    score_threshold: 0.3
  })
});
```

---

**Última actualización:** Enero 2025  
**Versión del sistema:** RAG v1.0 con Qdrant Cloud + Railway
