import os
import requests
from dotenv import load_dotenv
from test_data import data

load_dotenv()

DATA = os.getenv("DATA_SOURCE")

def fetch_data():
    response = requests.get(DATA)
    return response.text

def fetch_local_data():
    return data