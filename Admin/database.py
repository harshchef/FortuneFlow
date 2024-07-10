import mysql.connector
 
# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Harsh98321234@',
    'database': 'xxx4'
}
 
# MySQL Connection
def get_db_connection():
    return mysql.connector.connect(**db_config)