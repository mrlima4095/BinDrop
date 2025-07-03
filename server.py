#!/usr/bin/env python
# -*- coding: utf-8 -*-
# |
# Imports
# | (Flask)
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from flask import send_file
# | (Others) 
import jwt
import time
import json
import uuid
import flask
import os, re
import socket
import random
import bcrypt
import sqlite3
import requests
import threading, pytz
from random import randint
from threading import Timer
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
# |
# |
app = Flask(__name__)
CORS(app)
# |
SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")
# |
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
# |
# | (JWT Settings)
JWT_SECRET = json.load(open("server.json", "r"))['JWT_SECRET']
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 604800
# |
# SQLite3  
# | (Open Connection)
def getdb():
    conn = sqlite3.connect('mailserver.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor
# |
# JWT Tokens
# |
def gen_token(username):
    mailserver, mailcursor = getdb()
    mailcursor.execute("SELECT credentials_update FROM users WHERE username = ?", (username,))
    row = mailcursor.fetchone()
    credentials_update = row['credentials_update'] if row else None

    payload = {
        'username': username,
        'credentials_update': credentials_update,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
def get_user(token):
    if not token: return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload['username']

        mailserver, mailcursor = getdb()
        mailcursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        row = mailcursor.fetchone()

        if row is None: return None

        return username
    except (ExpiredSignatureError, InvalidTokenError): return None
# | 
# |
# PlainPost
# |
# Auth API
# | (Login)
@app.route('/api/login', methods=['POST'])
def login():
    mailserver, mailcursor = getdb()
    if not request.is_json: return jsonify({"response": "Invalid content type. Must be JSON."}), 400

    payload = request.get_json()
    username = payload.get('username')

    mailcursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = mailcursor.fetchone()

    if row and bcrypt.checkpw(payload.get('password').encode('utf-8'), row['password']):
        token = gen_token(username)
        response = make_response(jsonify({"response": "Login successful"}), 200)
        response.set_cookie('token', token, httponly=True, secure=True, samesite='Lax', max_age=60*60*24*7)

        return response
    else: return jsonify({"response": "Bad credentials"}), 401
# | (Register)
@app.route('/api/signup', methods=['POST'])
def signup():
    mailserver, mailcursor = getdb()
    if not request.is_json:
        return jsonify({"response": "Invalid content type. Must be JSON."}), 400

    payload = request.get_json()
    username = payload['username']
    password = bcrypt.hashpw(payload['password'].encode('utf-8'), bcrypt.gensalt())

    mailcursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if mailcursor.fetchone():
        return jsonify({"response": "This username is already in use."}), 409

    mailcursor.execute(
        "INSERT INTO users (username, password, coins, role, biography, credentials_update) VALUES (?, ?, 0, 'user', 'A PlainPost user', ?)",
        (username, password, datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Sao_Paulo')).isoformat())
    )
    mailserver.commit()

    token = gen_token(username)
    response = make_response(jsonify({"response": "Signup successful"}), 200)
    response.set_cookie(
        'token',
        token,
        httponly=True,
        secure=True,
        samesite='Lax',
        max_age=60*60*24*7
    )
    return response
# | 
# Status
@app.route('/api/status', methods=['GET'])
def status():
    username = get_user(request.cookies.get('token'))
    if not username: return jsonify({ "response": "Bad credentials!" }), 401

    return jsonify({ "response": username }), 200
# |
# |
# BinDrop
# | (Upload API)
@app.route('/api/drive/upload', methods=['POST'])
def drive_upload():
    username = get_user(request.cookies.get('token'))
    if not username: return jsonify({ "response": "Bad credentials!" }), 401
    
    file = request.files.get('file')
    
    file_id = str(uuid.uuid4())

    if not file or not username: return jsonify({"success": False, "response": "Bad request. File or user not found!"}), 400

    size = len(file.read())
    file.seek(0)

    if size > 100 * 1024 * 1024: return jsonify({"success": False, "response": "File is large then 100MB."}), 413

    saved_name = f"{file_id}.bin"
    path = os.path.join(UPLOAD_FOLDER, saved_name)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(path)

    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(SAO_PAULO_TZ)
    expire_time = None
    if size > 20 * 1024 * 1024: expire_time = now + timedelta(hours=5)

    mailserver, mailcursor = getdb()
    mailcursor.execute("INSERT INTO files (id, owner, original_name, saved_name, size, upload_time, expire_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (file_id, username, secure_filename(file.filename), saved_name, size, now.isoformat(), expire_time.isoformat() if expire_time else None))
    mailserver.commit()

    return jsonify({"success": True}), 200
# | (Download API)
@app.route('/api/drive/download/<file_id>', methods=['GET'])
def drive_download(file_id):
    mailserver, mailcursor = getdb()
    mailcursor.execute("SELECT original_name, saved_name FROM files WHERE id = ?", (file_id,))
    row = mailcursor.fetchone()

    if not row: return jsonify({"response": "File not found."}), 404

    original_name, saved_name = row
    path = os.path.join(UPLOAD_FOLDER, saved_name)
    return send_file(path, as_attachment=True, download_name=original_name)
@app.route('/api/drive/delete/<file_id>', methods=['DELETE'])
def drive_delete(file_id):
    username = get_user(request.cookies.get('token'))
    if not username: return jsonify({"success": False, "response": "Bad credentials!"}), 401

    mailserver, mailcursor = getdb()

    mailcursor.execute("SELECT saved_name FROM files WHERE id = ? AND owner = ?", (file_id, username))
    row = mailcursor.fetchone()

    if not row: return jsonify({"success": False, "response": "File not found or permission denied."}), 404

    saved_name = row[0]

    try: os.remove(os.path.join(UPLOAD_FOLDER, saved_name))
    except FileNotFoundError: pass

    mailcursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    mailserver.commit()

    return jsonify({"success": True}), 200
# | (View API)
@app.route('/api/drive/list', methods=['GET'])
def drive_list():
    username = get_user(request.cookies.get('token'))
    if not username: return jsonify({ "response": "Bad credentials!" }), 401
    
    mailserver, mailcursor = getdb()
    mailcursor.execute("SELECT id, original_name, size, upload_time, expire_time FROM files WHERE owner = ?", (username,))
    rows = mailcursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "file_id": row[0],
            "filename": row[1],
            "size": row[2],
            "upload_time": row[3],
            "expire_time": row[4]
        })
    return jsonify(result), 200
# |
# |
# Start API
if __name__ == '__main__':
    app.run(port = 9834, debug=True, host="127.0.0.1")
