from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import json
import pickle
import tempfile
from pathlib import Path

from .processors import ARFFProcessor, DatasetDivider, DataPreparator, TransformerPipeline
from .serializers import DatasetUploadSerializer, DivideDatasetSerializer

# Almacenamiento temporal en memoria para la sesión actual
_session_data = {}

@api_view(['POST'])
def upload_dataset(request):
    """
    Endpoint para cargar archivo ARFF
    POST /api/upload-dataset/
    """
    if 'file' not in request.FILES:
        return Response(
            {"error": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Guardar archivo temporalmente
    temp_path = os.path.join(settings.UPLOAD_DIR, file.name)
    with open(temp_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)
    
    # Procesar ARFF
    df, meta, result = ARFFProcessor.load_arff(temp_path)
    
    if result["status"] == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar en sesión
    _session_data['dataset'] = df
    _session_data['dataset_meta'] = meta
    _session_data['dataset_path'] = temp_path
    
    return Response({
        "status": "success",
        "message": "Dataset uploaded successfully",
        "info": result,
        "preview": df.head(5).to_dict(orient='records')
    })


@api_view(['POST'])
def divide_dataset(request):
    """
    Endpoint para dividir dataset
    POST /api/divide-dataset/
    """
    if 'dataset' not in _session_data:
        return Response(
            {"error": "No dataset loaded. Use /api/upload-dataset/ first"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = DivideDatasetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    df = _session_data['dataset']
    test_size = serializer.validated_data.get('test_size', 0.2)
    random_state = serializer.validated_data.get('random_state', 42)
    
    result = DatasetDivider.divide_dataset(df, test_size=test_size, random_state=random_state)
    
    if result["status"] == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar en sesión
    _session_data['division'] = result['data']
    
    return Response({
        "status": "success",
        "division": {
            "train_size": result["train_size"],
            "test_size": result["test_size"],
            "features": result["features"],
        }
    })


@api_view(['POST'])
def prepare_data(request):
    """
    Endpoint para preparar datos
    POST /api/prepare-data/
    """
    if 'division' not in _session_data:
        return Response(
            {"error": "Dataset not divided. Use /api/divide-dataset/ first"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    division = _session_data['division']
    X_train = division['X_train']
    X_test = division['X_test']
    y_train = division['y_train']
    y_test = division['y_test']
    
    result = DataPreparator.prepare_data(X_train, X_test, y_train, y_test)
    
    if result["status"] == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar en sesión
    _session_data['preparation'] = result['data']
    
    return Response({
        "status": "success",
        "preparation": {
            "numeric_features": result["numeric_features"],
            "categorical_features": result["categorical_features"],
            "scaler_mean": result["scaler_info"]["mean"][:5],  # Primeros 5
            "scaler_scale": result["scaler_info"]["scale"][:5],
        }
    })


@api_view(['POST'])
def apply_transformers(request):
    """
    Endpoint para aplicar transformaciones
    POST /api/apply-transformers/
    """
    if 'preparation' not in _session_data:
        return Response(
            {"error": "Data not prepared. Use /api/prepare-data/ first"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    preparation = _session_data['preparation']
    division = _session_data['division']
    
    X_train_scaled = preparation['X_train_scaled']
    X_test_scaled = preparation['X_test_scaled']
    y_train = preparation['y_train']
    y_test = preparation['y_test']
    numeric_cols = preparation['numeric_cols']
    
    result = TransformerPipeline.apply_transformations(
        X_train_scaled, X_test_scaled, y_train, y_test, numeric_cols
    )
    
    if result["status"] == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar en sesión
    _session_data['transformations'] = result['data']
    
    return Response({
        "status": "success",
        "transformation": {
            "original_features": result["original_features"],
            "transformed_features": result["transformed_features"],
            "explained_variance_ratio": result["explained_variance_ratio"][:10],
            "cumulative_variance": result["cumulative_variance"][:10],
        }
    })


@api_view(['POST'])
def pipeline_full(request):
    """
    Endpoint para ejecutar el pipeline completo de una vez
    POST /api/pipeline-full/
    """
    if 'file' not in request.FILES:
        return Response(
            {"error": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    temp_path = os.path.join(settings.UPLOAD_DIR, file.name)
    
    with open(temp_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)
    
    try:
        # 1. Cargar dataset
        df, meta, upload_result = ARFFProcessor.load_arff(temp_path)
        if upload_result["status"] == "error":
            raise Exception(upload_result["message"])
        
        # 2. Dividir dataset
        division_result = DatasetDivider.divide_dataset(df)
        if division_result["status"] == "error":
            raise Exception(division_result["message"])
        
        division_data = division_result['data']
        
        # 3. Preparar datos
        prep_result = DataPreparator.prepare_data(
            division_data['X_train'],
            division_data['X_test'],
            division_data['y_train'],
            division_data['y_test']
        )
        if prep_result["status"] == "error":
            raise Exception(prep_result["message"])
        
        prep_data = prep_result['data']
        
        # 4. Aplicar transformadores
        trans_result = TransformerPipeline.apply_transformations(
            prep_data['X_train_scaled'],
            prep_data['X_test_scaled'],
            prep_data['y_train'],
            prep_data['y_test'],
            prep_data['numeric_cols']
        )
        if trans_result["status"] == "error":
            raise Exception(trans_result["message"])
        
        return Response({
            "status": "success",
            "pipeline": {
                "upload": upload_result,
                "division": {
                    "train_size": division_result["train_size"],
                    "test_size": division_result["test_size"],
                    "features": division_result["features"],
                },
                "preparation": {
                    "numeric_features": prep_result["numeric_features"],
                    "categorical_features": prep_result["categorical_features"],
                },
                "transformation": {
                    "original_features": trans_result["original_features"],
                    "transformed_features": trans_result["transformed_features"],
                }
            }
        })
    
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def list_notebooks(request):
    """
    Endpoint para listar notebooks disponibles
    GET /api/notebooks/list/
    """
    try:
        notebooks = []
        if os.path.exists(settings.NOTEBOOKS_DIR):
            for file in os.listdir(settings.NOTEBOOKS_DIR):
                if file.endswith('.ipynb'):
                    file_path = os.path.join(settings.NOTEBOOKS_DIR, file)
                    size = os.path.getsize(file_path)
                    notebooks.append({
                        "filename": file,
                        "size": size,
                        "path": f"/api/notebooks/{file}/"
                    })
        
        return Response({
            "status": "success",
            "notebooks": notebooks,
            "count": len(notebooks)
        })
    
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_notebook(request, filename):
    """
    Endpoint para descargar notebook
    GET /api/notebooks/<filename>/
    """
    try:
        file_path = os.path.join(settings.NOTEBOOKS_DIR, filename)
        
        if not os.path.exists(file_path) or not filename.endswith('.ipynb'):
            return Response(
                {"error": "Notebook not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with open(file_path, 'r') as f:
            notebook_content = json.load(f)
        
        return Response({
            "status": "success",
            "notebook": notebook_content,
            "filename": filename
        })
    
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def notebook_to_html(request, filename):
    """
    Endpoint para convertir notebook a HTML
    GET /api/notebooks/<filename>/html/
    """
    try:
        file_path = os.path.join(settings.NOTEBOOKS_DIR, filename)
        
        if not os.path.exists(file_path) or not filename.endswith('.ipynb'):
            return Response(
                {"error": "Notebook not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Intentar convertir con nbconvert si está disponible
        try:
            import nbformat
            from nbconvert import HTMLExporter
            
            with open(file_path, 'r') as f:
                notebook = nbformat.read(f, as_version=4)
            
            exporter = HTMLExporter()
            html_content, _ = exporter.from_notebook_node(notebook)
            
            return Response({
                "status": "success",
                "html": html_content,
                "filename": filename
            })
        
        except ImportError:
            # Si nbconvert no está disponible, devolver el notebook como JSON
            with open(file_path, 'r') as f:
                notebook_content = json.load(f)
            
            return Response({
                "status": "success",
                "notebook": notebook_content,
                "filename": filename,
                "note": "Install nbconvert for HTML conversion"
            })
    
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
