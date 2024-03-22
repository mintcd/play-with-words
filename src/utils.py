import requests
from bs4 import BeautifulSoup
import json
import threading
import re
import numpy as np
from functools import reduce
from multiprocessing import Pool
from itertools import combinations
from time import time
import zipfile
import networkx as nx
import matplotlib.pyplot as plt
import csv


def print_key_structure(dictionary, indent=0):
    """
    Print the key structure of a dictionary
    """
    for key, value in dictionary.items():
        print('  ' * indent + str(key))
        if isinstance(value, dict):
            print_key_structure(value, indent + 1)

def read_json_from_zip(zip_file_path, json_file_name):
    """
    Function to read a JSON file from a ZIP archive.

    Parameters:
        zip_file_path (str): Path to the ZIP archive.
        json_file_name (str): Name of the JSON file within the ZIP archive.

    Returns:
        dict: Dictionary containing the JSON data.
    """
    try:
        # Open the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extract the JSON file from the zip archive
            with zip_ref.open(json_file_name) as json_file:
                # Read the JSON data
                json_data = json.load(json_file)
        return json_data
    except Exception as e:
        print(f"Error reading JSON from ZIP: {e}")
        return None

def split_words(text):
    pattern = r"\b\w+(?:'\w+)?\b|\w+"
    return re.findall(pattern, text)
