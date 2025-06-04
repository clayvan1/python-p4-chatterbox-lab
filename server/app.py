
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_cors import CORS # Import CORS
from sqlalchemy.exc import IntegrityError # Import IntegrityError for database errors
from datetime import datetime # Import datetime for timestamps

from models import db, Message # Import the Message model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False # Ensure JSON output is not compacted for readability

# Initialize CORS for the Flask app
CORS(app)

migrate = Migrate(app, db)

db.init_app(app) # Initialize db with the app

# --- Custom Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Resource not found"
    return make_response(jsonify({"error": message}), 404)

@app.errorhandler(400)
def bad_request(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Bad Request"
    return make_response(jsonify({"error": message}), 400)

@app.errorhandler(500)
def internal_server_error(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Internal Server Error"
    return make_response(jsonify({"error": message}), 500)

# --- API Routes ---

@app.route('/')
def home():
    return '<h1>Chatterbox API</h1>'

# GET /messages: returns an array of all messages as JSON, ordered by created_at in ascending order.
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        # Query all messages, ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        # Serialize each message object to a dictionary
        messages_data = [message.to_dict() for message in messages]
        return make_response(jsonify(messages_data), 200)
    except Exception as e:
        # Catch any exceptions during database query or serialization
        db.session.rollback() # Rollback in case of error
        return internal_server_error(str(e))

# POST /messages: creates a new message with a body and username from JSON, and returns the newly created post as JSON.
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json() # Get JSON data from the request body as the tests send JSON

    # Validate required fields
    if not data or not all(k in data for k in ('body', 'username')):
        return bad_request("Missing required fields: 'body' and 'username'")

    body = data.get('body')
    username = data.get('username')

    # Basic validation for empty strings
    if not body or not username:
        return bad_request("Body and username cannot be empty.")

    try:
        # Create a new Message instance
        new_message = Message(body=body, username=username)
        db.session.add(new_message) # Add to session
        db.session.commit() # Commit to database

        # Return new message with 201 Created status
        return make_response(jsonify(new_message.to_dict()), 201)
    except IntegrityError:
        db.session.rollback()
        # This error typically occurs if there's a unique constraint violation (not expected for this model)
        return bad_request("Failed to create message due to data integrity issue.")
    except Exception as e:
        db.session.rollback() # Rollback in case of other errors
        return internal_server_error(str(e))

# PATCH /messages/<int:id>: updates the body of the message using JSON, and returns the updated message as JSON.
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id) # Get message by ID

    # If message not found, return 404
    if not message:
        return not_found(f"Message with id {id} not found")

    data = request.get_json() # Get JSON data from the request body as the tests send JSON

    # Validate if data is provided and contains 'body'
    if not data or 'body' not in data:
        return bad_request("Missing 'body' field in request body for update")

    new_body = data.get('body')

    # Basic validation for empty string
    if not new_body:
        return bad_request("Message body cannot be empty.")

    message.body = new_body
    message.updated_at = datetime.utcnow() # Update timestamp

    try:
        db.session.add(message) # Add the modified object to the session
        db.session.commit() # Commit changes to the database
        return make_response(jsonify(message.to_dict()), 200) # Return updated message data
    except IntegrityError:
        db.session.rollback()
        return bad_request("Failed to update message due to data integrity issue.")
    except Exception as e:
        db.session.rollback() # Rollback in case of other errors
        return internal_server_error(str(e))

# DELETE /messages/<int:id>: deletes the message from the database and returns a JSON message.
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id) # Get message by ID

    # If message not found, return 404
    if not message:
        return not_found(f"Message with id {id} not found")

    try:
        db.session.delete(message) # Delete from session
        db.session.commit() # Commit to database

        # Return success message with 200 OK status
        return make_response(jsonify({"message": f"Message with id {id} successfully deleted"}), 200)
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        return internal_server_error(str(e))

if __name__ == '__main__':
    # Run the Flask app on port 5555 in debug mode
    app.run(port=5555, debug=True)
