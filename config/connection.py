import mysql.connector
from mysql.connector import pooling
from config.settings import settings

dbconfig = {
    "host": settings.MYSQL_HOST,
    "user": settings.MYSQL_USER,
    "password": settings.MYSQL_PASSWORD,
    "database": settings.MYSQL_DB,
    "port": settings.MYSQL_PORT,
    "autocommit": True,
    "charset": "utf8mb4"
}
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="telegram_pool",
        pool_size=5,
        **dbconfig
    )
except Exception as e:
    print(f"❌ Database connection pool error: {e}")
    connection_pool = None
def get_connection():
    if not connection_pool:
        raise Exception("Database pool chưa được khởi tạo!")
    return connection_pool.get_connection()
