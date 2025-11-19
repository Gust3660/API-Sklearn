# Carpeta de Notebooks Jupyter

Aquí es donde debes colocar tus notebooks:

## Archivos a agregar:

1. **07_division-del-dataset.ipynb**
   - Lógica de división del dataset
   - Reemplaza la función `DatasetDivider.divide_dataset()` en `api/processors.py`

2. **08_Preparacio-del-dataset.ipynb**
   - Preparación y normalización de datos
   - Reemplaza la función `DataPreparator.prepare_data()` en `api/processors.py`

3. **09_Creacion_de_tranformadores-y_pipelines-personalizados.ipynb**
   - Transformadores y pipelines personalizados
   - Reemplaza la función `TransformerPipeline.apply_transformations()` en `api/processors.py`

## Ubicación exacta:

\`\`\`
proyecto/
├── notebooks/           <-- AQUÍ VAN TUS IPYNB
│   ├── 07_division-del-dataset.ipynb
│   ├── 08_Preparacio-del-dataset.ipynb
│   └── 09_Creacion_de_tranformadores-y_pipelines-personalizados.ipynb
├── api/
├── config/
├── static/
└── templates/
\`\`\`

## Cómo acceder a los notebooks desde la API:

- **Listar todos:** `GET http://localhost:8000/api/notebooks/list/`
- **Ver notebook:** `GET http://localhost:8000/api/notebooks/07_division-del-dataset.ipynb/`
- **Ver como HTML:** `GET http://localhost:8000/api/notebooks/07_division-del-dataset.ipynb/html/`
- **Descargar:** `GET http://localhost:8000/api/notebooks/07_division-del-dataset.ipynb/download/`

## Pasos para usar:

1. Copia los 3 notebooks a esta carpeta (`notebooks/`)
2. La API detectará automáticamente
3. Accede a `http://localhost:8000/` para ver la interfaz
4. Extrae el código Python de tus notebooks y adapta las funciones en `api/processors.py`
\`\`\`

```python file="" isHidden
