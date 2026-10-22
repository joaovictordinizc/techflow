import mysql.connector


def conectar():
    return mysql.connector.connect(
        host="172.16.78.173",
        port=3306,
        user="appuser",
        password="SenhaForte@123",
        database="db_techvarejo"
    )
