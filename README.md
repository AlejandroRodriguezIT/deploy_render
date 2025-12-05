# Dashboard Rankings TruMedia

Dashboard interactivo para visualizar rankings de equipos de Segunda División basado en métricas de TruMedia.

## Características

- **Diagramas de Estilo**: Métricas de estilo de juego (posesión, elaboración, presión, etc.)
- **Diagramas de Rendimiento**: Métricas de rendimiento (xG, goles, eficacia, etc.)
- **Evolución por partido**: Gráfico de barras con la evolución de cada métrica

## Despliegue en Render

### Opción 1: Despliegue automático con render.yaml

1. Sube este directorio a un repositorio de GitHub
2. Ve a [Render Dashboard](https://dashboard.render.com/)
3. Crea un nuevo "Web Service"
4. Conecta tu repositorio de GitHub
5. Render detectará automáticamente el archivo `render.yaml`

### Opción 2: Despliegue manual

1. Crea un nuevo "Web Service" en Render
2. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT`
3. Añade las variables de entorno:
   - `DB_USER`: Usuario de la base de datos
   - `DB_PASSWORD`: Contraseña de la base de datos
   - `DB_HOST`: Host de la base de datos
   - `DB_NAME`: Nombre de la base de datos

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `DB_USER` | Usuario MySQL |
| `DB_PASSWORD` | Contraseña MySQL |
| `DB_HOST` | Host del servidor MySQL |
| `DB_NAME` | Nombre de la base de datos |

## Ejecución Local

```bash
pip install -r requirements.txt
python app.py
```

Abre tu navegador en: http://127.0.0.1:8050

## Tecnologías

- **Dash/Plotly**: Framework de visualización
- **Pandas**: Procesamiento de datos
- **SQLAlchemy**: Conexión a base de datos
- **Gunicorn**: Servidor WSGI para producción

---
© 2025 RC Deportivo de La Coruña - Departamento de Análisis
