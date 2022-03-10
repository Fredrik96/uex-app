import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mypass",
)

mycursor = mydb.cursor()

#mycursor.execute("DROP DATABASE app_users_table")

mycursor.execute("SHOW DATABASES")
for db in mycursor:
    print(db)
