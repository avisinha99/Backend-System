from flask import Flask, request, jsonify
from flask import abort
import jwt
import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admin@localhost:3306/Users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10), nullable=False)

    def __init__(self, username, email, password, full_name, age, gender):
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.age = age
        self.gender = gender

class KeyValueData(Base):
    __tablename__ = 'key_value_data'
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(String(200), nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

@app.route('/api/register', methods=['POST'])
def register_user():
    # Parse the request JSON
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ["username", "email", "password", "full_name"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "code": "INVALID_REQUEST",
                "message": f"Invalid request. Please provide all required fields: {', '.join(required_fields)}."
            }), 400

    # Check if the username is already taken
    if session.query(User).filter_by(username=data["username"]).first():
        return jsonify({
            "status": "error",
            "code": "USERNAME_EXISTS",
            "message": "The provided username is already taken. Please choose a different username."
        }), 409

    # Check if the email is already registered
    if session.query(User).filter_by(email=data["email"]).first():
        return jsonify({
            "status": "error",
            "code": "EMAIL_EXISTS",
            "message": "The provided email is already registered. Please use a different email address."
        }), 409

    # Validate the password
    if len(data["password"]) < 8:
        return jsonify({
            "status": "error",
            "code": "INVALID_PASSWORD",
            "message": "The provided password does not meet the requirements. Password must be at least 8 characters long."
        }), 400

    # Validate the age
    if "age" in data and (not isinstance(data["age"], int) or data["age"] < 0):
        return jsonify({
            "status": "error",
            "code": "INVALID_AGE",
            "message": "Invalid age value. Age must be a positive integer."
        }), 400

    # Gender is required
    if "gender" not in data:
        return jsonify({
            "status": "error",
            "code": "GENDER_REQUIRED",
            "message": "Gender field is required. Please specify the gender (e.g., male, female, non-binary)."
        }), 400

    # Registration successful, add the user to the database
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        full_name=data["full_name"],
        age=data.get("age"),
        gender=data["gender"]
    )
    session.add(new_user)
    session.commit()

    return jsonify({
        "status": "success",
        "message": "User successfully registered!",
        "data": {
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "age": new_user.age,
            "gender": new_user.gender
        }
    }), 200


@app.route('/api/token', methods=['POST'])
def generate_token():
    # Parse the request JSON
    data = request.get_json()

    # Check if both username and password are provided
    if "username" not in data or "password" not in data:
        return jsonify({
            "status": "error",
            "code": "MISSING_FIELDS",
            "message": "Missing fields. Please provide both username and password."
        }), 400

    # Query the database using the User model to check if the provided username and password match any registered user
    user = session.query(User).filter_by(username=data["username"], password=data["password"]).first()
    if user is None:
        return jsonify({
            "status": "error",
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid credentials. The provided username or password is incorrect."
        }), 401

    # Generate an access token using JWT
    SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  # Token expiration time (1 hour)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Return the success response with the access token
    return jsonify({
        "status": "success",
        "message": "Access token generated successfully.",
        "data": {
            "access_token": access_token,
            "expires_in": 3600
        }
    }), 200

# Sample data to store key-value pairs (you should use a database in a real-world scenario)
@app.route('/api/data', methods=['POST'])
def store_data():
    # Parse the request JSON
    data = request.get_json()

    # Check if the provided key and value are valid and not missing
    if "key" not in data or not data["key"].strip():
        return jsonify({
            "status": "error",
            "code": "INVALID_KEY",
            "message": "Invalid key. Please provide a valid key."
        }), 400

    if "value" not in data or not data["value"].strip():
        return jsonify({
            "status": "error",
            "code": "INVALID_VALUE",
            "message": "Invalid value. Please provide a valid value."
        }), 400

    # Check if the key already exists in the database
    key = data["key"]
    existing_data = session.query(KeyValueData).filter_by(key=key).first()
    if existing_data:
        return jsonify({
            "status": "error",
            "code": "KEY_EXISTS",
            "message": "The provided key already exists in the database. To update an existing key, use the update API."
        }), 409

    # Create a new instance of KeyValueData and store it in the database
    new_data = KeyValueData(key=key, value=data["value"])
    session.add(new_data)
    session.commit()

    # Return the success response
    return jsonify({
        "status": "success",
        "message": "Data stored successfully."
    }), 200



@app.route('/api/data/<string:key>', methods=['GET'])
def retrieve_data(key):
    # Query the database to check if the provided key exists
    data_entry = session.query(KeyValueData).filter_by(key=key).first()

    if data_entry is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database."
        }), 404

    # Retrieve the value associated with the provided key
    value = data_entry.value

    # Return the success response with the retrieved data
    return jsonify({
        "status": "success",
        "data": {
            "key": key,
            "value": value
        }
    }), 200



@app.route('/api/data/<string:key>', methods=['PUT'])
def update_data(key):
    # Query the database to check if the provided key exists
    data_entry = session.query(KeyValueData).filter_by(key=key).first()

    if data_entry is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database."
        }), 404

    # Parse the request JSON
    data = request.get_json()

    # Check if the provided value is valid and not missing
    if "value" not in data or not data["value"].strip():
        return jsonify({
            "status": "error",
            "code": "INVALID_VALUE",
            "message": "Invalid value. Please provide a valid value."
        }), 400

    # Update the value associated with the provided key in the database
    value = data["value"]
    data_entry.value = value
    session.commit()

    # Return the success response
    return jsonify({
        "status": "success",
        "message": "Data updated successfully."
    }), 200


@app.route('/api/data/<string:key>', methods=['DELETE'])
def delete_data(key):
    # Query the database to check if the provided key exists
    data_entry = session.query(KeyValueData).filter_by(key=key).first()

    if data_entry is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database."
        }), 404

    # Delete the key-value pair associated with the provided key from the database
    session.delete(data_entry)
    session.commit()

    # Return the success response
    return jsonify({
        "status": "success",
        "message": "Data deleted successfully."
    }), 200





if __name__ == "__main__":
    app.run(debug=True)
