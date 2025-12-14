from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from config.config import SystemConfig
import jwt
import datetime
from functools import wraps
app = Flask(__name__)
app.config['MYSQL_HOST'] = SystemConfig.MYSQL_HOST


mysql = MySQL(app)
app.config.from_object(SystemConfig)

