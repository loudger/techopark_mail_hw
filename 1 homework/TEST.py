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

class Users(Model):
    id = IntField(required= True)
    name = StringField(length = 22, default='Someone', required= False)

    class Meta:
        table_name = 'Users'


# Users.create_table()
# Users.drop_table()

# Users.objects.create(id = 1, name = 'Artur')
# Users.objects.create(id = 3, name = 'Maximka')
# Users.objects.create({'id': 2, 'name': 'Dasha'}, {'id': 3},{'id': 4, 'name': 'Sanya'})


# Users.objects.remove({'id': 2},{"name": 'Someone'})

# Users.objects.update({'name' : 'Artur', 'id' : 2}).where(
# 	{'name':'Artur'},
# 	{'name':'Nikita', 'id' : 100},
# 	{'id':2}
# 	)



# cursor.execute('CREATE DATABASE datacamp')
# cursor.execute('SHOW DATABASES')

# databases = cursor.fetchall()
# fetchall содержит ответ

# print(databases)

# for database in databases:
	# print(database)
# cursor.execute('use datacamp')

# cursor.execute('CREATE TABLE Notusers (first_name VARCHAR(255), second_name VARCHAR(255))')
