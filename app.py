import os
from flask import Flask, request, jsonify
from pymongo import MongoClient, WriteConcern, ReadPreference

app = Flask(__name__)

# connection to db
client = MongoClient(os.environ["MONGODB_URI"])
db = client["ev_db"]

# collection to w&r prefrences
fast_collection = db.get_collection(
    "vehicles",
    write_concern=WriteConcern(w=1)
)

safe_collection = db.get_collection(
    "vehicles",
    write_concern=WriteConcern(w="majority")
)

primary_collection = db.get_collection(
    "vehicles",
    read_preference=ReadPreference.PRIMARY
)

secondary_collection = db.get_collection(
    "vehicles",
    read_preference=ReadPreference.SECONDARY_PREFERRED
)


@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON document required"}), 400

    output = fast_collection.insert_one(data)
    return jsonify({"inserted_id": str(output.inserted_id)})


@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON document required"}), 400

    output = safe_collection.insert_one(data)
    return jsonify({"inserted_id": str(output.inserted_id)})


@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    total = primary_collection.count_documents({"Make": "TESLA"})
    return jsonify({"count": total})


@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():
    total = secondary_collection.count_documents({"Make": "BMW"})
    return jsonify({"count": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)