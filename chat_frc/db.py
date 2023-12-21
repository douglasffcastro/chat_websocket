from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from passlib.hash import bcrypt
from .user import User

class DbUser:

    def __init__(self, client : str, db_name : str, coll_name : str) -> None:
    
        self.client = MongoClient(client)
        self.db_name = self.client.get_database(db_name)
        self.collection = self.db_name.get_collection(coll_name)

    def insert_user(self, username : str, password : str) -> None:
        password_hash = bcrypt.hash(password)
        is_verified = bcrypt.verify(password, password_hash)
        if is_verified:
            self.collection.insert_one({'_id': username, 'password': password_hash})

    def get_user(self, username):
        user_login = self.collection.find_one({'_id' : username})
        if user_login:
            return User(user_login['_id'], user_login['password'])
        else: return None
    
class DbRoom:
    
    def __init__(self, client : str, db_name : str, coll_name_room : str, coll_name_users : str) -> None:
    
        self.client = MongoClient(client)
        self.db_name = self.client.get_database(db_name)
        self.collection_room = self.db_name.get_collection(coll_name_room)
        self.collection_users = self.db_name.get_collection(coll_name_users)

    def add_room_chat(self, room_number : int , admim : str):
        room_id = self.collection_room.insert_one({'room_number' : room_number, 'admim': admim}).inserted_id
        self.add_room_user(room_id, room_number, admim, is_room_admin=True)
        return room_id

    def update_room(self, room_id : str, new_room_number : int):
        self.collection_room.update_one({'_id': ObjectId(room_id)}, {'$set': {'room_number': new_room_number}})
        self.collection_users.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': new_room_number}})


    def get_room(self, room_id : str):
        room = self.collection_room.find_one({'_id': ObjectId(room_id)})
        if room:
            return room
        else: return None


    def add_room_user(self, room_id : str, room_number : int, username : str, is_room_admin : bool=False):
        self.collection_users.insert_one(
            {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_number': room_number, 
             'added_at': datetime.now(), 'is_room_admin': is_room_admin})

    
    def add_room_users(self, room_id : str, room_number : int, usernames : list):
        self.collection_users.insert_many( 
            [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_number': room_number,
            'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])

    
    def remove_room_members(self,room_id : str, usernames : list):
        self.collection_users.delete_one(
            {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})

    
    def get_room_members(self, room_id : str) -> list:
        return list(self.collection_users.find({'_id.room_id': ObjectId(room_id)}))


    
    def get_rooms_for_user(self, username : str) -> list:
        return list(self.collection_users.find({'_id.username': username}))


    def is_room_member(self, room_id, username : str) -> int:
        return self.collection_users.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


    def is_room_admin(self, room_id, username : str) -> int:
        return self.collection_users.count_documents(
            {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})
