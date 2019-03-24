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

user = User(id=2, name='name') 
User.create_table()
# User.drop_table()



# print(User.id.return_mysql_format())
# print(User.name.return_mysql_format())
# print(user.id)
# print(User.objects.create)
# user.name = '2'
# print(user.name)
# print(User.create_table())


# User.objects.create(id=1, name='name')


# cursor.execute('CREATE DATABASE datacamp')
# cursor.execute('SHOW DATABASES')

# databases = cursor.fetchall()
# fetchall содержит ответ

# print(databases)

# for database in databases:
	# print(database)
# cursor.execute('use datacamp')

# cursor.execute('CREATE TABLE Notusers (first_name VARCHAR(255), second_name VARCHAR(255))')
