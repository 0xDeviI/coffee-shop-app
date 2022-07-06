"""
Name: coffee-shop-app
File: server.py
Author: Armin Asefi
Data:   7/6/2022, 7:41:33 PM
File description: This file is main server file that manages the server.
"""

from datetime import timedelta
import json
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_mysqldb import MySQL
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, verify_jwt_in_request
from config import *
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

mySql = MySQL(app)
app.config["JWT_SECRET_KEY"] = """/RhCT6gsI9URVoGLkHF6TNGMFFIFrmQUvU9WMbpcBjRIVGsMXZMEXSsrCQgSjAPS7T5CQufZ7/59apa77bi2Ns0K0cvwY2mIyRrYpKX/+IjDVx2siTRPL28ZlAOrGOWDCBh3KVBau185+Yo+GztA/FmpQ6DYdLGS2Sp5mU2Eljm8sZa2/eB/ONCJnMsB5mjhiU/UIIj3haUGGprGLOwyctLe2qajWrAPR7kt7KCMYVtpfF+u5v5oQoWiHKqrg5VqUaJMP9lq+fefJlQRuak8ptvjWHvvhl1wH5Hj4rvnTg9pSJT1aGdeafobEqxrRkmVg10CdxMptO53ztj5uteUFQ=="""
jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Hello, World!'

#--------#  Users  #--------#
@app.route('/api/v1/user', methods=['POST'])
def add_user():
    username = request.json['username']
    password = hashlib.sha256(request.json['password'].encode('utf-8')).hexdigest()
    name = request.json['name']
    address = request.json['address']
    phone = request.json['phone']
    connectionCursor = mySql.connection.cursor()
    connectionCursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    
    if connectionCursor.fetchone():
        return jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
    else:
        connectionCursor.execute("INSERT INTO users (username, password, name, address, phone) VALUES (%s, %s, %s, %s, %s)", (username, password, name, address, phone))
        mySql.connection.commit()
        return jsonify({
            'status': 'success',
            'message': 'User added successfully'
        })

@app.route('/api/v1/user/login', methods=['POST'])
def login():
    username = request.json['username']
    password = hashlib.sha256(request.json['password'].encode('utf-8')).hexdigest()
    connectionCursor = mySql.connection.cursor()
    connectionCursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
    data_fetched = connectionCursor.fetchone()
    if data_fetched:
        user = {
            'id': data_fetched[0],
            'username': username,
            'name': data_fetched[1],
            'address': data_fetched[4],
            'phone': data_fetched[5]
        }
        access_token = create_access_token(identity=user, expires_delta=timedelta(days=30))
        return jsonify({
            'status': 'success',
            'message': 'User logged in successfully',
            'access_token': access_token
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Bad credentials'
        })

@jwt_required(optional=False)
@app.route('/api/v1/user', methods=['PUT'])
def edit_user():
    verify_jwt_in_request()
    user_id = get_jwt_identity()['id']
    name = request.json['name']
    address = request.json['address']
    phone = request.json['phone']
    connectionCursor = mySql.connection.cursor()
    connectionCursor.execute(f"UPDATE users SET name = '{name}', address = '{address}', phone = '{phone}' WHERE id = '{user_id}'")
    mySql.connection.commit()
    return jsonify({
        'status': 'success',
        'message': 'User edited successfully'
    })
#------------------------------#

#--------#  Coffees  #--------#
@app.route('/api/v1/coffee', methods=['GET'])
def get_coffee():
    verify_jwt_in_request()
    connectionCursor = mySql.connection.cursor()
    connectionCursor.execute("SELECT * FROM coffees")
    _coffees = connectionCursor.fetchall()
    coffees = []
    BASE_ADDRESS = f'{request.host_url}coffee/catalog/'
    for coffee in _coffees:
        coffees.append({
            'id': coffee[0],
            'name': coffee[1],
            'description': coffee[2],
            'tags': json.loads(coffee[3]),
            'image': f"{BASE_ADDRESS}{coffee[4]}",
            'price': coffee[5]
        })
        
    return jsonify({
        'status': 'success',
        'message': 'Coffee list fetched successfully',
        'coffee': coffees
    })

@app.route('/coffee/catalog/<string:file_name>', methods=['GET'])
def get_coffee_image(file_name):
    return send_from_directory('storage/catalogs/', file_name)
#------------------------------#

#--------#  Orders  #--------#
jwt_required(optional=False)
@app.route('/api/v1/order', methods=['POST'])
def add_order():
    verify_jwt_in_request()
    user_id = get_jwt_identity()['id']
    coffee_id = request.json['coffee_id']
    quantity = request.json['quantity']
    connectionCursor = mySql.connection.cursor()
    connectionCursor.execute(f"SELECT * FROM coffees WHERE id = '{coffee_id}'")
    if connectionCursor.fetchone():
        if (quantity == 0):
            connectionCursor.execute(f"DELETE FROM orders WHERE user_id = '{user_id}' AND coffee_id = '{coffee_id}'")
            mySql.connection.commit()
            return jsonify({
                'status': 'success',
                'message': 'Order removed successfully'
            })
        else:
            connectionCursor.execute(f"SELECT * FROM orders WHERE user_id = '{user_id}' AND coffee_id = '{coffee_id}'")
            data_fetched = connectionCursor.fetchone()
            if data_fetched:
                connectionCursor.execute(f"UPDATE orders SET quantity = '{quantity}' WHERE user_id = '{user_id}' AND coffee_id = '{coffee_id}'")
                mySql.connection.commit()
                return jsonify({
                    'status': 'success',
                    'message': 'Order updated successfully'
                })
            else:
                connectionCursor.execute("INSERT INTO orders (user_id, coffee_id, quantity) VALUES (%s, %s, %s)", (user_id, coffee_id, quantity))
                mySql.connection.commit()
                return jsonify({
                    'status': 'success',
                    'message': 'Order added successfully'
                })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Coffee does not exist'
        })
#------------------------------#

app.run(debug=True, host='0.0.0.0', port=5000)