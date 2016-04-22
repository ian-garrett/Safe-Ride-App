import flask
from flask import request
from flask import url_for
from flask import jsonify
from flask import render_template


import json
import logging

# Mongo database
from pymongo import *
from pymongo import MongoClient
from bson.objectid import ObjectId

# Globals
import CONFIG

app = flask.Flask(__name__)

try: 
    dbclient = MongoClient(CONFIG.MONGO_URL)
    db = dbclient.memos # reuseing DB from old project
    collection = db.dated

except:
    print("Failure opening database. Is Mongo running? Correct password?")
    sys.exit(1)

import uuid
app.secret_key = str(uuid.uuid4())



# ROUTING FUNCTIONS
@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  flask.session['rideRequests'] = get_rideRequests()
  for rideRequest in flask.session['rideRequests']:
      app.logger.debug("rideRequest: " + str(rideRequest))
  return flask.render_template('index.html')


@app.route("/dispatcher")
def dispatcher():
  app.logger.debug("Dispatcher page entry")
  flask.session['rideRequests'] = get_rideRequests()
  # check user login parameters from the URL
  username = request.args.get('username')
  password = request.args.get('password')

  # this will allow to check database for when multiple users have been created
  # for dispatcher in collection.find( { "type": "dispatcher" } ).sort("name", 1):
  #       if dispatcher['username']==username and dispatcher['password']==password:
  #         return flask.render_template('dispatcher.html')


  # return flask.render_template('loginFail.html')

  # this hardcoded check will suffice for the current scope of the project and demonstration purposes
  if username=="igarrett" and password=="maythesourcebewithyou":
    return flask.render_template('dispatcher.html')
  return flask.render_template('loginFail.html')


