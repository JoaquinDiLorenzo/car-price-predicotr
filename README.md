Estrucutra inicial del poryecto

car_price_predictor/  
│── data/                  # Carpeta para guardar los datos
│   ├── raw/               # Datos sin procesar (scrapeados)
│   ├── processed/         # Datos limpios y listos para el modelo
│── notebooks/             # Jupyter notebooks para exploración y experimentación
│   ├── 01_exploratory_data_analysis.ipynb  # Análisis exploratorio (EDA)
│   ├── 02_feature_engineering.ipynb       # Transformación de datos
│   ├── 03_model_training.ipynb            # Pruebas con modelos
│── src/                   # Código fuente del proyecto  
│   ├── scraping.py        # Script para hacer web scraping  
│   ├── processing.py      # Limpieza y procesamiento de datos  
│   ├── model.py           # Entrenamiento del modelo de predicción  
│   ├── api.py             # Backend para exponer el modelo como API  
│   ├── utils.py           # Funciones auxiliares (como carga/guardado de datos)   
│── requirements.txt       # Dependencias del proyecto  
│── .gitignore             # Archivos a ignorar en Git  
│── README.md              # Documentación del proyecto  

