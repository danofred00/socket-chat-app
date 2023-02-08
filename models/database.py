
from json.decoder import JSONDecoder
from typing import Collection, Mapping
import os

def get_users() -> Collection[dict]:

    buffer = str()

    with open('assets/db.json') as fp:
        buffer = fp.read().strip()
        fp.close()

    users = JSONDecoder().decode(buffer)
    return users['users']


class DatabaseInterface:

    def get_table(self, table :str) -> Collection[dict]:
        raise NotImplemented

    @property
    def tables(self) -> Collection:
        raise NotImplemented

    @property
    def name(self) -> str:
        raise NotImplemented

    def open(self):
        raise NotImplemented
    
    def close(self):
        raise NotImplemented
    
    def create_table(self, table:str, **kargs):
        raise NotImplemented
    
    def drop_table(self, table :str):
        raise NotImplemented
    
    def insert(self, table :str, element):
        pass

class DataBaseType:
    
    def __str__():
        raise NotImplemented

class  DataBaseTypeFile(DataBaseType):
    
    def __str__():
        raise NotImplemented

class DataBaseTypeJson(DataBaseTypeFile):
    def __str__():
        return 'json'

class Database(DatabaseInterface):

    def __init__(self, url :str, name :str, _db_type : DataBaseType = None) -> None:
        
        self._name = name
        self._url = url
        self._tables : Collection[str] = []
        self._type = _db_type

        # get path
        if name:
            self.path = os.path.join(self._url, self._name)
        else:
            self.path = url

        # load tales names
        self.load_tables_name()


    def name(self) -> str:
        return self._name
    

    def get_table(self, table: str) -> Collection[dict]:

        if table.lower() in self._tables:
            
            buffer = str()
            with open(self.path) as fp:
                buffer = fp.read().strip()
                fp.close()
            
            return JSONDecoder().decode(buffer)[table.lower()]

    def open(self):
        pass


    def load_tables_name(self):

        buffer = str()
        with open(self.path) as fp:
            buffer = fp.read().strip()
            fp.close()
        
        for k in JSONDecoder().decode(buffer).keys():
            self._tables.append(k.lower())