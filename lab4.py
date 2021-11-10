import bs4 as bs
import networkx as nx
import urllib.request as urllib2
import re
import matplotlib.pyplot as plt
import threading
import os
import pandas as pd
import threading, queue

q = queue.Queue()
max_threads=50
next_url=queue.Queue()
crawled_urls=[]


def get_links_from_page(url):
    # print(url)
    urllist = []
    try:
      res = urllib2.urlopen(url)
      htmlpage=res.read()
    except:
      return urllist

    try:
      page=bs.BeautifulSoup(htmlpage, "html.parser")
    except:
      return urllist

    pattern = re.compile(r"https://*.*.*/*")
    refs = page.findAll("a", href=pattern)
    for a in refs:
      try:
        link = a['href']
        # if link[:4] == 'http':
        if str(link).find("https://gazeta.ru/") != -1:
          urllist.append(link)
      except:
        pass

    # print(urllist)
    return urllist


def find_links(url_tuple,graph):
    # Crawls to a given depth using a tuple structure to tag urls with their depth
    global crawled_urls, next_url, max_depth
    url = url_tuple[0]
    depth = url_tuple[1]
    if (depth < 2) :
      links = get_links_from_page(url)
      for link in links:
        # These two lines create the graph
        graph.add_node(link)
        graph.add_edge(url,link)
        # If the link has not been crawled yet, add it in the queue with additional depth
        if link not in crawled_urls:
          next_url.put((link, depth+1))
          crawled_urls.append(link)
    return

class crawler_thread(threading.Thread):
    def __init__(self,queue,graph):
      threading.Thread.__init__(self)
      self.to_be_crawled=queue
      self.graph=graph
      while self.to_be_crawled.empty() is False:
        find_links(self.to_be_crawled.get(), self.graph)

def draw_graph(graph, graph_file_name):
	nx.draw(graph,with_labels=False)
	nx.write_dot(graph,os.cwd()+graph_file_name+'.dot')
	plt.savefig(os.cwd()+graph_file_name+'.png')

def calculatePageRank(url):
  print(str(url))
  root_url = url
  parser_flag = 'beautifulsoup'
  max_depth=2

  next_url.put((root_url,0))
  crawled_urls.append(root_url)
  ip_list=[]
  g = nx.Graph()
  g.add_node(root_url)
  thread_list = []

  for i in range(max_threads): #changed
    t=crawler_thread(next_url,g)
    t.daemon=True
    t.start()
    thread_list.append(t)

  for t in thread_list:
    t.join()

  pagerank = nx.pagerank_numpy(g, alpha=0.5, personalization=None,  weight='weight', dangling=None)
  # print(pagerank)
  pg = sorted(pagerank)
  # print(pg)
  k = 1
  for i in pg:
      if k<=10:
        print(str(i) + " " + str(pagerank.get(i)))
        k+=1

  edgeNumber = g.number_of_edges()
  nodeNumber = g.number_of_nodes()
  nodesize=[g.degree(n)*10 for n in g]
  pos=nx.spring_layout(g,iterations=20)

  nx.draw(g,with_labels=False)
  nx.draw_networkx_nodes(g,pos,node_size=nodesize,node_color='r')
  nx.draw_networkx_edges(g,pos)
  plt.figure(figsize=(5,5))
  plt.show()

  return pd.Series([pagerank.get(url), edgeNumber, nodeNumber], index=['pagerank','edges', 'nodes'])

url = 'https://pythonist.ru/'
calculatePageRank(url)