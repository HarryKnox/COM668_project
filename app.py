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


# API route to return all exercise posts
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


# API route to add an exercise post
@app.route("/api/v1.0/posts", methods = ["POST"])
def add_exercise_post():

    # validation and then form data taken
    if "type" in request.form and "dist" in request.form and \
    "dType" in request.form and "time" in request.form :

        new_post = {
            "_id" : ObjectId(),
            "userName" : request.form["userName"],
            "date" : request.form["date"],
            "text" : request.form["text"],
            "type" : request.form["type"],
            "dist" : request.form["dist"],
            "dType" : request.form["dType"],
            "time" : request.form["time"]
        }

        # data inserted and id taken
        new_post_id = posts.insert_one(new_post)

        # link for new post set
        new_post_link = "http://localhost:5000/api/v1.0/posts/" + str(new_post_id.inserted_id)

        return make_response( jsonify({"url" : new_post_link}), 201)
    else:
        return make_response( jsonify({"error" : "Missing form data"}), 404)


# API route to function to delete an exercise post
@app.route("/api/v1.0/posts/<string:id>", methods = ["DELETE"])
def delete_post(id):

    # post deleted
    deletePost = posts.delete_one({"_id" : ObjectId(id)})

    # validation of deletion + HTTP codes returned
    if deletePost.deleted_count == 1:
        return make_response ( jsonify({} ), 204)
    else:
        return make_response ( jsonify({"error" : "Invalid post ID"}), 404)




# flask app ran
if __name__ == "__main__":
   app.run(debug=True)