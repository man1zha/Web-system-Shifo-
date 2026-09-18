import os

class Config:
    SECRET_KEY = 'pharmacy-secret-key-2024'
    DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    PHARMACY_NAME = 'Аптека Шифо'
    PHARMACY_ADDRESS = 'г. Душанбе, ул. Рудаки 12'
    PHARMACY_PHONE = '+992 37 123-45-67'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database.db")