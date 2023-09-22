import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="TIKTOKPASS123",
        database="tiktok"
    )

    if mydb.is_connected():
        print("Successfully connected to the database!")
        mydb.close()
    else:
        print("Failed to connect to the database.")

except Exception as e:
    print("Error:", e)
