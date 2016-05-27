#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Graph utilities."""

import logging
import sys
from os import path
from time import time
from glob import glob
from six.moves import range, zip, zip_longest
from six import iterkeys
from collections import defaultdict, Iterable
from multiprocessing import cpu_count
import random
import collections
from random import shuffle
from itertools import product,permutations
from scipy.io import loadmat
from scipy.sparse import issparse

from concurrent.futures import ProcessPoolExecutor

from multiprocessing import Pool
from multiprocessing import cpu_count



logger = logging.getLogger("deepwalk")


__author__ = "Bryan Perozzi"
__email__ = "bperozzi@cs.stonybrook.edu"

LOGFORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"


class Node(object):
    def __init__(self, id, name, type='user'):
        self.id = str(id)
        self.neighbors = []
        self.name = name
        self.type = type
        self.rating = {}

class Movie(object):
    def __init__(self, name):
        self.name = name
        self.director = None
        self.actors = [] 
        self.genres = []


def load_movie_data():
    # Movie data files used for building the graph
    movies_directors_filename = "./data/movie_directors.dat"
    movies_actors_filename = "./data/movie_actors.dat"
    movies_genres_filename = "./data/movie_genres.dat"
    movies_filename = "./data/movies.dat"
    
    # Load the data about the movies into a dictionary
    # The dictionary maps a movie ID to a movie object
    # Also store the unique directors, actors, and genres
    movies = {}
    with open(movies_filename, "r") as fin:
        fin.next()  # burn metadata line
        for line in fin:
            m_id, name = line.strip().split()[:2]
            movies["m"+m_id] = Movie(name)
    
    directors = set([])
    with open(movies_directors_filename, "r") as fin:
        fin.next()  # burn metadata line
        for line in fin:
            m_id, director = line.strip().split()[:2]
            if "m"+m_id in movies:
                movies["m"+m_id].director = director
            directors.add(director)
    
    actors = set([])
    with open(movies_actors_filename, "r") as fin:
        fin.next()  # burn metadata line
        for line in fin:
            m_id, actor = line.strip().split()[:2]
            if "m"+m_id in movies:
                movies["m"+m_id].actors.append(actor)
            actors.add(actor)
    
    genres = set([])
    with open(movies_genres_filename, "r") as fin:
        fin.next()  # burn metadata line
        for line in fin:
            m_id, genre = line.strip().split()
            if "m"+m_id in movies:
                movies["m"+m_id].genres.append(genre)
            genres.add(genre)

    return movies, directors, actors, genres

    
    


