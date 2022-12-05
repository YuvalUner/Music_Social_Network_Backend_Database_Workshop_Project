import mysql.connector
from flask import Flask
from config import consts

app = Flask(__name__)

db_conn = mysql.connector.connect(
    host=consts.DB_HOST,
    user=consts.DB_USER,
    password=consts.DB_PASSWORD,
    database=consts.DB_NAME)
