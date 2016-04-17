import flask
from flask import request
from flask import url_for
from flask import jsonify
from flask import render_template


import json
import logging

# Date handling 
import arrow
import datetime
from dateutil import tz

# Mongo database
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



#routing functions
@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  flask.session['rideRequests'] = get_rideRequests()
  for rideRequest in flask.session['rideRequests']:
      app.logger.debug("rideRequest: " + str(rideRequest))
  return flask.render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#main functions
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


def put_rideRequest(name, cellphone, studentID, pickupTime, pickupLoc, dropoffLoc):
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

  put_rideRequest(name,cellphone,studentID,pickupTime,pickupLoc,dropoffLoc) 
  return jsonify(result="add success")
  


@app.route('/_delete')
def python_method_for_delete():
  """
  Deletes entry by ID
  """
  rideRequestID = request.args.get('objectID', 0, type=str) 
  collection.remove({'_id': ObjectId(rideRequestID)}) 
  return jsonify(result="delete success") 



if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    if CONFIG.DEBUG:
        # Reachable only from the same computer
        app.run(port=CONFIG.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=CONFIG.PORT,host="0.0.0.0")
