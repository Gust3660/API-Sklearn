from django.urls import path
from . import views

urlpatterns = [
    # Endpoints para procesamiento de datos
    path("upload-dataset/", views.upload_dataset, name="upload_dataset"),
    path("divide-dataset/", views.divide_dataset, name="divide_dataset"),
    path("prepare-data/", views.prepare_data, name="prepare_data"),
    path("apply-transformers/", views.apply_transformers, name="apply_transformers"),
    path("pipeline-full/", views.pipeline_full, name="pipeline_full"),
    
    # Endpoints para visualización de notebooks
    path("notebooks/list/", views.list_notebooks, name="list_notebooks"),
    path("notebooks/<str:filename>/", views.get_notebook, name="get_notebook"),
    path("notebooks/<str:filename>/html/", views.notebook_to_html, name="notebook_to_html"),
]
