from flask import Flask
from flask_restful import Resource, Api
from resources.message import Message

app = Flask(__name__)
api = Api(app)

#Add the /Message route to the REST api
api.add_resource(Message, '/Message')

if __name__ == '__main__':
     app.run()
