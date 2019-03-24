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
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    def create(self):
        print(self.model_cls)



class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects = Manage()
    # todo DoesNotExist

    def __init__(self, *_, **kwargs):
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)
    
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
