

from typing import Collection, Iterator
from models.database import Database
from constants import *


class User:

    def __init__(self, username :str, password :str, id :int = None) -> None:
            
        self._username = username
        self._password = password
        self._id = id
    
    @property
    def username(self) -> str:
        return self._username

    @property
    def id(self) -> int:
        return self._id

    @property
    def password(self) -> str:
        return self._password

    def to_dict(self) -> dict:
        return {
            "id":self._id,
            "name": self._username, 
            "password": self._password
        }

    def from_dict(user : dict):
        
        return User(
            id          =user["id"],
            username    =user["name"],
            password    =user["password"]
        )

    def set_id(self, id :int):
        self._id = id

    def set_username(self, username:str):
        self._username = username
    
    def set_password(self, password:str):
        self._password = password


    def __eq__(self, user) -> bool:
        
        return (self.username == user.username) and (self.password == user.password)
        # return self._id == user._id



class UserModel:

    """
        UserModel
    """

    def __init__(self, table :str = 'users') -> None:
        
        self._db = Database(DB_URL, None)
        self.table = table

        self._users : Collection[User] = []

        # load everything
        self.load()

    def load(self) -> Collection[User]:

        self._users = []
        for user in self._db.get_table(self.table):
            self._users.append(User(user["name"], user["password"], user["id"]))
        
        return self._users
    

    # get user by her name
    def get_by_name(self, name) -> User | None:
        
        for user in self._users:
            if user._username == name:
                return user
    

    def get_by_id(self, id) -> User | None:

        for user in self._users:
            if user._id == id:
                return user

    # add user in model
    def add_user(self, name:str, password:str):
        user = User(name, password)

        if not self.user_exist(user):
            user.set_id(len(self._users)) 
            # append user  
            self._users.append(user)
    
    def remove_user(self, id :int):

        i=0
        for user in self._users:
            if user.id() == id:
                self._users.remove(i)
            i += 1
    

    def save(self):
        pass

    
    def user_exist(self, user : User) -> bool :
        for _user in self._users:
            if user == _user:
                return True
        
        return False
        
    
    def auth_user(self, name :str, password :str) -> bool:
        return self.user_exist(User(name, password))
    

