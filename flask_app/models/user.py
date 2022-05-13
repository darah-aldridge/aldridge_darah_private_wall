import email
import imp, re
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_app import app
from datetime import datetime
from datetime import timedelta
import math
from flask_app.models.message import Message

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
current_time = datetime.now()

db ="private_wall"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r"^[A-Za-z]+$") 

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']  
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.message_list = []

    def timelapse(time):
        past_time = current_time - time
        if past_time.days >= 1:
            return f'{past_time.days} day ago'
        elif past_time.days >= 1 <=0 :
            return f'{past_time.days} day ago'
        elif math.floor(past_time.total_seconds()) / 60 >= 60:
            return f'{math.floor(math.floor((past_time.total_seconds())/60)/60)} hours ago'
        elif math.floor(past_time.total_seconds()) / 60 == 60:
            return f'{math.floor(math.floor((past_time.total_seconds())/60)/60)} hour ago'
        elif math.floor(past_time.total_seconds()) >= 60:
            return f'{math.floor(past_time.total_seconds()/60)} minutes ago'
        elif math.floor(past_time.total_seconds()) < 60:
            return f'{math.floor(past_time.total_seconds())} seconds ago'    

    @staticmethod
    def validate_registration(form_data):
        is_valid = True
        if not EMAIL_REGEX.match(form_data['email']): 
            flash(u"Invalid email address!", 'register error')
            is_valid = False
        if len(form_data['first_name']) < 2:
            flash(u"First name must be at least 2 characters.", 'register error')
            is_valid = False
        if not form_data['first_name']:
            flash(u"You must include a first name.", 'register error')
            is_valid = False
        if not NAME_REGEX.match(form_data['first_name']):
            flash(u"You can only use letters for your first name.", 'register error')
            is_valid = False
        if len(form_data['last_name']) < 2:
            flash(u"Last name must be at least 2 characters.", 'register error')
            is_valid = False
        if not form_data['last_name']:
            flash(u"You must include a last name.", 'register error')
            is_valid = False
        if not NAME_REGEX.match(form_data['last_name']):
            flash(u"You can only use letters for your last name.", 'register error')
            is_valid = False
        if not form_data['email']:
            flash(u"You must include an email.", 'register error')
            is_valid = False
        if not form_data['password']:
            flash(u"You must include an password.", 'register error')
            is_valid = False
        if User.get_by_email({'email': form_data['email']}):
            flash(u"Email address is already in use!", 'register error')
            is_valid=False
        if form_data['password'] != form_data['confirm_password']:
            flash(u"Passwords don't match!", 'register error')
            is_valid=False
        if len(form_data['password']) < 8:
            flash(u"Password must be at least 8 characters.", 'register error')
            is_valid = False
        return is_valid

    @classmethod
    def get_one(cls, id):
        query  = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL(db).query_db(query, {'id':id})
        return cls(result[0])

    @classmethod
    def get_all(cls, id):
        query = "SELECT * FROM users WHERE id != %(id)s ORDER BY first_name ASC;"
        results = connectToMySQL(db).query_db(query, {'id':id})
        users = []
        for user in results:
            users.append( cls(user) )
        return users

    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return connectToMySQL(db).query_db( query, data )  

    @classmethod
    def check(cls, email, password):
        query  = "SELECT * FROM users WHERE password = %(password)s && email = %(email)s;"
        results = connectToMySQL(db).query_db(query)
        if results:
            return cls(results[0])
        else:
            return False
    
    @classmethod
    def login(cls, data):
        query  = "SELECT * FROM users WHERE password = %(password)s && email = %(email)s;"
        results = connectToMySQL(db).query_db(query)
        if results:
            return cls(results[0])
        else:
            return False
        
    @classmethod
    def get_by_email(cls, email):
        query  = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(db).query_db(query, email)
        if len(results) < 1:
            return False
        if results:
            return cls(results[0])
        else:
            return False
    
    @classmethod
    def get_one_user_with_messages(cls, user_id):
        query = f"SELECT * FROM messages LEFT JOIN users ON users.id = messages.sender_id LEFT JOIN users as users2 ON users2.id = messages.user_id WHERE messages.user_id = {user_id};"
        results = connectToMySQL(db).query_db(query)
        userWithMessages = False
        for row in results:
            if not userWithMessages:
                user = {
                    "id": row['users2.id'],
                    "first_name": row['users2.first_name'],
                    "last_name": row['users2.last_name'],
                    "email": row['users2.email'],
                    "password": row['users2.password'],
                    "created_at": row['users2.created_at'],
                    "updated_at": row['users2.updated_at']
                }
                userWithMessages = cls(user)
            sender = {
                    "id": row['id'],
                    "first_name": row['first_name'],
                    "last_name": row['last_name'],
                    "email": row['email'],
                    "password": row['password'],
                    "created_at": row['users.created_at'],
                    "updated_at": row['users.updated_at'],
                }
            data = {
                "id": row['id'],
                "message": row['message'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "user_id": row['user_id'],
                "sender_id": row['sender_id'],
                "time_elapsed": cls.timelapse(row['created_at']),
                "sender_info": cls(sender),
            }
            session['message_count'] = len(results)
            userWithMessages.message_list.append(Message(data))
        return userWithMessages
