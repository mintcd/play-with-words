import requests
from bs4 import BeautifulSoup
import json
import threading
import re
import numpy as np
from functools import reduce
from multiprocessing import Pool
from itertools import combinations


class WordupScrape:
  """
  Scrape words from the Wordup dictionary
  """
  def scrape_word(word):
    if " " in word:
      search_for = word.replace(" ", "-")
    elif "-" in word:
      search_for = word.replace("-", "3")
    else:
      search_for = word
    url = f"https://www.wordupapp.co/dictionary/{search_for}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        json_tag = soup.find('script', {'type': 'application/json'})

        if json_tag:
            json_data = json.loads(json_tag.text)
            print(f"Scraped {search_for} successfully!")
            return json_data

        else:
            print(f"No tag with type='application/json' of {search_for}.")
    else:
        print(f"Failed to retrieve {search_for}")


  def scrape_thread(num, word_list, scraped_words):
    """A thread to scrape words from a list.
      Parameters: 
        num (int): the thread will scrape word of index divisible by num in word_list
        word_list: (list[str])
        scraped_words: global variable for scraped words of the threads, initialized as list()"""
    length = len(word_list)
    total = 0
    for i in range(length):
      if i % num_threads == num:
        search_for = word_list[i].lower().replace(" ", "-")
        url = f"https://www.wordupapp.co/dictionary/{search_for}"
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
          soup = BeautifulSoup(response.text, 'html.parser')
          json_tag = soup.find('script', {'type': 'application/json'})

          if json_tag:
            json_data = json.loads(json_tag.text)
            scraped_words.append(json_data)

            total += 1
            if total % 100 == 0:
                print(f"Thread {i} reached {total} words")
          else:
            print(f"No tag with type='application/json' of {search_for}.")
        else:
          print(f"Failed to retrieve {search_for}")

  def get_processed_wordup(wordup_raw):
    return [{'root':word['props']['pageProps']['currentWord']['wordRoot'],
                     'senses':word['props']['pageProps']['senses'],
                     'comparisons':word['props']['pageProps']['comparisons']}
                    for word in wordup_raw]