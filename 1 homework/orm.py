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
        '''Проверяет правильность ввода значения
        '''
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
    '''Метакласс, недобходим для определения метода __new__, для изменения namespace'а классов (детей Model)
    Находит все атрибуты наследованные от класса Field и добавляет их в namespace как отдельный словарь _fields
    Также добавляет _table_name из Meta.
    '''
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')
            
        # todo mro
        print(bases)
        print(bases[0])

        fields = {k: v for k, v in namespace.items()
                  if isinstance(v, Field)}
        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        return super().__new__(mcs, name, bases, namespace)


class Database:
    '''Класс для подключения к базе данных и вывода таблиц на экран
    '''
    db = None
    cursor = None
    @classmethod
    def connection(cls,**kwargs):
        '''Подключение к базе данных
        '''
        cls.db = mysql.connect(
            host = kwargs['host'],
            user = kwargs['user'],
            passwd = kwargs['passwd'],
            database = kwargs['database']
        )
        cls.cursor = cls.db.cursor()

    @classmethod
    def tables(cls):
        '''Возвращает все таблицы из выбранной базы данных
        '''
        cls.cursor.execute("SHOW TABLES")
        tables = cls.cursor.fetchall()
        return tables

class Manage:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        '''Принимает из owner _fields и _table_name
        '''
        if self.model_cls is None:
            self.model_cls = owner
            self.fields = owner._fields
            self.table_name = owner._table_name
        return self

    def get(self, *args):
        '''Возвращает заданные строчки из таблицы
        '''
        cursor = Database.cursor
        if len(args) == 0:
            cursor.execute('SELECT * FROM {table_name}'.format(table_name = self.table_name))
            return cursor.fetchall()
        else:
            stmt = []
            for input_field in args:
                if input_field not in self.fields.items():
                    stmt.append(input_field)
                else: 
                    raise ValueError('input get error')
            cursor.execute('SELECT {fields} FROM {table_name}'.format(
                fields = ', '.join(stmt),
                table_name = self.table_name
                ))
            return cursor.fetchall()
                
    def describe(self, *args):
        '''Возвращает описание полей таблицы
        '''
        cursor = Database.cursor
        if len(args) == 0:
            cursor.execute('DESCRIBE {table_name}'.format(table_name = self.table_name))
            return cursor.fetchall()

    def create(self, *args,**kwargs):
        '''Создаёт строчку в таблице с заданными значениями
        '''
        if len(args) > 0 and len(kwargs) == 0:
            for block in args:
                fields_input = self.validate_input(block) #Валидация значений
                cursor = Database.cursor
                cursor.execute('INSERT INTO {table_name} ({fields_key}) VALUES ({fields_value}) '.format(
                    table_name = self.table_name, 
                    fields_key = ', '.join(fields_input.keys()),
                    fields_value = ', '.join(fields_input.values())
                    ))
                Database.db.commit()

        elif len(args) == 0 and len(kwargs) > 0:
            fields_input = self.validate_input(kwargs)
            cursor = Database.cursor
            cursor.execute('INSERT INTO {table_name} ({fields_key}) VALUES ({fields_value}) '.format(
                table_name = self.table_name, 
                fields_key = ', '.join(fields_input.keys()),
                fields_value = ', '.join(fields_input.values())
                ))
            Database.db.commit()
        # return self

    def remove(self, *args,  **kwargs):
        '''Удаляет строчку с заданными значениями из таблицы
        '''
        cursor = Database.cursor
        def remove_line(fields_input):
            _fields_format = []
            for field_key, field_value in fields_input.items():
                _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
            cursor.execute('DELETE FROM {table_name} WHERE {fields_format} '.format(
                table_name = self.table_name, 
                fields_format = '{}'.format(' AND '.join(_fields_format))
                ))
            Database.db.commit()

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
        '''Обновляет строчку в таблице
        Для коммита необходимо после update() вызвать where()
        Model.objects.update().where()
        OR
        Model.objects.update()
        ...
        Model.objects.where()
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
        return self

    def where(self, *args, **kwargs):
        cursor = Database.cursor
        tmp_stmt = self.stmt
        def add_where_str(fields_input, stmt):
            _fields_format = []
            for field_key, field_value in fields_input.items():
                _fields_format.append('{key} = {value}'.format(key = field_key, value = field_value))
            stmt += ' {fields_where_format} '.format(
                fields_where_format = '{}'.format(' AND '.join(_fields_format))
                )
            return stmt
        if len(args) == 0 and len(kwargs) == 0:
            pass

        elif len(args) > 0 and len(kwargs) == 0:
            counter = 0
            tmp_stmt += ' WHERE'
            for block in args:
                counter += 1 
                fields_input = self.validate_input(block, required=False)
                tmp_stmt = add_where_str(fields_input, tmp_stmt)
                if counter != len(args):
                    tmp_stmt += 'OR'

        elif len(args) == 0 and len(kwargs) > 0:
            tmp_stmt += ' WHERE'
            fields_input = self.validate_input(kwargs, required=False)
            tmp_stmt = add_where_str(fields_input, tmp_stmt)

        else: raise ValueError('input where error')
        cursor.execute(tmp_stmt)
        Database.db.commit()


    def validate_input(self, input_dict, required = True):
        '''Валидация значений
        Если required = True, значит важно чтобы имена полей были назначены верно(также их значения)
        и все поля с атрибутами required были заданы.
        Если False, то он просто проверяет валидность имена полей и их значений.
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

    objects = Manage() # содержит методы для работы с таблицей
    # todo DoesNotExist


    def __init__(self, *_, **kwargs):
        # for field_name, field in self._fields.items():
            # value = field.validate(kwargs.get(field_name))
            # setattr(self, field_name, value)
        pass
    
    @classmethod
    def create_table(cls):
        '''Создаёт таблицу в базе данных
        '''
        cursor = Database.cursor
        cursor.execute('CREATE TABLE {table_name} ({fields}) '.format(
            table_name = cls._table_name, 
            fields = make_fields_stmt(cls._fields)
            ))
    
    @classmethod
    def drop_table(cls):
        '''Удаляет таблицу из базы данных
        '''
        cursor = Database.cursor
        cursor.execute('DROP TABLE {table_name}'.format(table_name= cls._table_name))


# User.objects.filter(id=2).filter(name='petya')
