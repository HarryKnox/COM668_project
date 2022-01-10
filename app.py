import datetime
from flask import Flask, jsonify, make_response, request
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
from datetime import date,datetime,timedelta

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

        # using dType convert distance to KM
        if request.form["dType"] == "Kilometres":
            distance = request.form["dist"]
        
        else:
            distance = int(request.form["dist"])*1.60934

        # slice out timezone bit and then set string to date
        sliced_date = request.form["date"][0:24]
        
        # use below to fake dates, for test data
        #sliced_date = "Mon Jan 12 2021 01:26:05"

        fixed_date = datetime.strptime(sliced_date,'%a %b %d %Y %H:%M:%S')

        # new post dictionary delcared
        new_post = {
            "_id" : ObjectId(),
            "userName" : request.form["userName"],
            "date" : fixed_date,
            "text" : request.form["text"],
            "type" : request.form["type"],
            "dist" : distance,
            "time" : time2Minutes(request.form["time"]),
            "userID" : request.form["userID"]
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

# API route to generate stats for a user
@app.route("/api/v1.0/stats/<string:id>", methods = ["GET"])
def get_user_stats(id):

    # empty array to hold user's posts
    users_posts = []

    # loop through each post and append matching ID posts
    for post in posts.find():
        if(post["userID"] == id):
            users_posts.append(post)


    # posts filtered out according to time period
    time_period = request.args.get("param")

    # get todays date
    today = date.today()

    # var to hold new posts
    correctDate_posts = []

    # take only posts from last month
    if time_period == "Monthly":

        # loop through posts
        for post in users_posts:

            # if correct month and year then append
            if post["date"].month == today.month and post["date"].year == today.year:
                correctDate_posts.append(post)
        
    
    # takes only post from last week
    if time_period == "Weekly":

        # loop through posts
        for post in users_posts:

            # array of days in last week
            lastWeek = []

            # loop through last 7 days
            for i in range(0,7):
                lastWeek.append(today-timedelta(days=i))

            # if post date in last week array, then append
            for day in lastWeek:
                if post["date"].month == day.month and post["date"].year == day.year and \
                    post["date"].day == day.day:
                    correctDate_posts.append(post)

    # for all time
    if time_period == "AllTime":
        correctDate_posts = users_posts

    # dictionary to hold stats to be returned
    stats_to_return = {
        "favourite_exercise" : getFavouriteType(correctDate_posts),
        "total_exercises" : len(correctDate_posts),
        "total_distance" : 0,
        "total_time" : 0,
        "average_speed" : 0
    }

    # loop through all user posts and take values
    for userPost in correctDate_posts:
        stats_to_return["total_distance"] = int(stats_to_return["total_distance"]) + int(userPost["dist"])
        stats_to_return["total_time"] = int(stats_to_return["total_time"]) + int(userPost["time"])

    # average speed set
    stats_to_return["average_speed"] = round(stats_to_return["total_distance"]/stats_to_return["total_time"],2)

    return(stats_to_return)


# function to find most frequent exercise type in a list of posts
# DOESNT HANDLE DRAWS
def getFavouriteType(posts):

    # validation for if no posts
    if (len(posts) == 0):
        return("None")

    # array to hold all post types
    types = []

    # loop through all posts and append to array
    for post in posts:
        types.append(post["type"])

    # find most common one
    favourite = max(set(types), key=types.count)

    # value returned
    return(favourite)



# function to convert from time format to minutes
def time2Minutes(time):

    # time split by colon
    split_time =  time.split(":")

    # var to hold overall time in minutes - hours added
    minutes = int(split_time[0])*60 + int(split_time[1]) + int(split_time[2])/60

    return(minutes)


# flask app ran
if __name__ == "__main__":
   app.run(debug=True)