import mysql.connector
from flask import Flask
# from sqlalchemy import create_engine

from config import consts
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_conn = mysql.connector.connect(
    host=consts.DB_HOST,
    user=consts.DB_USER,
    password=consts.DB_PASSWORD,
    database=consts.DB_NAME,
    connect_timeout=1000,
)

# db_conn = create_engine(f'mysql+pymysql://{consts.DB_USER}:{consts.DB_PASSWORD}@{consts.DB_HOST}/{consts.DB_NAME}',
#                         pool_recycle=60 * 5, pool_pre_ping=True).raw_connection()
