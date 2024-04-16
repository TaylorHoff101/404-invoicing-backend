from flask import jsonify, abort, send_file
from werkzeug.utils import secure_filename
import os


def downloaded_file(username):
    # find the directory of file that username has
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401

    user_dir = os.path.join('uploads', secure_filename(username))
    if not os.path.exists(user_dir):
        abort(400, "User has not uploaded any files")

    # check whether the file is xml type
    xml_files = [f for f in os.listdir(user_dir) if f.endswith('.xml')]
    if not xml_files:
        abort(400, "User has not uploaded any XML files")

    xml_file_path = os.path.join(user_dir, xml_files[0])

    return send_file(xml_file_path, as_attachment=True)
