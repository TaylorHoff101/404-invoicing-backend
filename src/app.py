from asyncio.windows_events import NULL
import logging
import sys
from flask import Flask, request, jsonify, send_file
from authentication import validate_login, register_user
from file import delete_file, delete_file_for_user, delete_user_file
from bulk_validation import upload_and_scrape_chrome
from download import downloaded_file
from user import empty_users, save_user_upload, delete_user_invoice, get_list_user_invoices, send_to_user
from upload import upload_file, upload_file_for_user
import os
import requests

app = Flask(__name__)
# create the random key for the security of session data
app.secret_key = os.urandom(24)

session_cookie_five_guys = '.eJytj0tuwzAMRK8iaB0UpKwPlTN00X0RGJJI2UGduLDsVZC7V2h7g3ZFDGcGePPQY11Sm6Xp8_tDq70ffZPW0iT6pN8WSU3Usk7qelf7qlIp3VT7fG3qs2de9OV5-muvHd9u772uU8__6nos_5y6nPrcTdqsz_t2SFdX1mftyVT0wcUqhrhmGxAwCeEgZAC8ZbbJMwaLIVCgAhLRsRBHy54zlxisc4YCAzipxGBctOAygiMe2EKMhUCSgSQDVuidwfGAJfgQXYcdjybbD43xXZe21XFfP-TePxUjCngBip3BGhDjc4wuWy6UCQhpyF5QP78AQHuOCQ.Zh57zw.EHewWexEqBUJ8N_XiobYVAhnbbo'

@app.route('/')
def home():
    return "Validate Home Page"

@app.route('/render/<invoiceId>/html', methods=['GET'])
def render_html(invoiceId):
    cookies = {'session': session_cookie_five_guys}
    response = requests.get(f'http://3.27.23.157/invoice/{invoiceId}/html', cookies=cookies)
    return response.text

@app.route('/render/<invoiceId>/json', methods=['GET'])
def render_json(invoiceId):
    cookies = {'session': session_cookie_five_guys}
    response = requests.get(f'http://3.27.23.157/invoice/{invoiceId}/json', cookies=cookies)
    return response.text

@app.route('/view/<invoiceId>', methods=['GET'])
def view_xml(invoiceId):
    cookies = {'session': session_cookie_five_guys}
    response = requests.get(f'http://3.27.23.157/invoice/{invoiceId}', cookies=cookies)
    return response.text

@app.route('/send/<invoiceId>/<type>', methods=['POST'])
def send_invoice(invoiceId, type):
    cookies = {'session': session_cookie_five_guys}
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'please provide a email'})
    if type == "xml":
        file = requests.get(f'http://3.27.23.157/invoice/{invoiceId}', cookies=cookies)
        response = send_to_user(email, type, file.text)
    elif type == "json":
        file = requests.get(f'http://3.27.23.157/invoice/{invoiceId}/json', cookies=cookies)
        response = send_to_user(email, type, file.text)
    elif type == "html":
        file = requests.get(f'http://3.27.23.157/invoice/{invoiceId}/html', cookies=cookies)
        response = send_to_user(email, type, file.text)
    else:
        return jsonify({'error': 'invalid send option'})
    return response

@app.route('/validate/login', methods=['POST'])
def login_route():
    return validate_login()

@app.route('/validate/register', methods=['POST'])
def register_route():
    return register_user()

@app.route('/validate/save', methods=['POST'])
def validate_save_user_upload():
    return save_user_upload()

@app.route('/validate/delete', methods=['DELETE'])
def validate_delete_user_upload():
    return delete_user_invoice()

@app.route('/validate/list', methods=['GET'])
def validate_get_list_user_invoices():
    return get_list_user_invoices()


@app.route('/validate', methods=['GET', 'DELETE'])
def validate_route():
    if request.method == 'GET':
        logging.info("uploading file ------------------------------------------------")
        upload_file()
        xml_file_path = "temp_uploads.xml"
        rule_set_value = "AU-NZ Peppol BIS Billing 3.0 Invoice - Australia"
        logging.info("going into webscraping ------------------------------------------------")
        upload_and_scrape_chrome(xml_file_path, rule_set_value)
        with open('validation.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        return html_content

    elif request.method == 'DELETE':
        return delete_file()

    else:
        # If some other method is received
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/validate/user', methods=['POST', 'GET', 'DELETE'])
def validate_user_route():
    if request.method == 'POST':
        return upload_file_for_user()

    elif request.method == 'GET':
        xml_file_path = "temp_uploads_user.xml"
        rule_set_value = "AU-NZ Peppol BIS Billing 3.0 Invoice - Australia"
        upload_and_scrape_chrome(xml_file_path, rule_set_value)
        return send_file("validation.html", as_attachment=True)

    elif request.method == 'DELETE':
        return delete_user_file()

    else:
        # If some other method is received
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/validate/user/<username>/downloads', methods=['GET'])
def get_downloaded(username):
    return downloaded_file(username)


@app.route('/validate/user/<username>/downloads', methods=['DELETE'])
def delete_downloaded(username):
    return delete_file_for_user(username)


if __name__ == '__main__':
    empty_users()
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
