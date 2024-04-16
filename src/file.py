from werkzeug.utils import secure_filename
from flask import jsonify
import os


def delete_file():
    temp_dir = 'temp_uploads.xml'
    # get the current directory
    curr_dir = os.path.dirname(__file__)
    # place the file into the current directory
    final_dir = os.path.join(curr_dir, temp_dir)
    # save the file into the current folder
    os.remove(final_dir)

    return jsonify({'message': 'File successfully removed'})


def delete_user_file():
    temp_dir = 'temp_uploads_user.xml'

    # get the current directory
    curr_dir = os.path.dirname(__file__)

    # place the file into the current directory
    final_dir = os.path.join(curr_dir, temp_dir)

    # save the file into the current folder
    os.remove(final_dir)

    return jsonify({'message': 'File successfully removed'})


def delete_file_for_user(username):

    if not username:
        return jsonify({'error': 'Not authenticated'}), 401

    user_dir = os.path.join('uploads', secure_filename(username))

    try:
        # Assuming there's only one file per user
        files = os.listdir(user_dir)
        for file in files:
            os.remove(os.path.join(user_dir, file))
        # Optionally, you can remove the user's directory after clearing the files
        os.rmdir(user_dir)
        return jsonify({'message': 'User files deleted successfully'}), 200
    except OSError as e:
        return jsonify({'error': str(e)}), 500
