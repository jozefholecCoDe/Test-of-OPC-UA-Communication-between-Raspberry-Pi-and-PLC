import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="SafeControl",
        password="SafeControl2523",
        database="skuska"
    )

    if connection.is_connected():
        print("✅ Connection to MySQL was successful!")

except mysql.connector.Error as err:
    print("❌ Error connecting to MySQL:", err)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("🔌 Connection closed.")