def records_to_graph():
    """
    Creates a graph from the datasets (hardcoded).

    A node is created for each entity: user, movie, director, genre, rating.
    The rating nodes created as one node for each possible 1-5 rating and for each movie.
        e.g., The movie 124 will lead to the nodes 124_1, 124_2, 124_3, 124_4, and 124_5.

    Edges are added based on the datasets; e.g., actor a1 was in movie m1, so an edge is created between m1 and a1.
    The movie rating node 124_2, for example, will be connected to movie 124 and any users who rated 124 as a 2.
    """
    
    # Output files for the graph
    adjlist_file = open("./out.adj", 'w')
    node_list_file = open("./nodelist.txt", 'w')

    # Load all the ratings for every user into a dictionary
    # The dictionary maps a user to a list of (movie, rating) pairs
    #   e.g., ratings[75] = [(3,1), (32,4.5), ...]
    num_ratings = 0
    ratings = collections.defaultdict(dict)
    with open("./data/train_user_ratings.dat", "r") as fin:
        fin.next()  # burn metadata line
        for line in fin:
            ls = line.strip().split("\t")
            user, movie, rating = ls[:3]
            rating = str(int(round(float(rating))))
            ratings["u"+user]["m"+movie] = rating
            num_ratings += 1
    
    movies, directors, actors, genres = load_movie_data()
    
    
    # Create nodes for the different entities in the graph
    # Keep all the nodes that you make in nodelist.
    # nodedict should map node IDs to their respective node object.
    # The node IDs should be the ID of that node in the graph; the IDs need to range from 0 to n-1 incrementally.
    #   e.g., the node u75's ID may be 12 => nodedict["u75"].id = 12
    nodelist = []
    nodedict = {}
    
    ####################################################################################################################################################################
    # Code Written for BI Project : Author : Himangshu Ranjan Borah(hborah)
    ####################################################################################################################################################################

    id_counter = 0
    # Create and add User Nodes
    for user in ratings.keys():
      current_node = Node(id = id_counter, name = user, type = "user")      
      id_counter += 1
      nodelist.append(current_node)
      nodedict[user] = current_node


    # Create and add Movie Nodes
    # Also create and add 5 ratings nodes per movie.
    for movie in movies:
      current_node = Node(id = id_counter, name = movie, type = "movie")
      id_counter += 1
      nodelist.append(current_node)
      nodedict[movie] = current_node
      # Create and add five ratings node for this movie.
      for i in xrange(1, 6):
        current_rating_node = Node(id = id_counter, name = movie + '_' + str(i), type = "rating")
        id_counter += 1
        nodelist.append(current_rating_node)
        nodedict[current_rating_node.name] = current_rating_node

    # Create Directors Nodes
    for direc in directors:
      current_node = Node(id = id_counter, name = direc, type = "directors")
      id_counter += 1
      nodelist.append(current_node)
      nodedict[direc] = current_node

    # Create actor nodes
    for actor in actors:
      current_node = Node(id = id_counter, name = actor, type = "actors")
      id_counter += 1
      nodelist.append(current_node)
      nodedict[actor] = current_node


    # Create genre nodes.
    for gne in genres:
      current_node = Node(id = id_counter, name = gne, type = "genres")
      id_counter += 1
      nodelist.append(current_node)
      nodedict[gne] = current_node 


    ####################################################################################################################################################################
    # Code Written for BI Project : Author : Himangshu Ranjan Borah(hborah)
    ####################################################################################################################################################################

    # Add edges between users and movie-rating nodes
    # Add edges between movies and directors
    # Add edges between movies and actors
    # Add edges between movies and genres
    # Add edges between movie ratings and movies
    # By "add an edge" we mean to update the neighbors list of the nodes in both directions:
    #   e.g., 
    #           director_node.neighbors.append(movie_node)
    #           movie_node.neighbors.append(director_node)
    


    ####################################################################################################################################################################
    # Code Written for BI Project : Author : Himangshu Ranjan Borah(hborah)
    ####################################################################################################################################################################

    # Draw connections from the ratings dict.
    for user_key in ratings.keys():
      current_movie_rating = ratings[user_key]
      # current_movie_rating is a dict of the movies and their corresponding ratings.
      for curr_movie in current_movie_rating.keys():
        source = user_key
        dest = curr_movie + '_' + current_movie_rating[curr_movie]
        user_node = nodedict[source]
        rating_node = nodedict[dest]
        user_node.neighbors.append(rating_node)
        rating_node.neighbors.append(user_node)


    # Parse the movies dict and fill the 3 types of connections.
    for movie_key in movies:
      current_movie_str = movies[movie_key]
      movie_node = nodedict[movie_key]
      # Do the mendatory connections to all the movies to their ratingd.
      for i in xrange(1,6):
        rating_node_for_movie = nodedict[movie_key + '_' + str(i)]
        rating_node_for_movie.neighbors.append(movie_node)
        movie_node.neighbors.append(rating_node_for_movie)
      
      # Do the director.
      if current_movie_str.director in nodedict:
        director_node = nodedict[current_movie_str.director]
        director_node.neighbors.append(movie_node)
        movie_node.neighbors.append(director_node)

      # Do the actors.
      for act in current_movie_str.actors:
        actor_node = nodedict[act]
        actor_node.neighbors.append(movie_node)
        movie_node.neighbors.append(actor_node)

      # Do the Genres.
      for gnr in  current_movie_str.genres:
        genre_node = nodedict[gnr]
        genre_node.neighbors.append(movie_node)
        movie_node.neighbors.append(genre_node)



    ####################################################################################################################################################################
    # Code Written for BI Project : Author : Himangshu Ranjan Borah(hborah)
    ####################################################################################################################################################################
    
    
    # Write out the graph
    for node in nodelist:
        node_list_file.write("%s\t%s\t%s\n" % (node.id, node.name, node.type))
        adjlist_file.write("%s " % node.id)
        for n in node.neighbors:
            adjlist_file.write("%s " % n.id)
        adjlist_file.write("\n")
    adjlist_file.close()
    node_list_file.close()
    
    return nodedict





class Graph(defaultdict):
  """Efficient basic implementation of nx `Graph' â€“ Undirected graphs with self loops"""  
  def __init__(self):
    super(Graph, self).__init__(list)

  def nodes(self):
    return self.keys()

  def adjacency_iter(self):
    return self.iteritems()

  def subgraph(self, nodes={}):
    subgraph = Graph()
    
    for n in nodes:
      if n in self:
        subgraph[n] = [x for x in self[n] if x in nodes]
        
    return subgraph

  def make_undirected(self):
  
    t0 = time()

    for v in self.keys():
      for other in self[v]:
        if v != other:
          self[other].append(v)
    
    t1 = time()
    logger.info('make_directed: added missing edges {}s'.format(t1-t0))

    self.make_consistent()
    return self

  def make_consistent(self):
    t0 = time()
    for k in iterkeys(self):
      self[k] = list(sorted(set(self[k])))
    
    t1 = time()
    logger.info('make_consistent: made consistent in {}s'.format(t1-t0))

    self.remove_self_loops()

    return self

  def remove_self_loops(self):

    removed = 0
    t0 = time()

    for x in self:
      if x in self[x]: 
        self[x].remove(x)
        removed += 1
    
    t1 = time()

    logger.info('remove_self_loops: removed {} loops in {}s'.format(removed, (t1-t0)))
    return self

  def check_self_loops(self):
    for x in self:
      for y in self[x]:
        if x == y:
          return True
    
    return False

  def has_edge(self, v1, v2):
    if v2 in self[v1] or v1 in self[v2]:
      return True
    return False

  def degree(self, nodes=None):
    if isinstance(nodes, Iterable):
      return {v:len(self[v]) for v in nodes}
    else:
      return len(self[nodes])

  def order(self):
    "Returns the number of nodes in the graph"
    return len(self)    

  def number_of_edges(self):
    "Returns the number of nodes in the graph"
    return sum([self.degree(x) for x in self.keys()])/2

  def number_of_nodes(self):
    "Returns the number of nodes in the graph"
    return order()

  def random_walk(self, path_length, alpha=0, rand=random.Random(), start=None):
    """ Returns a truncated random walk.

        path_length: Length of the random walk.
        alpha: probability of restarts.
        start: the start node of the random walk.
    """
    G = self
    if start:
      path = [start]
    else:
      # Sampling is uniform w.r.t V, and not w.r.t E
      path = [rand.choice(G.keys())]

    while len(path) < path_length:
      cur = path[-1]
      if len(G[cur]) > 0:
        if rand.random() >= alpha:
          path.append(rand.choice(G[cur]))
        else:
          path.append(path[0])
      else:
        break
    return path

