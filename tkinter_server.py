from flask import Flask, request, json
from utils import MongoHelper
import bisect

mongo = MongoHelper()

app = Flask(__name__)

global part_id

# Obtaining Part ID, with which is part of the name of the item collection
@app.route('/get_part_id/', methods = ['POST'])
def get_item_coll():
    data = json.loads(request.data)
    part_name = data['part_name']

    part = mongo.getCollection("parts").find_one({"part_name" : part_name})

    global part_id
    part_id = str(part['_id'])
    return {"message" : "success", "status_code" : 200}

# Adding a new item
@app.route('/add_items/', methods = ['POST'])
def update_items():
    data = json.loads(request.data)['itm_val']

    global part_id
    mongo.getCollection(part_id+"_items").update_one(
        {"item_name" : data[0]}
        , {"$set" : {"item_threshold" : data[1], "is_deleted" : False}}
        , upsert = True
    )

    return {"message" : "success", "status_code" : 200}

# Getting all the items from db
@app.route('/get_items', methods = ['GET'])
def get_items():
    global part_id
    items_coll = mongo.getCollection(part_id+"_items")
    items = items_coll.find()

    item_values = []

    for item in items:
        item_values.append((item['item_name'], item['item_threshold']))

    return {"result" : item_values, "status_code" : 200}

# Deletion of a particular item
@app.route('/delete_item/', methods = ['POST'])
def delete_item():
    data = json.loads(request.data)
    item_name = data['item']
    part_name = data['part_name']
    old_order = data['old_order']


    global part_id
    mongo.getCollection(part_id+"_items").delete_one({"item_name" : item_name})

    part_coll = mongo.getCollection("parts")
    part_config = part_coll.find_one({'part_name' : part_name})["part_configuration"]

    del_idx = []
    updated_part_config = []

    for item in part_config:
        if item["item_id"] == item_name:
            del_idx.append(item["item_sequence"])
        else:
            updated_part_config.append(item)

    print("This is the updated part config : ", updated_part_config)
    print(" ================= ")
    # print("These are the indexes that are deleted :  ", del_idx)
    del_idx.sort()

    return {"message" : "success", "del_idx" : del_idx, "status_code" : 200}

# Editing a particular item
@app.route('/edit_item/', methods = ['POST'])
def edit_item():
    data = json.loads(request.data)

    old_val = data['old_itm_val']
    new_val = data['new_itm_val']

    global part_id
    items_coll = mongo.getCollection(part_id+"_items")

    # Checking if new item name already exists
    if items_coll.find_one({"item_name" : new_val[0]}) is None:
        if new_val[0] == "": new_val[0] = old_val[0]
        if new_val[1] == "": new_val[1] = old_val[1]

        items_coll.update_one(
            {"item_name" : old_val[0]}
            , {"$set" : {"item_name" : new_val[0], "item_threshold" : new_val[1], "is_deleted" : False}}
            , upsert = True
        )

        return {"result" : new_val, "status_code" : 200}
    else:
        return {"result" : "failure", "status_code" : 400}

# Get all sequence entries 
@app.route('/get_sequence/', methods = ['POST'])
def get_sequence():
    data = json.loads(request.data)
    part_name = data['part_name']

    parts_coll = mongo.getCollection("parts")
    parts = parts_coll.find_one({"part_name" : part_name})
    try:
        parts_configs = parts["part_configuration"]
    except:
        return {"result" : "failure", "status_code" : 400}

    parent_order = parts['parent_order']
    print("This is the parent order : )", parent_order)
    parts_configs = sorted(parts_configs, key = lambda x : x["item_sequence"])

    return {"result" : parts_configs,"parent_order" : parent_order, "status_code" : 200}



# Adding new sequence entry
@app.route('/add_seq_entry/', methods=['POST'])
def add_seq_entry():
    data = json.loads(request.data)
    
    part_name = data['part_name']
    # print("This is part name : ", part_name)
    print("This is the index : ", data['sequence_index'])

    mongo.getCollection("parts").update_one(
        {"part_name" : part_name}
        # i want to push to an array called parts_configuration of the part collection
        , {"$push" : {"part_configuration" : {
            "item_id" : None
            , "item_sequence" : data['sequence_index']+1
            , "item_position" : {}
            , "item_qty" : None
            , "reference_img" : None
        }}, "$set" : {"parent_order" : data['parent_order']}}
        , upsert = True   # !!!!!!!!!!!!!!!!!!!!!!!!! FOR DEBUG !!!  REMOVE IN PROD
    )

    return {"message" : "success", "status_code" : 200}

