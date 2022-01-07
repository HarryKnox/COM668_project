from flask import Flask, jsonify, make_response, request
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId


app = Flask(__name__)
CORS(app)

# Get data from mongoDB server
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.fitnessApp
posts = db.posts

# variable for users collection
#users = db.users

# index app route
@app.route('/')
def index():
    return "<h1>Welcome to the fitness app route!</h1>"


# API route to return all leagues
@app.route("/api/v1.0/posts", methods = ["GET"])
def get_all_posts():

    # empty array for posts
    data_to_return = []

    # loop through posts, set ObjectIDs to strings and append
    for post in posts.find():
        post["_id"] = str(post["_id"])
        data_to_return.append(post)

    # return posts data array
    return make_response( jsonify(data_to_return), 200 )


# flask app ran
if __name__ == "__main__":
   app.run(debug=True)