@app.route("/manage")
def manage():
  app.logger.debug("Manage accounts + possible informatics")
  flask.session['dispatchers'] = get_dispatchers()
  # check user login parameters from the URL
  username = request.args.get('username')
  password = request.args.get('password')

  # this will allow to check database for when multiple users have been created
  # for dispatcher in collection.find( { "type": "dispatcher" } ).sort("name", 1):
  #       if dispatcher['username']==username and dispatcher['password']==password:
  #         return flask.render_template('dispatcher.html')


  # return flask.render_template('loginFail.html')

  # this hardcoded check will suffice for the current scope of the project and demonstration purposes
  if username=="igarrett" and password=="maythesourcebewithyou":
    return flask.render_template('manage.html')
  return flask.render_template('loginFail.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

# main functions


# RIDE REQUEST FUNCTIONS

def get_rideRequests():
    """
    Returns all rideRequests in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_rideRequest" } ).sort("pickupTime", 1):
        try:
          record['_id'] = str(record['_id'])
        except:
          del record['_id']
        records.append(record)
    return records


def put_rideRequest(name, cellphone, studentID, pickupTime, pickupLoc, dropoffLoc, passengers, bikes):
    """
    Place rideRequest into database with appropriate attributes
    """
    record = { "type": "dated_rideRequest", 
               "name": name,
               "cellphone": cellphone,
               "studentID": studentID,
               "pickupTime": pickupTime,
               "pickupLoc": pickupLoc,
               "dropoffLoc": dropoffLoc,
               "passengers": passengers,
               "bikes": bikes,
               "assigned": "false",
               "resolved": "false",

            }
    collection.insert(record)
    return
    

@app.route("/_createrideRequest")
def createrideRequest():
  """
  Call put_rideRequest with user input
  """
  name = request.args.get('name', 0, type=str)
  cellphone = request.args.get('cellphone', 0, type=str)
  studentID = request.args.get('studentID', 0, type=str)
  pickupTime = request.args.get('pickupTime', 0, type=str)
  pickupLoc = request.args.get('pickupLoc', 0, type=str)
  dropoffLoc = request.args.get('dropoffLoc', 0, type=str)
  passengers = request.args.get('passengers', 0, type=int)
  bikes = request.args.get('bikes', 0, type=int)

  put_rideRequest(name,cellphone,studentID,pickupTime,pickupLoc,dropoffLoc,passengers,bikes) 
  return jsonify(result="add success")


@app.route('/_delete')
def deleteRideRequest():
  """
  Deletes entry by ID
  """
  rideRequestID = request.args.get('objectID', 0, type=str)
  collection.remove({'_id': ObjectId(rideRequestID)})
  print("SUCCES DELETE")
  return jsonify(result="delete success")


@app.route('/_checkStrikes')
def checkStrikes():
  """
  Check to see if user has three strikes, and if they do return false
  """
  studentID = request.args.get('studentID', 0, type=str)
  print("entering checkstrikes")
  strikes = collection.find( { "type": "user", "studentID": studentID } )
  # strikeCount = strikes[0]["strikes"]
  # print("strikes retrieved")
  # if strikeCount>=3:
  #   print("strikes checked")
  #   return jsonify(result="true")
  # print("if over")
  return jsonify(result="false")

# USER FUNCTIONS

# create user functions

def put_user(name, cellphone, studentID):
    """
    Place user into database with appropriate attributes
    """
    print(name,cellphone,studentID)
    record = { "type": "user",
               "name": name,
               "cellphone": cellphone,
               "studentID": studentID,
               "strikes": 0
   }
    collection.insert(record)
    return


@app.route("/_createuser")
def createuser():
  """
  Get request info and create user user input
  """
  name = request.args.get('name', 0, type=str)
  cellphone = request.args.get('cellphone', 0, type=str)
  studentID = request.args.get('studentID', 0, type=str)

  put_user(name,cellphone,studentID)
  return jsonify(result="add success")

# user strike functions

def incrementStike(studentID):
  """
  Increase user strikes by 1
  """
  print("entering increment strike")
  strikes = collection.find( { "type": "user", "studentID": studentID } )
  strikeCount = strikes[0]["strikes"]
  if strikeCount==0: # for some reason it takes two updates when strikes is at 0
    print("0 strikes thus far")
    collection.update({"studentID": studentID}, {"$inc": {"strikes": 1}})

  collection.update({"studentID": studentID}, {"$inc": {"strikes": 1}})
  print(collection.find( { "type": "user", "studentID": studentID } )[0]["strikes"])
  return


@app.route("/_addStrike")
def addStrike():
  """
  Calls the incrementStike on a studentID
  """
  print("entering add strike")
  studentID = request.args.get('studentID', 0, type=str)
  incrementStike(studentID)
  print("finished incrementStike")
  return jsonify(result="add success")

# MANAGE FUNCTIONS

# dispatcher functions

def get_dispatchers():
    """
    Returns all dispatchers in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dispatcher" } ).sort("name", 1):
        try:
          record['_id'] = str(record['_id'])
        except:
          del record['_id']
        records.append(record)
    return records

def put_dispatcher(name, cellphone):
    """
    Place dispatcher into database with appropriate attributes
    """
    print("begin put dispatcher")
    record = { "type": "dispatcher",
               "name": name,
               "cellphone": cellphone,
   }
    print("about to inert dispatcher")
    collection.insert(record)
    return


@app.route("/_createdispatcher")
def createdispatcher():
  """
  Get dispatcher account
  """
  print("entered createdispatcher")
  name = request.args.get('name', 0, type=str)
  cellphone = request.args.get('cellphone', 0, type=str)
  put_dispatcher(name,cellphone)
  return jsonify(result="add success")


@app.route('/_deletedispatcher')
def deleteDispatcher():
  """
  Deletes dispatcher by ID
  """
  rideRequestID = request.args.get('objectID', 0, type=str)
  collection.remove({'_id': ObjectId(rideRequestID)})
  print("SUCCES DELETE")
  return jsonify(result="delete success")


# OTHER FUNCTIONS

@app.route('/_checkID')
def checkID():
  """
  check if a user had has an account
  """
  studentID = request.args.get('studentID', 0, type=str)
  entryCount = collection.find( { "type": "user", "studentID": studentID } ).count();

  print(entryCount)

  if entryCount == 0:
    print("no account associated with that studentID")
    return jsonify(result="true")
  else:
    print("account already exists")
    return jsonify(result="false")



if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    if CONFIG.DEBUG:
        # Reachable only from the same computer
        app.run(port=CONFIG.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=CONFIG.PORT,host="0.0.0.0")
