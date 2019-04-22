from flask import Flask
from flask import redirect
from flask import request

app = Flask(__name__)

from app import routes
