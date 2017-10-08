from flask_restful import fields, marshal_with, reqparse, Resource
from datetime import datetime
from json import dumps
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.message_service

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'sender', required=True,
    help='The sender\'s username'
)
post_parser.add_argument(
    'reciever', required=True,
    help='The reciever\'s username'
)
post_parser.add_argument(
    'message', required=True,
    help='The text message'
)

get_parser = reqparse.RequestParser()
get_parser.add_argument(
    'reciever', required=True,
    help='The sender\'s username'
)

get_parser = reqparse.RequestParser()
get_parser.add_argument(
    'reciever', required=True,
    help='The reciever\'s username'
)
get_parser.add_argument(
    'from_date', required=False,
    help='The start date to retrieve from'
)
get_parser.add_argument(
    'to_date', required=False,
    help='The end date to retrieve from'
)

del_parser = reqparse.RequestParser()
del_parser.add_argument(
    'reciever', required=True,
    help='The reciever\'s username'
)
del_parser.add_argument(
    'ids', required=True,
    action='append',
    help='The ids of the messages to remove'
)

message_fields = {
    'sender': fields.String,
    'reciever': fields.String,
    'message': fields.String,
    'date_sent': fields.DateTime,
    'date_opened': fields.DateTime
}

message_list_fields = {
    'new_messages': fields.List(fields.Nested(message_fields)),
}


class Message(Resource):
    @marshal_with(message_list_fields)
    def get(self):
        args = get_parser.parse_args()
        if(args.from_date is not None and args.to_date is not None):
            message = fetch_message_list(args.reciever, args.from_date, args.to_date)
        else:
            message = fetch_message_list(args.reciever)
        return message

    @marshal_with(message_fields)
    def post(self):
        args = post_parser.parse_args()
        message = create_message(args.sender, args.reciever, args.message)
        return message

    def delete(self):
        args = del_parser.parse_args()
        del_messages(args.reciever, args.ids)
        return

def create_message(sender, reciever, message):
    message = {"sender": sender, "reciever": reciever, "message": message, 'date_sent': datetime.now()}
    db.messages.insert_one(message)
    return message

def fetch_message_list(reciever, from_date=None, to_date=None):
    opened_date = datetime.now();
    if(from_date is not None and to_date is not None):
        from_date=datetime.strptime(from_date, '%Y-%m-%d')
        to_date=datetime.strptime(to_date, '%Y-%m-%d')
        messages = db.messages.find({'reciever': reciever, 'date_sent': { '$gte': from_date, '$lte': to_date }})
    else:
        messages = db.messages.find({'reciever': reciever, 'date_opened':{'$exists':False}})
    messages.sort("date_sent", -1)
    result = []
    for message in messages:
        result.append(message)
        db.messages.update({'_id': message['_id']}, {'$set': {'date_opened': opened_date}})
    return {'new_messages': result}

def del_messages(reciever, ids):
    ids = list(map(lambda id: ObjectId(id),ids))
    db.messages.delete_many({'reciever': reciever, '_id' : {'$in' : ids}})
