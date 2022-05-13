from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from datetime import datetime

db ="private_wall"

class Message:
    def __init__( self , data ):
        self.id = data['id']
        self.message = data['message']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.sender_id = data['sender_id']
        self.time_elapsed = data['time_elapsed']
        self.sender_info = data['sender_info']

    @staticmethod
    def validate_registration(form_data):
        is_valid = True
        if len(form_data['message']) < 5:
            flash(u"Message must be at least 5 characters.", 'message error')
            is_valid = False
        return is_valid

    @classmethod
    def save(cls, data):
        query = "INSERT INTO messages (message, user_id, sender_id) VALUES (%(message)s, %(receiver)s, %(sender_id)s);"
        return connectToMySQL(db).query_db(query, data)  

    @classmethod
    def delete(cls, id):
        query  = f"DELETE FROM messages WHERE id = %(id)s;"
        return connectToMySQL(db).query_db(query, {'id':id})

    def timespan(self):
        now = datetime.now()
        elapse = now - self.created_at

        