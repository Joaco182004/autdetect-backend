# autdetect/ml_models/ml_model_loader.py
import joblib
import os

# Ruta al modelo guardado - usa correctamente os.path para evitar duplicación de rutas
modelo_path = os.path.join(os.path.dirname(__file__), 'modelo_svm_gs.joblib')

# Verifica si el archivo existe
if not os.path.exists(modelo_path):
    raise FileNotFoundError(f"El archivo {modelo_path} no fue encontrado.")

# Cargar el modelo
modelo_tea = joblib.load(modelo_path)
