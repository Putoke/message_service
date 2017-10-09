from flask_restful import fields, marshal_with, reqparse, Resource
from datetime import datetime
from json import dumps
from pymongo import MongoClient
from bson.objectid import ObjectId

#Connect to mongo
client = MongoClient()
#Select db message_service
db = client.message_service

#Request parser for post route
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

#Request parser for get route
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

#Request parser for delete route
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

#Fields for a message objet
message_fields = {
    '_id': fields.String,
    'sender': fields.String,
    'reciever': fields.String,
    'message': fields.String,
    'date_sent': fields.DateTime,
    'date_opened': fields.DateTime
}

#List of messages
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
        del_count = del_messages(args.reciever, args.ids)
        return {"num_deleted": del_count}

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
    result = [] #Create a result array for the return data
    for message in messages:
        result.append(message) #Append to result array, messages will be empty after the update
        db.messages.update({'_id': message['_id']}, {'$set': {'date_opened': opened_date}})
    for message in result:
        message['_id'] = str(message['_id'])#Need to remap ObjectId to String so the id can be read in the response
    return {'new_messages': result}

def del_messages(reciever, ids):
    ids = list(map(lambda id: ObjectId(id),ids)) #Need to remap the ids to ObjectId that mongo uses
    res = db.messages.delete_many({'reciever': reciever, '_id' : {'$in' : ids}})
    return res.deleted_count
