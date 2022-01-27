import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mypass",
)

mycursor = mydb.cursor()

#mycursor.execute("CREATE DATABASE app_users")

mycursor.execute("SHOW DATABASES")
for db in mycursor:
    print(db)
