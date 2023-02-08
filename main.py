
from constants import *

from models.user import User, UserModel

user_model = UserModel()

for user in user_model._users:
    print(user.to_dict())

#print(Database(DB_URL, DB_NAME).get_table('users'))