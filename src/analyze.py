import json
import threading
import re
from functools import reduce
from multiprocessing import Pool
from itertools import combinations
import networkx as nx
import csv


class WordupAnalysis:
  """
  Functions to analyze the wordup list
  """

  def get_unscraped(graph):
    result = set()
    all_nodes = set()
    presented = list(graph.keys())
    for value in graph.values():
      all_nodes.update(value)

    for node in all_nodes:
      if node not in presented:
        result.add(node)
    return list(result)

  def get_graph(wordup_processed):
    """
    Generate a nx Graph from the processed wordup list.
    """
    G = nx.DiGraph()
    nodes = list()
    edges = list()
    for word_def in wordup_processed:
      nodes.append(word_def['root'].lower())
      for comp in word_def['comparisons']:
        edges.append((word_def['root'].lower(), comp.lower()))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

  def lookup(word, wordup):
    for ele in wordup:
      if ele['root'] == word.lower(): return ele
    return None

  def get_all_words(wordup):
    words = set()
    for word_def in wordup:
      words.add(word_def['root'])
      for sense in word_def['senses']:
        words.update([ele.lower() for ele in split_words(sense['de'])])
    return words

  def get_dependencies(wordup):
    """
    Find out each word defined by a set of other words.
    """
    depd = dict()
    for word_def in wordup:
        depd[word_def['root'].lower()] = set()
        for sense in word_def['senses']:
          for ele in re.findall(r'\b\w+\b', sense['de']):
              depd[word_def['root'].lower()].add(ele.lower())
    return depd

  def get_dependants(word_list, wordup):
    """
    Find out the words that are needed to define the words in word_list
    """
    result = set()
    for word_def in wordup:
      if word_def['root'] in word_list:
        for sense in word_def['senses']:
          result.update([ele.lower() for ele in re.findall(r'\b\w+\b', sense['de']) if ele.isalpha()])
    return result

  def get_dependers(word_list, wordup):
    """
    Find out the words that are defined by the words in word_list
    """
    result = set()
    for word_def in wordup:
      for sense in word_def['senses']:
        for ele in re.findall(r'\b\w+\b', sense['de']):
          if ele.lower() in word_list:
            result.add(word_def['root'])
    return result

  def get_minimal_wordlist(word_list, wordup):
    """
    Get the minimal word list needed to defined the whole wordup list
    """
    result = set()
    iter = 0

    print(f"Original list length: {len(word_list)}")

    while len(result) <= len(word_list) and iter < 20:
      result = get_dependants(word_list, wordup)
      iter += 1
      print(f"Reduced list length after {iter+1} iteration(s): {len(word_list)}")
      if word_list == result: 
        print(f"Minimalization converges!")
        break
      word_list = result 
      
    
    if len(result) > len(word_list):
      print("Dependant list is longer than last list!")


    return sorted(list(result))

  def add_to_processed(word, wordup_raw, wordup_processed):
    for word_def in wordup_raw:
      if word_def['props']['pageProps']['currentWord']['wordRoot'] == word:
        if not lookup(word.lower(), wordup_processed):
          wordup_processed.append({'root':word_def['props']['pageProps']['currentWord']['wordRoot'],
                        'senses':word_def['props']['pageProps']['senses'],
                        'comparisons':word_def['props']['pageProps']['comparisons']})
          print(f"Add {word} successfully!")
        else:
          print(f"Already there {word}")
        return wordup_processed
    print(f"Cannot add {word}!")
  return wordup_processed

class MorphemeAnalysis:
  """
  Functions for morpheme analysis
  """

  def get_morpheme_dict(path = "D:\Projects\play-with-words\data\morphemes\lookup.csv"):   
    morpheme_dict = dict()
    with open(path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            morpheme_dict[row[0]] = row[1].split(" ")
    return morpheme_dict

  def get_affix_dict(param='pre' or 'suf' or 'all', folder_path="D:\Projects\play-with-words\data\morphemes"):
    if param == 'pre':
      path = folder_path + "\prefixes.csv"
    elif param == 'suf': 
      path = folder_path + "\suffixes.csv"
    else: 
      raise TypeError("Parameter must be 'pre', 'suf' or 'all")

    result = set()
    with open(path, 'r', newline='', encoding='utf-8') as csv_file:
      csv_reader = csv.reader(csv_file)
      next(csv_reader)
      for row in csv_reader:
        result.add(row[0])
    return list(result)

  def get_root_dict():
    morpheme_dict = get_morpheme_dict()
    root_dict = dict()

    for word, morphemes in morpheme_dict.items():
      if len(morphemes) == 1:
        root_dict[word] = morphemes[0]
        continue
      
      found = False

      for morpheme in morphemes:
        if '##' not in morpheme:
          root_dict[word] = [morpheme]
          found = True
      
      if not found:
        """ Take all prefixes as roots """
        root_dict[word] = [morpheme.replace("##", "") for morpheme in morphemes if re.match(r'.*##$', morpheme)]
        
    return root_dict

  def get_minimal_root_list(minimal_word_list, morpheme_dict):
    minimal_root_list = set()
    for word in minimal_word_list:
      if word in root_dict.keys():
        minimal_root_list.update(root_dict[word])
      else:
        minimal_root_list.add(word)
        
    return sorted(list(minimal_root_list))