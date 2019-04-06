# import mysql.connector as mysql
# from orm import *
from orm import Database,Model,IntField,StringField

Database.connection(
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

class Man(Users):
	sex = StringField(length=5, required= False)
	class Meta:
		table_name = 'Man'

print(Man._fields)
# Users.create_table()
# Users.drop_table()

# print(Database.tables())
# print(Users.objects.get())

# Users.objects.create(id = 65342, name = 'Pother')
# Users.objects.create(id = 3, name = 'Maximka')
# Users.objects.create({'id': 2, 'name': 'Dasha'}, {'id': 3},{'id': 4, 'name': 'Sanya'})


# Users.objects.remove({'id': 1, "name": "Pother"},{"name": 'Someone'})
# Users.objects.remove(name = 'Artur')

# Users.objects.update({'name' : 'Artur'}).where(
# 	{'name':'Artur'},
# 	{'name':'Nikita', 'id' : 100},
# 	{'id':2}
# 	)

# print(Man.id)
# Man.create_table()
# print(Man.name)
