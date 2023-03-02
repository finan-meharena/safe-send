import datetime
import json
import requests
from flask import render_template,redirect,request

from app import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"


