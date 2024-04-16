from flask import Flask, request, jsonify, session
from werkzeug.utils import secure_filename
from user import User, empty_users
import os

def allowed_file(filename):
    allowed_file_type = ['xml']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_file_type


def upload_file():
    updated_file = request.files['file']

    if updated_file and allowed_file(updated_file.filename):
        temp_dir = 'temp_uploads.xml'

        curr_dir = os.path.dirname(__file__)

        final_dir = os.path.join(curr_dir, temp_dir)

        updated_file.save(final_dir)

        return jsonify({'message': 'File successfully uploaded and syntax is valid'})
    else:
        return jsonify({'error': 'File upload failed, You should upload xml file only'})


def upload_file_for_user():
    # This assumes you have a get_current_user() function that retrieves the User object from the session
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401

    updated_file = request.files['file']

    if updated_file and allowed_file(updated_file.filename):
        # Create a directory for the user if it doesn't exist
        user_dir = os.path.join(
            'uploads', secure_filename(current_user.username))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Save the file to the user's directory
        filename = secure_filename(updated_file.filename)
        file_path = os.path.join(user_dir, filename)

        updated_file.save(file_path)

        # Add file path to the user's file list
        current_user.add_file(file_path)

        updated_file.seek(0)
        final_dir = os.path.join(os.path.dirname(
            __file__), 'temp_uploads_user.xml')
        updated_file.save(final_dir)

        return jsonify({'message': 'File successfully uploaded and syntax is valid'})
    else:
        return jsonify({'error': 'File upload failed, You should upload xml file only'})

# Utility function to get the current user from the session


def get_current_user():
    username = session.get('username')
    password = session.get('password')
    # This is a simplified example. You would normally get the User object from the database.
    return User(username, password)
