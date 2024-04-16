import shutil
from flask import request, jsonify, session

import json
import os
import smtplib
import ssl
from email.message import EmailMessage

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.files = []

    def add_file(self, file_path):
        self.files.append(file_path)

    def get_files(self):
        return self.files

    def remove_file(self, file_path):

        # Remove the file if it exists in the files list
        if file_path in self.files:
            self.files.remove(file_path)


def empty_users():
    shutil.rmtree("uploads", ignore_errors=True)

def save_user_upload():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    else:
        data = {}

    invoiceId = request.json.get('invoiceId')
    username = request.json.get('username')

    if username in data:
        data[username]['invoices'].append(invoiceId)
        data[username]['invoices'] = list(set(data[username]['invoices']))
    else:
        data[username] = {'invoices': [invoiceId]}

    with open('data.json', 'w') as save_file:
        json.dump(data, save_file)

    return jsonify({'success': f'uploaded invoice {invoiceId} to user {username}'}), 200


def delete_user_invoice():
    invoiceId = request.json.get('invoiceId')
    username = request.json.get('username')
    if os.path.exists('data.json'):
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    else:
        return jsonify({'error': f"InvoiceId {invoiceId} doesn't exist for {username}"}), 400

    if username in data:
        data[username]['invoices'] = list(set(data[username]['invoices']))
        if invoiceId in data[username]['invoices']:
            data[username]['invoices'].remove(invoiceId)
            if len(data[username]['invoices']) == 0:
                del data[username]
        else:
            return jsonify({'error': f"InvoiceId {invoiceId} doesn't exist for {username}"}), 400
    else:
        return jsonify({'error': f"InvoiceId {invoiceId} doesn't exist for {username}"}), 400

    with open('data.json', 'w') as save_file:
        json.dump(data, save_file)

    return jsonify({'success': f'deleted invoice {invoiceId} for {username}'}), 200

def get_list_user_invoices():
    username = request.json.get('username')
    if os.path.exists('data.json'):
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    else:
        return jsonify({'error': f"No invoices found for for {username}"}), 400

    if username in data:
        return data[username]
    else:
        return jsonify({'error': f"No invoices found for for {username}"}), 400

def send_to_user(email, type, file):
    email_sender = "taylorhoff101@gmail.com"
    email_password = "vavc faft nixe prmb"
    email_receiver = email
    subject = "404-Invoicing Invoice"
    body = "Please find attached your invoice.\n" + file

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    email_sent = False

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        try:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            email_sent = True
        except Exception as e:
            return jsonify({'error': "An error occurred while sending the email:"})
    if not email_sent:
        if type == "xml":
            return jsonify({'error': f'failed to send xml invoice send to {email}'})
        elif type == "json":
            return jsonify({'error': f'failed to send json invoice send to {email}'})
        elif type == "html":
            return jsonify({'error': f'failed to send html invoice send to {email}'})
    else:
        if type == "xml":
            return jsonify({'success': f'xml invoice send to {email}'})
        elif type == "json":
            return jsonify({'success': f'json invoice send to {email}'})
        elif type == "html":
            return jsonify({'success': f'html invoice send to {email}'})