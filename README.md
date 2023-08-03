# Backend-System
# API Documentation

## Framework

The API is built using Flask, a lightweight Python web framework.

## Database Schema

The application uses a MySQL database named `Users` with two tables:
1. `users`: To store user information.
2. `key_value_data`: To store key-value pairs.

The `users` table has the following columns:
- `id`: Integer, Primary Key, Auto Increment
- `username`: String(50), Unique, Not Null
- `email`: String(100), Unique, Not Null
- `password`: String(100), Not Null
- `full_name`: String(100), Not Null
- `age`: Integer
- `gender`: String(10), Not Null

The `key_value_data` table has the following columns:
- `id`: Integer, Primary Key, Auto Increment
- `key`: String(50), Unique, Not Null
- `value`: String(200), Not Null

## Instructions to Run the Code

1. Install Python (version 3.7 or higher) on your system.
2. Install the required Python packages using the following command:pip install flask sqlalchemy mysql-connector-python
3. Create a MySQL database named `Users`.
4. Update the `SQLALCHEMY_DATABASE_URI` in `app.py` with your MySQL server configuration (username, password, host, port, and database name).
5. Run the Flask app using the following command:python app.py
6. The app will be accessible at `http://localhost:5000`.

## Instructions to Setup the Code

1. Clone the repository to your local machine
2. Navigate to the project directory:
3. Follow the "Instructions to Run the Code" section to set up the environment and run the Flask app.

## Test Scripts

The `test_scripts.py` file contains test cases for the API. To run the tests, ensure that the Flask app is running.

To execute the tests, run the following command:
python test_scripts.py


