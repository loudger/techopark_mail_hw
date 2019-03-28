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
            self.fields = owner._fields
            self.table_name = owner._table_name
        return self

    def create(self, *args,**kwargs):
        if len(args) > 0 and len(kwargs) == 0:
            for block in args:
                fields_input = self.validate_input(block)
                cursor = Settings.cursor
                cursor.execute('INSERT INTO {table_name} ({fields_key}) VALUES ({fields_value}) '.format(
                    table_name = self.table_name, 
                    fields_key = ', '.join(fields_input.keys()),
                    fields_value = ', '.join(fields_input.values())
                    ))
                Settings.db.commit()

        elif len(args) == 0 and len(kwargs) > 0:
            fields_input = self.validate_input(kwargs)
            cursor = Settings.cursor
            cursor.execute('INSERT INTO {table_name} ({fields_key}) VALUES ({fields_value}) '.format(
                table_name = self.table_name, 
                fields_key = ', '.join(fields_input.keys()),
                fields_value = ', '.join(fields_input.values())
                ))
            Settings.db.commit()
        # return self

    def remove(self, *args,  **kwargs):
        cursor = Settings.cursor
        def remove_line(fields_input):
            _fields_format = []
            for field_key, field_value in fields_input.items():
                _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
            cursor.execute('DELETE FROM {table_name} WHERE {fields_format} '.format(
                table_name = self.table_name, 
                fields_format = '{}'.format(' AND '.join(_fields_format))
                ))
            Settings.db.commit()

        if len(args) > 0 and len(kwargs) == 0:
            for block in args:
                fields_input = self.validate_input(block, required=False)
                remove_line(fields_input)

        elif len(args) == 0 and len(kwargs) > 0:
            fields_input = self.validate_input(kwargs, required=False)
            remove_line(fields_input)

        else: ValueError('Error input')
        # return self

    def update(self, *args ,**kwargs):
        '''Необходимо после update() вызвать where()
            Model.objects.update().where()
        '''
        if len(args) == 1 and len(kwargs) == 0:
            fields_input = self.validate_input(args[0], required=False)
        elif len(args) == 0 and len(kwargs) > 0:
            fields_input = self.validate_input(kwargs, required=False)
        else: raise ValueError('input update error')
        _fields_format = []
        for field_key, field_value in fields_input.items():
            _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
        self.stmt = 'UPDATE {table_name} SET {fields_set_format}'.format(
                table_name = self.table_name, 
                fields_set_format = '{}'.format(' , '.join(_fields_format))
                )
        # print(stmt)
        return self

    def where(self, *args, **kwargs):
        cursor = Settings.cursor
        def add_where_str(fields_input):
            _fields_format = []
            for field_key, field_value in fields_input.items():
                _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
            self.stmt += ' {fields_where_format} '.format(
                fields_where_format = '{}'.format(' AND '.join(_fields_format))
                )
        if len(args) == 0 and len(kwargs) == 0:
            cursor.execute(self.stmt)
            Settings.db.commit()

        elif len(args) > 0 and len(kwargs) == 0:
            counter = 0
            self.stmt += ' WHERE'
            for block in args:
                counter += 1 
                fields_input = self.validate_input(block, required=False)
                add_where_str(fields_input)
                if counter != len(args):
                    self.stmt += 'OR'

        elif len(args) == 0 and len(kwargs) > 0:
            self.stmt += ' WHERE'
            fields_input = self.validate_input(kwargs, required=False)
            add_where_str(fields_input)

        else: raise ValueError('input where error')
        cursor.execute(self.stmt)
        Settings.db.commit()
        del self.stmt



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


        
# class classproperty(object):
#     def __init__(self, fget):
#         self.fget = fget

#     def __get__(self, owner, cls):
#         return self.fget(cls)

class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects = Manage()
    # todo DoesNotExist


    # @classproperty
    # def objects(cls):
    #     return Manage(cls._fields, cls._table_name)



    def __init__(self, *_, **kwargs):
        # for field_name, field in self._fields.items():
            # value = field.validate(kwargs.get(field_name))
            # setattr(self, field_name, value)
        pass
    
    @classmethod
    def create_table(cls):
        cursor = Settings.cursor
        # cursor.execute
        print('CREATE TABLE {table_name} ({fields}) '.format(
            table_name = cls._table_name, 
            fields = make_fields_stmt(cls._fields)
            ))
    
    @classmethod
    def drop_table(cls):
        cursor = Settings.cursor
        cursor.execute('DROP TABLE {table_name}'.format(table_name= cls._table_name))


# User.objects.filter(id=2).filter(name='petya')

# user.save()
# user.delete()
