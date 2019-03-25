# Homework
import mysql.connector as mysql

def make_fields_stmt(meta_fields):
    '''Принимает словарь типа {'name': <orm.StringFiled>, ...}
    Чтобы вернуть строчку например 'name VARCHAR(20) DEFAULT 'John' NOT NULL, ...'
    '''
    fields = []
    for name_field, value_field in meta_fields.items():
        fields.append('{name} {info}'.format(
            name = name_field, 
            info = value_field.return_mysql_format()
            ))
    return ', '.join(fields)

class Field:
    def __init__(self, f_type, required:bool =True, default = None):
        if not isinstance(required, bool):
            raise ValueError('required is not bool')
        if not isinstance(default,(f_type,type(None))):
            raise ValueError('default is not {}'.format(f_type))
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None and not self.required:
            return None
        if not isinstance(value, (self.f_type, type(None))):
            print(value, type(value), self.f_type)
            raise ValueError('input ValueError')
        return self.f_type(value)


class IntField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(int, required, default)

    def return_mysql_format(self):
        ''' Используется для вывода строчки например 'id DEFAULT 5 NOT NULL'
        '''
        result = ['INT']
        if self.default != None:
            result.append('DEFAULT')
            result.append(str(self.default))
        if self.required:
            result.append('NOT')
        result.append('NULL')
        return ' '.join(result)

class StringField(Field):
    def __init__(self, required:bool =True, length:int = None, default = None):
        if length == None or length <= 0 or length > 65535:
            raise ValueError('length error')
        super().__init__(str, required, default)
        self.length = length

    def return_mysql_format(self):
        ''' Используется для вывода строчки например  'name VARCHAR(20) DEFAULT 'John' NOT NULL'
        '''
        result = ['VARCHAR({length})'.format(length = self.length)]
        if self.default != None:
            result.append('DEFAULT')
            result.append("'{}'".format(self.default))
        if self.required:
            result.append('NOT')
        result.append('NULL')
        return ' '.join(result)

class DataField(Field):
    '''Не реализован
    '''
    def __init__(self, required=True, default = None):
        super().__init__(str, required, default)


# --------------------------------------------------------------


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')
            
        # todo mro Возвращает саписок родит классов
        # забрать все методы из род классов в нужном порядке!
        # не понял, неужели не все поля и методы наследуются?

        fields = {k: v for k, v in namespace.items()
                  if isinstance(v, Field)}
        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        return super().__new__(mcs, name, bases, namespace)

class Settings:
    db = None
    cursor = None
    @classmethod
    def connection(cls,**kwargs):
        cls.db = mysql.connect(
            host = kwargs['host'],
            user = kwargs['user'],
            passwd = kwargs['passwd'],
            database = kwargs['database']
        )
        cls.cursor = cls.db.cursor()

class Manage:
    def __init__(self, fields, table_name):
        self.fields = fields     
        self.table_name = table_name    

    # def __get__(self, instance, owner):
    #     print('!!!')
    #     return self.fields

    def create(self, **kwargs):
        fields_input = self.validate_input(kwargs)
        cursor = Settings.cursor
        cursor.execute('INSERT INTO {table_name} ({fields_key}) VALUES ({fields_value}) '.format(
            table_name = self.table_name, 
            fields_key = ', '.join(fields_input.keys()),
            fields_value = ', '.join(fields_input.values())
            ))
        Settings.db.commit()

    def remove(self, **kwargs):
        fields_input = self.validate_input(kwargs, required=False)
        cursor = Settings.cursor
        _fields_format = []
        for field_key, field_value in fields_input.items():
            _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
        cursor.execute('DELETE FROM {table_name} WHERE {fields_format} '.format(
            table_name = self.table_name, 
            fields_format = '{}'.format(' AND '.join(_fields_format))
            ))
        Settings.db.commit()




    def validate_input(self, input_dict, required = True):
        '''
        '''
        result = {}
        for input_key, input_value in input_dict.items():
            if input_key not in self.fields:
                raise ValueError('extra attributes')
            _input_value = self.fields[input_key].validate(input_value)
            if isinstance(_input_value,str):
                result[input_key] = "'" + _input_value + "'"                
            else: 
                result[input_key] = str(_input_value)
        if required:
            for field_key, field in self.fields.items():
                if field.required and (field_key not in result):
                    raise ValueError('not enough attributes')
        return result


        
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner, cls):
        return self.fget(cls)

class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    # objects = Manage(_fields)
    # todo DoesNotExist

    @classproperty
    def objects(cls):
        return Manage(cls._fields, cls._table_name)


    def __init__(self, *_, **kwargs):
        # for field_name, field in self._fields.items():
            # value = field.validate(kwargs.get(field_name))
            # setattr(self, field_name, value)
        pass
    
    @classmethod
    def create_table(cls):
        cursor = Settings.cursor
        cursor.execute('CREATE TABLE {table_name} ({fields}) '.format(
            table_name = cls._table_name, 
            fields = make_fields_stmt(cls._fields)
            ))
    
    @classmethod
    def drop_table(cls):
        cursor = Settings.cursor
        cursor.execute('DROP TABLE {table_name}'.format(table_name= cls._table_name))

    @classmethod
    def update_table(cls):
        pass

# class Man(User):
#     sex = StringField()

# User.objects.create(id=1, name='name')
# User.objects.update(id=1)
# User.objects.delete(id=1)

# User.objects.filter(id=2).filter(name='petya')

# user.save()
# user.delete()
