#Script for clearing out all rideRequests from a DB
from pymongo import MongoClient

import CONFIG

try:
	dbclient = MongoClient(CONFIG.MONGO_URL)
	db = dbclient.memos
	collection = db.dated

except:
	print("Failure opening database.")
	sys.exit(1)

for record in collection.find( { "type": "dated_rideRequest" } ).sort("pickupTime", 1):
	del record;