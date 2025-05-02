from flask import Flask, jsonify, request
from flexbase_client import FlexBaseClient

app = Flask(__name__)
db = FlexBaseClient()

@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = db.get_documents("users")
        return jsonify(users)
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = db.insert_document("users", request.json)
        return jsonify(user), 201
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = db.get_document_by_id("users", user_id)
        return jsonify(user)
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    app.run(debug=True)