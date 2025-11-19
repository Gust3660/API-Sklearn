import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.io import arff

class ARFFProcessor:
    """Procesador de archivos ARFF"""
    
    @staticmethod
    def load_arff(file_path):
        """Cargar archivo ARFF y convertir a DataFrame"""
        try:
            data, meta = arff.loadarff(file_path)
            df = pd.DataFrame(data)
            
            # Convertir atributos bytes a string si es necesario
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].str.decode('utf-8')
                    except:
                        pass
            
            return df, meta, {"status": "success", "rows": len(df), "columns": len(df.columns)}
        except Exception as e:
            return None, None, {"status": "error", "message": str(e)}


class DatasetDivider:
    """Divisor de datasets - TODO: Reemplazar con tu código de 07_division-del-dataset.ipynb"""
    
    @staticmethod
    def divide_dataset(df, test_size=0.2, random_state=42):
        """
        Dividir dataset en entrenamiento y prueba
        ADAPTABLE: Reemplaza esta función con tu lógica de 07_division-del-dataset.ipynb
        """
        try:
            # Separar features y target
            if 'class' in df.columns:
                X = df.drop('class', axis=1)
                y = df['class']
            elif 'label' in df.columns:
                X = df.drop('label', axis=1)
                y = df['label']
            else:
                X = df.iloc[:, :-1]
                y = df.iloc[:, -1]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            return {
                "status": "success",
                "train_size": len(X_train),
                "test_size": len(X_test),
                "features": len(X.columns),
                "data": {
                    "X_train": X_train,
                    "X_test": X_test,
                    "y_train": y_train,
                    "y_test": y_test,
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class DataPreparator:
    """Preparador de datos - TODO: Reemplazar con tu código de 08_Preparacio-del-dataset.ipynb"""
    
    @staticmethod
    def prepare_data(X_train, X_test, y_train, y_test):
        """
        Preparar datos para el modelo
        ADAPTABLE: Reemplaza esta función con tu lógica de 08_Preparacio-del-dataset.ipynb
        """
        try:
            # Identificar columnas numéricas y categóricas
            numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = X_train.select_dtypes(include=['object']).columns.tolist()
            
            # Normalizar datos numéricos
            scaler = StandardScaler()
            X_train_numeric = X_train[numeric_cols].copy()
            X_test_numeric = X_test[numeric_cols].copy()
            
            X_train_scaled = scaler.fit_transform(X_train_numeric)
            X_test_scaled = scaler.transform(X_test_numeric)
            
            return {
                "status": "success",
                "numeric_features": len(numeric_cols),
                "categorical_features": len(categorical_cols),
                "scaler_info": {
                    "mean": scaler.mean_.tolist(),
                    "scale": scaler.scale_.tolist(),
                },
                "data": {
                    "X_train_scaled": X_train_scaled,
                    "X_test_scaled": X_test_scaled,
                    "y_train": y_train,
                    "y_test": y_test,
                    "numeric_cols": numeric_cols,
                    "categorical_cols": categorical_cols,
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class TransformerPipeline:
    """Pipeline de transformadores - TODO: Reemplazar con tu código de 09_Creacion_de_tranformadores-y_pipelines-personalizados.ipynb"""
    
    @staticmethod
    def apply_transformations(X_train_scaled, X_test_scaled, y_train, y_test, numeric_cols):
        """
        Aplicar transformaciones personalizadas
        ADAPTABLE: Reemplaza esta función con tu lógica de 09_Creacion_de_tranformadores-y_pipelines-personalizados.ipynb
        """
        try:
            # Ejemplo: Aplicar PCA para reducción de dimensionalidad
            from sklearn.decomposition import PCA
            
            pca = PCA(n_components=0.95)  # Mantener 95% de varianza
            X_train_transformed = pca.fit_transform(X_train_scaled)
            X_test_transformed = pca.transform(X_test_scaled)
            
            return {
                "status": "success",
                "original_features": X_train_scaled.shape[1],
                "transformed_features": X_train_transformed.shape[1],
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
                "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
                "data": {
                    "X_train_transformed": X_train_transformed,
                    "X_test_transformed": X_test_transformed,
                    "y_train": y_train,
                    "y_test": y_test,
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
