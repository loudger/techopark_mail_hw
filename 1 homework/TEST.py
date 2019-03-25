# import mysql.connector as mysql
# from orm import *
from orm import Settings,Model,IntField,StringField

Settings.connection(
	host = 'localhost',
	user = 'Artur',
	passwd = 'Artur', 
	database = 'datacamp'
)



# print(db)

class User(Model):
    id = IntField(required= True)
    name = StringField(length = 22, default='something', required= False)

    class Meta:
        table_name = 'Users'

# User.create_table()
# User.drop_table()
# User.objects.create(id = 1, name = 'Artur')
# User.objects.create(id=2, name='Max')
# User.objects.remove(id = 2, name = 'Max')
print(User.objects)






# cursor.execute('CREATE DATABASE datacamp')
# cursor.execute('SHOW DATABASES')

# databases = cursor.fetchall()
# fetchall содержит ответ

# print(databases)

# for database in databases:
	# print(database)
# cursor.execute('use datacamp')

# cursor.execute('CREATE TABLE Notusers (first_name VARCHAR(255), second_name VARCHAR(255))')