# Updating sequence order (after dragging)
@app.route('/update_seq_order/', methods=['POST'])
def update_seq_order():
    data = json.loads(request.data)
    
    part_name = data['part_name']
    new_order = data['sequence_order']
    # print("This is part name : ", part_name)
    
    for idx in range(len(new_order)):
        mongo.getCollection("parts").update_one(
            {"part_name" : part_name}
            # i want to push to an array called parts_configuration of the part collection
            , {"$set" : {f"part_configuration.{new_order[idx]}.item_sequence" : idx+1}}
        )
        mongo.getCollection("parts").update_one(
            {"part_name" : part_name}
            # i want to push to an array called parts_configuration of the part collection
            , {"$set" : {f"parent_order" : new_order}}
        )

    return {"message" : "success", "status_code" : 200}

# Updating sequence item
@app.route('/update_seq_item/', methods=['POST'])
def update_seq_item():
    data = json.loads(request.data)
    
    part_name = data['part_name']
    selected_item = data['selected_item']
    sequence_index = data['sequence_index']
    
    print(" =================== ")
    print("I will change this index : ", sequence_index)
    print("To this value : ", selected_item)
    print(" =================== ")


    # print("This is part name : ", part_name)
    # print("selected_item is : ", data['selected_item'])
    # print("This is the index : ", data['sequence_index'])

    part_coll = mongo.getCollection("parts")
    part_config = part_coll.find_one({"part_name" : part_name})["part_configuration"]

    for idx in range(len(part_config)):
        if part_config[idx]['item_sequence'] == sequence_index+1:
            mongo.getCollection("parts").update_one(
                {"part_name" : part_name}
                # i want to push to an array called parts_configuration of the part collection
                , {"$set" : {f"part_configuration.{idx}.item_id" : selected_item}}
            )
            break

    return {"message" : "success", "status_code" : 200}

# Deleting sequence entry
@app.route('/delete_seq_entry/', methods=['POST'])
def delete_seq_item():
    data = json.loads(request.data)

    part_name = data['part_name']
    sequence_index = data['sequence_index']+1

    print("I will delete this index : )", sequence_index)

    parts_coll = mongo.getCollection("parts")

    part_config = parts_coll.find_one({"part_name" : part_name})["part_configuration"]
    print(len(part_config))
    print(part_config)

    part_config = [item for item in part_config if item["item_sequence"] != sequence_index]
    
    # Updating index of items ahead of deleted index
    for item in part_config:
        if item["item_sequence"] > sequence_index:
            item["item_sequence"]-=1

    parts_coll.update_one(
        {"part_name" : part_name}
        , {"$set" : {
            "part_configuration" : part_config
            , "parent_order" : data['parent_order']  
            }
        }
    )
    return {"message" : "success", "status_code" : 200}

# To Update the drawn bounding box coordinates for the specific item
@app.route('/update_coordinates/', methods=['POST'])
def update_coordinates():
    data = json.loads(request.data)

    part_name = data['part_name']
    new_coords = data['coord_list']
    item_name = data['item_details'][0]
    item_seq = data['item_details'][1]

    parts_coll = mongo.getCollection("parts")

    parts_coll.update_one(
        {"part_name" : part_name, "part_configuration.item_sequence": int(item_seq)+1, "part_configuration.item_id" : str(item_name)}
        , {"$set" : {
                'part_configuration.$.item_position' : new_coords
                , 'part_configuration.$.item_qty' : len(new_coords)
            }
        }
    ) 

    return {"message" : "success", "status_code" : 200}

# To update the item quantity for every sequence entry 
@app.route('/update_seq_qty/', methods=['POST'])
def update_seq_qty():
    data = json.loads(request.data)
    
    part_name = data['part_name']

    parts_coll = mongo.getCollection("parts")
    parts = parts_coll.find_one({"part_name" : part_name})

    quants = [item["item_qty"] for item in parts["part_configuration"]]

    return {"result" : quants, "status_code" : 200}

# To obtain coordinate list of selected item if it already exists
@app.route('/get_coordinates/', methods = ['POST'])
def get_coordinates():
    data = json.loads(request.data)

    part_name = data['part_name']
    item_name = data['item_details'][0]
    item_seq = data['item_details'][1]

    parts_coll = mongo.getCollection("parts")
    part_config = parts_coll.find_one({"part_name" : part_name})["part_configuration"]

    coord_list = [item['item_position'] for item in part_config if item["item_id"] == item_name and item['item_sequence'] == int(item_seq)+1]

    return {"result" : coord_list[0], "status_code" : 200}

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,threaded=True,debug=False)