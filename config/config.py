import os

class SystemConfig:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root123')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'flask_crud_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_POOL_NAME = os.environ.get('MYSQL_POOL_NAME', 'flask_pool')
    MYSQL_POOL_SIZE = int(os.environ.get('MYSQL_POOL_SIZE', 5))
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
    API_USERNAME = os.environ.get('API_USERNAME', 'admin')
    API_PASSWORD = os.environ.get('API_PASSWORD', 'password')