from flask import Flask, request, jsonify, Response
from pymongo import MongoClient
import sys
sys.path.append("../")
from utils import *
from flask_cors import CORS

import datetime

app = Flask(__name__)
CORS(app)

@app.route('/create_part', methods=['POST'])
def create_part():    
    data = request.json
    mp = MongoHelper().getCollection('parts')


    part_name = data['part_name'].title()
    
    #check if already exist
    existing_part = mp.find_one({"part_name":part_name,"is_deleted":False})
    print("checkign if ", part_name.title(), " already exists")

    if existing_part:
        return jsonify({"message": "Part with part name already exists"}), 401


    part = {
        "part_name": data["part_name"].title(),
        "created_at": datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S"),
        "created_by": None,
        "is_deleted":False,
        "modified_at":None,
        "modified_by":None,
        "parent_order" : [],
        "part_configuration" : []
    }
    mp.insert_one(part)

    return jsonify({"message":"Part Created"}), 200


#when part is configured for qty,boxes for each item

@app.route('/update_part/<part_name>', methods=['PATCH'])
def update_part(part_name):
    data = request.json

    mp = MongoHelper().getCollection('parts')

    existing_part = mp.find_one({"part_name" : data['new_part'].title(), "is_deleted":False})
    if existing_part:
        return jsonify({"message": "Part with part name already exists"}), 401

    mp.update_one({"part_name": part_name}, {"$set": {"part_name": data["new_part"].title()}})

    return jsonify({"message":"Part Updated"}), 200
    


@app.route('/delete_part', methods=['DELETE'])
def delete_part():
    
    data = request.json
    part_name = data['part_name']
    
    print(" i wanna delete ", part_name)

    mp = MongoHelper().getCollection('parts')
    existing_part = mp.find_one({"part_name": part_name, "is_deleted":False})
    if not existing_part:
        return jsonify({"message": "Part not Found","extra":{}}), 401
    
    sp = MongoHelper().getCollection('session')
    session_doc = sp.find_one()
    # user_id = session_doc["user_id"]
    # part_id = existing_part['_id']
    part = {
        "modified_at": datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S"),
        "modified_by":None,
        # "modified_by":user_id,
        "is_deleted":True
    }

    mp.update_one({"part_name": part_name}, {"$set": part})

    deleted_part = mp.find_one({"part_name": part_name, "is_deleted":True})

    del deleted_part['_id']
    
    return jsonify({"message":"Part deletion Successful","extra":deleted_part}),200 


@app.route('/get_all_parts', methods=['GET'])
def get_all_parts():

    
    mp = MongoHelper().getCollection('parts')
    parts = [i for i in mp.find({"is_deleted":False})]
    new_parts = []
    for i in parts:
        del i['_id']
        new_parts.append(i)

    return jsonify({"message":"Fetch Success","extra":new_parts}),200


@app.route('/get_specific_part/<part_id>', methods=['GET'])
def get_specific_part(part_id):

    
    mp = MongoHelper().getCollection('parts')
    part = mp.find_one({"_id": ObjectId(part_id),"is_deleted":False})
    if part:
        del part['_id']
        return jsonify({"message":"Fetch Success","extra":part}),200
    else:
        return jsonify({"message":"Part not Found","extra":{}}),401
    

if __name__ == '__main__':
    app.run(debug=True,port=5001, host="0.0.0.0")