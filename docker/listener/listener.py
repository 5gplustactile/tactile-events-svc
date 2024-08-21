"""A webhook listener service."""

from datetime import datetime
from http import HTTPStatus
import json
import logging
from flask import Flask, request, abort, jsonify
from jsonschema import validate, ValidationError
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv


#from _utils import fminio

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))
print('PATHH: ', sys.path[0])

#Define current path
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#Load env file
env_path_envFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', '_env', '.env'))
load_dotenv(env_path_envFolder)

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
print("Current path:", current_path)

print('MONGO_HOST1:', os.getenv('MONGO_HOST'))

SCHEMA_PATH = 'schema.json'

#CONNECTION_STRING = "mongodb://root:example@mongo"
CONNECTION_STRING = "mongodb://"+os.getenv('MONGO_USER')+":"+os.getenv('MONGO_PASSWORD')+"@"+os.getenv('MONGO_HOST')

EXPIRE_AFTER_SECONDS = 60 * 60 * 24 * 14  # two week

MAX_DOCUMENTS = 10000


def get_collection(DB_NAME,COL_NAME):
    """Get the collection of events."""
    client = MongoClient(CONNECTION_STRING)

    database = client[DB_NAME]
    collection = database[COL_NAME]
    collection.find()

    logging.info('Ready collection')

    return collection


