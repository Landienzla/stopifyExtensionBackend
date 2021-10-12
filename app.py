from flask import Flask, request
from flask.globals import request
from flask.helpers import make_response
from flask_pymongo import PyMongo
from flask_cors import CORS
import json
from datetime import datetime
from threading import Thread

app = Flask(__name__)
app.config[
    "MONGO_URI"
] = ""
CORS(app)
mongo = PyMongo(app)
db = mongo.db


@app.route("/")
def home_page():
    return "<h1>Hello From Flask</h1>"


@app.route("/users/")
def users():
    users = []
    usersDB = mongo.db.stopify.find()
    for i in usersDB:
        users.append(i)
    res = make_response(json.dumps(users, default=str))
    res.mimetype = "application/json"
    return res


@app.route("/users/<userId>/")
def user(userId):
    user = db.stopify.find_one({"userId": userId})
    res = make_response(json.dumps(user, default=str))
    res.mimetype = "application/json"
    return res


@app.route("/users/<userId>/<userName>/addData/followers", methods=["POST"])
def addFollowersData(userId, userName):
    requestData = json.loads(request.data)
    if db.stopify.find_one({"userId": userId, "lastRecords": True}):
        db.stopify.delete_one({"userId": userId, "lastRecords": False})
        db.stopify.update(
            {"userId": userId, "lastRecords": True}, {"$set": {"lastRecords": False}}
        )
        db.stopify.insert_one(
            {
                "userId": userId,
                "userName": userName,
                "followersData": requestData,
                "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "lastRecords": True,
            }
        )
    else:
        db.stopify.insert_one(
            {
                "userId": userId,
                "userName": userName,
                "followersData": requestData,
                "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "lastRecords": True,
            }
        )
    return "oq", 200


@app.route("/users/<userId>/<userName>/addData/following", methods=["POST"])
def addFollowingData(userId, userName):
    requestData = json.loads(request.data)

    if db.stopify.find_one({"userId": userId}):
        db.stopify.update(
            {"userId": userId, "lastRecords": True},
            {"$set": {"followingData": requestData}},
        )
    else:
        db.stopify.insert_one(
            {
                "userId": userId,
                "userName": userName,
                "followingData": requestData,
                "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "lastRecords": True,
            }
        )
    return "oq", 200


@app.route("/users/<userId>/<userName>/addData/playlists", methods=["POST"])
def addPlaylistsData(userId, userName):
    requestData = json.loads(request.data)
    if db.stopify.find_one({"userId": userId}):
        db.stopify.update({"userId": userId}, {"$set": {"playlistData": requestData}})
    else:
        db.stopify.insert_one(
            {
                "userId": userId,
                "userName": userName,
                "playlistData": requestData,
                "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )
    return "oq", 200


@app.route("/stalk/<userId>/<url>")
@app.route("/stalk/<userId>", defaults={"url": ""})
def stalk(userId, url):
    if db.stopify.find_one({"userId": userId, "lastRecords": True}):
        if db.stopify.find_one({"userId": userId, "lastRecords": True}):
            lastRecords = db.stopify.find_one({"userId": userId, "lastRecords": True})
            oldRecords = db.stopify.find_one({"userId": userId, "lastRecords": False})
            oldFollowers = []
            lastFollowers = []
            oldFollowersId = []
            for data in oldRecords["followersData"]:
                oldFollowers.append(data["followerName"])
                oldFollowersId.append(data["followerId"])
            for data in lastRecords["followersData"]:
                lastFollowers.append(data["followerName"])
            if oldFollowers == lastFollowers:
                res = make_response(json.dumps("Kacak Yok", default=str))
                res.mimetype = "application/json"
                return res, 200

            else:
                awols = list(set(oldFollowers) - set(lastFollowers))
                print(awols)
                awolsData = {}
                for name in awols:
                    for _id in oldFollowersId:
                        awolsData[name] = _id
                res = make_response(json.dumps(awolsData, default=str))
                res.mimetype = "application/json"
                print(oldFollowers)
                print(lastFollowers)
                return res, 331
    else:
        return "Error", 300