# TODO add build_walks in here

def build_deepwalk_corpus(G, num_paths, path_length, alpha=0,
                      rand=random.Random(0)):
  walks = []

  nodes = list(G.nodes())
  
  for cnt in range(num_paths):
    rand.shuffle(nodes)
    for node in nodes:
      walks.append(G.random_walk(path_length, rand=rand, alpha=alpha, start=node))
  
  return walks

def build_deepwalk_corpus_iter(G, num_paths, path_length, alpha=0,
                      rand=random.Random(0)):
  walks = []

  nodes = list(G.nodes())

  for cnt in range(num_paths):
    rand.shuffle(nodes)
    for node in nodes:
      yield G.random_walk(path_length, rand=rand, alpha=alpha, start=node)


def clique(size):
    return from_adjlist(permutations(range(1,size+1)))


# http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def parse_adjacencylist(f):
  adjlist = []
  for l in f:
    if l and l[0] != "#":
      introw = [int(x) for x in l.strip().split()]
      row = [introw[0]]
      row.extend(set(sorted(introw[1:])))
      adjlist.extend([row])
  
  return adjlist

def parse_adjacencylist_unchecked(f):
  adjlist = []
  for l in f:
    if l and l[0] != "#":
      adjlist.extend([[int(x) for x in l.strip().split()]])
  
  return adjlist

def load_adjacencylist(file_, undirected=False, chunksize=10000, unchecked=True):

  if unchecked:
    parse_func = parse_adjacencylist_unchecked
    convert_func = from_adjlist_unchecked
  else:
    parse_func = parse_adjacencylist
    convert_func = from_adjlist

  adjlist = []

  t0 = time()

  with open(file_) as f:
    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
      total = 0 
      for idx, adj_chunk in enumerate(executor.map(parse_func, grouper(int(chunksize), f))):
          adjlist.extend(adj_chunk)
          total += len(adj_chunk)
  
  t1 = time()

  logger.info('Parsed {} edges with {} chunks in {}s'.format(total, idx, t1-t0))

  t0 = time()
  G = convert_func(adjlist)
  t1 = time()

  logger.info('Converted edges to graph in {}s'.format(t1-t0))

  if undirected:
    t0 = time()
    G = G.make_undirected()
    t1 = time()
    logger.info('Made graph undirected in {}s'.format(t1-t0))

  return G 


def load_edgelist(file_, undirected=True):
  G = Graph()
  with open(file_) as f:
    for l in f:
      x, y = l.strip().split()[:2]
      x = int(x)
      y = int(y)
      G[x].append(y)
      if undirected:
        G[y].append(x)
  
  G.make_consistent()
  return G


def load_matfile(file_, variable_name="network", undirected=True):
  mat_varables = loadmat(file_)
  mat_matrix = mat_varables[variable_name]

  return from_numpy(mat_matrix, undirected)


def from_networkx(G_input, undirected=True):
    G = Graph()

    for idx, x in enumerate(G_input.nodes_iter()):
        for y in iterkeys(G_input[x]):
            G[x].append(y)

    if undirected:
        G.make_undirected()

    return G


def from_numpy(x, undirected=True):
    G = Graph()

    if issparse(x):
        cx = x.tocoo()
        for i,j,v in zip(cx.row, cx.col, cx.data):
            G[i].append(j)
    else:
      raise Exception("Dense matrices not yet supported.")

    if undirected:
        G.make_undirected()

    G.make_consistent()
    return G


def from_adjlist(adjlist):
    G = Graph()
    
    for row in adjlist:
        node = row[0]
        neighbors = row[1:]
        G[node] = list(sorted(set(neighbors)))

    return G


def from_adjlist_unchecked(adjlist):
    G = Graph()
    
    for row in adjlist:
        node = str(row[0])
        neighbors = map(str, row[1:])
        G[node] = neighbors

    return G


