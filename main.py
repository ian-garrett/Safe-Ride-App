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

###
# Pages
###

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


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Returns formatted date
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human


def get_rideRequests():
    """
    Returns all rideRequests in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_rideRequest" } ).sort("date", 1):
        record['date'] = arrow.get(record['date']).isoformat()
        try:
          record['_id'] = str(record['_id'])
        except:
          del record['_id']
        records.append(record)
    return records


def put_rideRequest(dt, request):
    """
    Place rideRequest into database
    Args:
       dt: Datetime (arrow) object
       request: Text of rideRequest
    """
    #print(dt)
    date = arrow.get(dt, 'DD/MM/YYYY').to('utc').naive
    record = { "type": "dated_rideRequest", 
               "date": date,
               "text": request,
            }
    collection.insert(record)
    return


@app.route("/_createrideRequest")
def createrideRequest():
  """
  Call put_rideRequest with user input
  """
  date = request.args.get('date', 0, type=str) 
  rideRequest = request.args.get('rideRequest', 0, type=str) 
  put_rideRequest(date,rideRequest) 
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
