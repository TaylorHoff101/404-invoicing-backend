from flask import request, jsonify, session
import hashlib
import os
import json


def register_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check password criteria
    check = password_check(password)
    if check:
        return check

    # Load user data
    data = load_user_data()

    # Check if username already exists
    if username in data:
        return jsonify({'error': 'Username already exists'}), 409

    # Hash the password
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Add the new user to the data
    data[username] = {'password': hashed_password}

    # Save user data
    save_user_data(data)

    return jsonify({'success': f'User {username} registered successfully'}), 201


def validate_login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Username is required'}), 400
      # Load user data
    data = load_user_data()

    # Check if username exists and password matches
    if username in data and data[username]['password'] == hashlib.sha256(password.encode('utf-8')).hexdigest():
        session['username'] = username
        save_user_data(data)
        return jsonify({'success': f"User {session['username']} logged in"}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

def load_user_data():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as json_file:
            return json.load(json_file)
    else:
        return {}

def save_user_data(data):
    with open('users.json', 'w') as save_file:
        json.dump(data, save_file)


def password_check(passwd):
    SpecialSym =['$', '@', '#', '%']

    if len(passwd) < 6:
        return jsonify({'error': 'length should be at least 6'}), 400

    if len(passwd) > 20:
        return jsonify({'error': 'length should be not be greater than 20'}), 400

    if not any(char.isdigit() for char in passwd):
        return jsonify({'error': 'Password should have at least one numeral'}), 400

    if not any(char.isupper() for char in passwd):
        return jsonify({'error': 'Password should have at least one uppercase letter'}), 400

    if not any(char.islower() for char in passwd):
        return jsonify({'error': 'Password should have at least one lowercase letter'}), 400

    if not any(char in SpecialSym for char in passwd):
        return jsonify({'error': 'Password should have at least one of the symbols $@#'}), 400