def event_is_valid(data):
   
    """Check if the structure of the event is valid"""
    with open(SCHEMA_PATH, encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    try:
        app.logger.info('Checkpoint')
        app.logger.info(data)
        app.logger.info(type(data))
        app.logger.info(schema)
        app.logger.info(type(schema))

        #validate(instance=data, schema=schema)
        return True

    except ValidationError:
        app.logger.info('validation error')
        return False


app = Flask(__name__)
app.logger.setLevel(logging.INFO)


#################### NWDAF ANALYTICS CORE API #############################
@app.post('/events-core-analytics')
def event_post():
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_CORE_ANA') #'eventsNfLoadOpen5gs'
    print('MONGO_DB:', os.getenv('MONGO_EVN_DB'))
    print('MONGO_CORE ANA:', os.getenv('MONGO_EVN_COL_CORE_ANA'))
    """Register webhook events."""
    if not request.is_json:
        app.logger.info('Invalid request.It is not a json.')
        abort(HTTPStatus.BAD_REQUEST)

    event = request.get_json()

    # if not event_is_valid(event):
    #     app.logger.info('Invalid request. It is not a schema valid request.')
    #     abort(HTTPStatus.BAD_REQUEST)

    app.logger.info('Valid request: %s', str(event))

    app.logger.info('-1----------------------------------')
    app.logger.info('Insert into %s and colelction %s', str(DB_NAME),  str(COL_NAME))

    # Add a time stamp to each event for traceability and in order to keep
    # track of lifetime.
    event_with_timestamp = {}
    event_with_timestamp["data"] = json.loads(event).copy()
    app.logger.info('--2---------------------------------')

    # Metadata info
    event_with_timestamp["owner"] = 'Telefonica'
    event_with_timestamp["entity_source"] = 'prometheus-opengs'
    event_with_timestamp["event_name"] = 'CORE_METRIC'
    event_with_timestamp["entity_resource"] = 'open5gs-cpu-metric'
    event_with_timestamp["gdpr_analytic"] = True
    event_with_timestamp["gdpr_commercial"] = False
    app.logger.info('--3---------------------------------')

    event_with_timestamp["createdAt"] = datetime.now()
    app.logger.info('--4---------------------------------')


    collection = get_collection(DB_NAME,COL_NAME)
    app.logger.info('----collection created-------------------------------')

    collection.create_index([("createdAt", pymongo.ASCENDING)],
                             expireAfterSeconds=EXPIRE_AFTER_SECONDS)

    app.logger.info('----index created-------------------------------')


    app.logger.info('Insert info: %s', str(event_with_timestamp))

    try:
        app.logger.info('----insert one-------------------------------')

        collection.insert_one(event_with_timestamp)
    except: 
        app.logger.info('Error occurred when inserting data in DB')


    return jsonify({'success': True})



#################### NWDAF ANALYTICS QOS API #############################
@app.post('/events-devo-qos-analytics')
def nwdaf_nokia_post():
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_QOS_ANA') 
    print('MONGO_DB:', os.getenv('MONGO_EVN_DB'))
    print('MONGO_QOS ANA:', os.getenv('MONGO_EVN_COL_QOS_ANA'))
    """Register webhook events."""
    print('Start registaring event..')
    if not request.is_json:
        app.logger.info('Invalid request.It is not a json.')
        abort(HTTPStatus.BAD_REQUEST)

    event = request.get_json()

    #print('check event: ', event)

    # if not event_is_valid(event):
    #     app.logger.info('Invalid request. It is not a schema valid request.')
    #     abort(HTTPStatus.BAD_REQUEST)

    app.logger.info('Valid request: %s', str(event))

    # Add a time stamp to each event for traceability and in order to keep
    # track of lifetime.
    event_with_timestamp = {}
    event_with_timestamp["data"] = json.loads(event).copy()
    # Metadata info
    event_with_timestamp["owner"] = 'Telefonica'
    event_with_timestamp["entity_source"] = 'devo-telefonica'
    event_with_timestamp["event_name"] = 'CORE_QOS_METRIC'
    event_with_timestamp["entity_resource"] = 'telefonica-qos-metric'
    event_with_timestamp["gdpr_analytic"] = True
    event_with_timestamp["gdpr_commercial"] = False
    event_with_timestamp["createdAt"] = datetime.now()

    collection = get_collection(DB_NAME,COL_NAME)
    collection.create_index([("CELLID", pymongo.ASCENDING)],
                             expireAfterSeconds=EXPIRE_AFTER_SECONDS)

    app.logger.info('Insert info: %s', str(event_with_timestamp))

    try:
        app.logger.info('Inserting data into DB.')
        app.logger.info('QoS Insert EVENT INFO in %s in %s: %s', DB_NAME, COL_NAME, str(event_with_timestamp))
        collection.insert_one(event_with_timestamp)
    except: 
        app.logger.info('Error occurred when inserting data in DB')


    return jsonify({'success': True})


#################### NWDAF ANALYTICS CORE PREDICTIONS API #############################
@app.post('/events-core-predictions')
def core_prediction_post():
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_CORE_PRED') 
    print('MONGO_DB:', os.getenv('MONGO_EVN_DB'))
    print('MONGO_CORE PRED:', os.getenv('MONGO_EVN_COL_CORE_PRED'))
    """Register webhook events."""
    print('Start registaring event..')
    if not request.is_json:
        app.logger.info('Invalid request.It is not a json.')
        abort(HTTPStatus.BAD_REQUEST)

    event = request.get_json()

    #print('check event: ', event)

    # if not event_is_valid(event):
    #     app.logger.info('Invalid request. It is not a schema valid request.')
    #     abort(HTTPStatus.BAD_REQUEST)

    app.logger.info('Valid request: %s', str(event))

    # Add a time stamp to each event for traceability and in order to keep
    # track of lifetime.
    event_with_timestamp = {}
    event_with_timestamp["data"] = json.loads(event).copy()
    # Metadata info
    event_with_timestamp["owner"] = 'Telefonica'
    event_with_timestamp["entity_source"] = 'open5gs-telefonica'
    event_with_timestamp["event_name"] = 'CORE_NFLOAD_PREDICT'
    event_with_timestamp["entity_resource"] = 'telefonica-nfload-predict'
    event_with_timestamp["gdpr_analytic"] = True
    event_with_timestamp["gdpr_commercial"] = False
    event_with_timestamp["createdAt"] = datetime.now()

    collection = get_collection(DB_NAME,COL_NAME)
    collection.create_index([("core_category", pymongo.ASCENDING)],
                             expireAfterSeconds=EXPIRE_AFTER_SECONDS)

    app.logger.info('Insert info: %s', str(event_with_timestamp))

    try:
        app.logger.info('Inserting data into DB.')
        app.logger.info('Insert EVENT INFO in %s in %s: %s', DB_NAME, COL_NAME, str(event_with_timestamp))
        collection.insert_one(event_with_timestamp)
    except: 
        app.logger.info('Error occurred when inserting data in DB')

    return jsonify({'success': True})



#################### NWDAF QOS PREDICTIONS API #############################
@app.post('/events-devo-qos-predictions')
def qos_prediction_post():
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_QOS_PRED') #'eventsQosPredictions'
    print('MONGO_DB:', os.getenv('MONGO_EVN_DB'))
    print('MONGO_QOS PRED:', os.getenv('MONGO_EVN_COL_QOS_PRED'))
    """Register webhook events."""
    print('Start registaring event..')
    if not request.is_json:
        app.logger.info('Invalid request.It is not a json.')
        abort(HTTPStatus.BAD_REQUEST)

    event = request.get_json()

    #print('check event: ', event)

    # if not event_is_valid(event):
    #     app.logger.info('Invalid request. It is not a schema valid request.')
    #     abort(HTTPStatus.BAD_REQUEST)

    app.logger.info('Valid request: %s', str(event))

    # Add a time stamp to each event for traceability and in order to keep
    # track of lifetime.
    event_with_timestamp = {}
    event_with_timestamp["data"] = json.loads(event).copy()
    # Metadata info
    event_with_timestamp["owner"] = 'Telefonica'
    event_with_timestamp["entity_source"] = 'devo-telefonica'
    event_with_timestamp["event_name"] = 'CORE_QOS_PREDICT'
    event_with_timestamp["entity_resource"] = 'telefonica-qos-predict'
    event_with_timestamp["gdpr_analytic"] = True
    event_with_timestamp["gdpr_commercial"] = False
    event_with_timestamp["createdAt"] = datetime.now()

    collection = get_collection(DB_NAME,COL_NAME)
    collection.create_index([("nodebname", pymongo.ASCENDING)],
                             expireAfterSeconds=EXPIRE_AFTER_SECONDS)

    app.logger.info('Insert info: %s', str(event_with_timestamp))

    try:
        app.logger.info('Inserting data into DB.')
        app.logger.info('QoS Insert EVENT INFO in %s in %s: %s', DB_NAME, COL_NAME, str(event_with_timestamp))
        collection.insert_one(event_with_timestamp)
    except: 
        app.logger.info('Error occurred when inserting data in DB')


    return jsonify({'success': True})


##################### CLEAR COLLECTIONS ###############################

# CLEAR CORE EVENT COLLECTION
@app.post('/events-devo-core-analytics/clear')
def nwdaf_discovery_clear_core_ana_post():
    """Clear all webhook events."""
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_CORE_ANA') 

    get_collection(DB_NAME,COL_NAME).drop()

    return jsonify({'success': True})

@app.post('/events-devo-core-predictions/clear')
def nwdaf_discovery_clear_core_pred_post():
    """Clear all webhook events."""
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_CORE_PRED') 

    get_collection(DB_NAME,COL_NAME).drop()

    return jsonify({'success': True})

# CLEAR QOS EVENT COLLECTION
@app.post('/events-devo-qos-analytics/clear')
def nwdaf_nokia_clear_qos_ana_post():
    """Clear all webhook events."""
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_QOS_ANA') 

    get_collection(DB_NAME,COL_NAME).drop()

    return jsonify({'success': True})

@app.post('/events-devo-qos-predictions/clear')
def nwdaf_discovery_clear_qos_pred_post():
    """Clear all webhook events."""
    DB_NAME=os.getenv('MONGO_EVN_DB')
    COL_NAME=os.getenv('MONGO_EVN_COL_QOS_PRED') 

    get_collection('eventsDB','nwdafDiscoveryAnalytics').drop()

    return jsonify({'success': True})

# CLEAR EVENT INPUT
@app.post('/events/clear')
def clear_post():
    """Clear all webhook events."""
    DB_NAME=os.getenv('MONGO_EVN_DB')

    get_collection(DB_NAME,'events').drop()

    return jsonify({'success': True})
