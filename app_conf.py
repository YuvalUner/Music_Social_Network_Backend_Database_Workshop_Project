import mysql.connector
from flask import Flask
from config import consts
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_conn = mysql.connector.connect(
    host=consts.DB_HOST,
    user=consts.DB_USER,
    password=consts.DB_PASSWORD,
    database=consts.DB_NAME)
