# Install
To install and run the server you need python 3 and the requirements listed in requirements.txt installed.
The database used is monogdb (version 3.2.11) and there's no need for any configuration. The server will try to connect to the default
localhost:27017 and use the collection message_service. Just see to that there's a mongodb service running when starting the server.

To run just type:
    python3 app.py

# Examples
There's no client for the message service so curl is needed to talk to the API.
Here are some examples how you can call the API:

To send a message from a sender called "You" to a reciever called "Me" with a message "Hi buddy!":
curl -H "Content-Type: application/json" -X POST 'http://localhost:5000/Message' -d '{"sender": "You", "reciever": "Me", "message": "Hi buddy!"}'

To get all the new messages for the reciever "Me":
curl -H "Content-Type: application/json" -X GET 'http://localhost:5000/Message' -d '{"reciever": "Me"}'
To get all the messages for the reciever "Me" between the dates 2017-10-01 to 2017-10-10
curl -H "Content-Type: application/json" -X GET 'http://localhost:5000/Message' -d '{"reciever": "Me", "from_date":"2017-10-01", "to_date":"2017-10-10"}'

To delete a message with the id "59da866dc759131685ff5b22". To delete several messages add more ids to the "ids"-array.
curl -H "Content-Type: application/json" -X DELETE 'http://localhost:5000/Message' -d '{"reciever": "Me", "ids":["59da866dc759131685ff5b22"]}'
