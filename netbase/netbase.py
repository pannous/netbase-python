#!/usr/bin/env PYTHONIOENCODING="utf-8" python
# -*- coding: utf-8 -*-
import codecs  # codecs.open(file, "r", "utf-8")
import json
import locale
import os
import os.path
import re
import urllib
from urllib.request import urlopen
from urllib.request import urlretrieve
# from .alle import All

# api_limit = 100000
api_limit = 400
show_ids = False # else Charité(162684)
limit_string= "%20limit%20" + str(api_limit)

from .extensions import *  # for functions

from os.path import expanduser

api = "http://netbase.pannous.com/json/"
api_all = "http://netbase.pannous.com/json/all/"
api_list = "http://netbase.pannous.com/json/short/"
api_query = "http://netbase.pannous.com/json/query/all/"

api_html = api_all.replace("json", "html")
caches_netbase_ = os.path.expanduser("~/Library/Caches/netbase/")
abstracts_netbase = os.path.expanduser("~/Library/Caches/netbase/all/")

def encode(text):
	return urllib.parse.quote( text)

def cached_names():
	return []
	# cached_files = ls(
	# 	"~/Library/Caches/netbase/").map(lambda x: x.replace(".json", "").replace(" ", "_"))
	# cached_files = cached_files.filter(lambda x: not is_number_string(x))
	# return list(set(cached_files + cache.keys() + ['OKAH']))


if not os.path.exists(abstracts_netbase):
	os.makedirs(abstracts_netbase)  # mkdir


def download(url):  # to memory
	return urlopen(url).read()


def spo(edge):
	subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
	return subject, predicate, object


def spo_ids(edge):
	sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
	return sid, pid, oid


class Edges(list):
	def show(self):
		for edge in self:
			sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			print("%d %d  %d  %s  %s  %s" %
					(sid, pid, oid, subject, predicate, object))


def get(id, name=0):
	return net.get(id or name)

class SelectProxy:
	def __init__(self, node):
		self.node=node

	def __getattr__(self, item):
		return self.node.getProperty(item)


def partner(node, edge):
	if edge['sid'] == node.id:
		return SelectProxy(net.get(edge['oid']))
	else:
		return SelectProxy(net.get(edge['sid']))

def property(node, edge):
	if edge['sid'] == node.id:
		return (edge['predicate'], Node(name=edge['object'], id=edge['oid']))
	else:
		return (edge['predicate']+" @", Node(name=edge['subject'], id=edge['sid']))


class Node:
	def __init__(self, *args, **kwargs):
		if not kwargs:
			kwargs = args[0]
		self.loaded = False
		self.id = kwargs['id']
		self.name = kwargs['name']
		self.kind= 'kind' in kwargs and kwargs['kind'] or 0
		self.image= 'image' in kwargs and kwargs['image'] or None
		self.is_abstract= self.kind == -102
		self.main_id = 'main_id' in kwargs and kwargs['main_id']
		self.topic = 'topic' in kwargs and kwargs['topic']
		if 'description' in kwargs:
			self.description = kwargs['description']
		else:
			self.description = ""
		if 'statementCount' in kwargs:
			self.count = kwargs['statementCount']
		if 'statements' in kwargs:
			self.edges = Edges(kwargs['statements'])
			self.loaded = True

	# def __dir__(self):
	# 	return list(vars(self))+list(map(lambda x: x.replace(" ", "_"), self._predicates()))

	def __str__(self):
		if not show_ids:
			return self.name
		if self.kind == -123 or self.name[0]=="+" : # number (may not be loaded yet)
			return self.name # atoi
		if self.topic:
			return "%s(%s)%s" % (self.name, self.topic, self.is_abstract and "*" or "")
		if self.name and self.id:
			return "%s(%d)%s" % (self.name, self.id, self.is_abstract and "*" or "")
		return self.name or self.id

	def __repr__(self):
		return self._short()

	def __iter__(self):
		return self.items()

	def items(self):
		pos=0
		leng = len(self.edges)
		while pos<self.count and pos< leng:
			edge = self.edges[pos]
			if not "ID" in edge['predicate']:
				yield property(self, edge)
			pos+=1
			if pos%api_limit==0:
				break
				# self.edges += self.load_edges(self.id, pos, api_limit)

	def __contains__(self, item):
		return item in self._predicates() or item in self._objects()

	def __len__(self):
		return self.count

	def __bool__(self):
		return self.id>0

	def __eq__(self, other):
		if isinstance(other, Node):
			if self.id == other.id:
				return True
		return self.name == other

	def __hash__(self):
		return self.id
	# def __add__(self, other):
	# def __radd__(self, other):

	def _short(self):
		if self.topic:
			return "{name:'%s', id:%d, topic:'%s'}" % (self.name, self.id, self.topic)
		if not self.description:
			return "{name:'%s', id:%s%d}" % (self.name, self.is_abstract and "+" or "", self.id)
		return "{name:'%s', id:%d, description:'%s'}" % (self.name, self.id, self.description)

	def _json(self):
		return "{name:'%s', id:%d, description:'%s', statements:%s}" % (self.name, self.id, self.description, self.edges)


	# todo: load more edges
	# def load_edges(self, offset, limit):
	# 	url = api_all + "%d/%d/%d" % (self.id, offset, limit)
	# 	more_edges = json.loads(download(url))
	# 	return more_edges

	def print_csv(self):
		self.edges.show()

	def show_compact(self):
		print("%s{id:%d, topic:%s, edges=[" % (self.name, self.id, self.topic))
		for edge in self.edges:
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			predicate= predicate.replace(" ","_")
			if subject == self.name or edge['sid'] == self.id:
				print(" %s:%s," % (predicate, object))
			else:
				in_predicate = "_of" in predicate or "_after" in predicate or "_by" in predicate
				in_predicate = in_predicate or "_in" in predicate or "_von" in predicate
				if in_predicate:
					print(" %s:%s," % (predicate, subject))
				else:
					print(" %s_of:%s," % (predicate, subject))
		print("]}")


	def open(self):
		if "http" in self.name:
			os.system("open " + self.name)
		else:
			os.system("open " + api_html + self.name)

	def show(self):
		if "http" in self.name:
			os.system("open " + self.name)
		print(self.show_compact())
		# print(self._json())

	def _predicates(self):
		alles = []
		for e in self.edges:
			predicate = e['predicate']
			if "ID" in predicate:
				continue
			if not predicate in alles:
				alles.append(predicate)
		return list(set(alles))


	def _objects(self):
		alles = []
		for e in self.edges:
			alles.append(e['object'])
		return list(set(alles))


	def _print_edges(self):
		for e in self.edges:
			if e['sid'] == self.id:
				print(" %s:%s" % (e['predicate'], e['object']))
			else:
				if " of" in e['predicate']:
					print(" %s: %s" %
							(e['predicate'].replace(" of", ""), e['subject']))
				else:
					print(" %s of: %s" % (e['predicate'], e['subject']))
		return self.edges

	def _map(self):
		map = {}
		for e in self.edges:
			if e['sid'] == self.id:
				map[e['predicate']] = e['object']
			else:
				if " of" in e['predicate']:
					map[e['predicate'].replace(" of", "")] = e['subject']
				else:
					map[e['predicate'] + " of"] = e['subject']
		return map

	def _load_edges(self):
		if self.loaded:
			return self.edges
		file = caches_netbase_ + str(self.id) + ".json"
		if not os.path.exists(file):
			url = api_all + str(self.id) + limit_string
			print(url)
			urlretrieve(url, file)
		# data = open(file,'rb').read()
		data = codecs.open(file, "r", "utf-8").read()
		data = json.loads(data)  #  !!!
		# data = json.loads(str(data, "UTF8"))  #  !!!
		if len(data['results']) > 0:
			result = data['results'][0]
			self.edges = Edges(result['statements'])
		else:
			self.edges = []
		self.loaded = True
		return self.edges

	def fetchProperty(self, property):
		data = json.loads(download(api_all + encode(self.name) + "." + encode(property)))
		if not "results" in data or not data["results"] or len(data["results"]) == 0:
			return None
		return Node(data["results"][0])

	# list of nodes vs getProperty single node
	def getProperties(self, property, strict=False):
		found = []
		if not self.loaded:
			self._load_edges()
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property or not strict and (property in predicate):
				if e['sid'] == self.id:
					found.append(Node(name=e['object'], id=e['oid']))
				elif not strict:
					found.append(Node(name=e['subject'], id=e['sid']))
			if not strict and property in e['object']:
				found.append(Node(name=e['object'], id=e['sid']))
		if property == 'instance':
			found.extend(self.getProperties('type', strict=True))
		try:
			if self in found:
				found.remove(self)
		except Exception as ex:
			pass
		if not found and not property.endswith("s"):
			return [self.fetchProperty(property)]

		if not found:
			return list([])
		return list(found)

	# print(found)
	# return set(found)


	def __getitem__(self, index):
		return self.getProperty(index)

	def getProperty(self, property, strict=False):
		# those where hasattr(self,property) is false!
		if property.endswith("s"):
			return self.getProperties(property[:-1], strict)
		if isinstance(property, int):
			return self.edges[property]
		if property == 'predicates':
			return self._predicates()
		if property == 'properties':
			return self._predicates()
		if property == 'keys':
			return self._predicates()
		if property == 'statements':
			return self.edges
		if property == 'net':
			return net
		if property == 'select':
			return SelectProxy(self)
		if property == 'nr':
			return locale.atoi(self.name)
		if property == 'edges':
			return self._load_edges()
		if property == 'all':
			return net._all(self.id, True, False)
		if property == 'list':
			return self._map()
		if property == 'count':
			if hasattr(self, "edges"):
					return self.edges.count(self.edges)
			return 0
		if property == 'json':
			return self._json()
		if property == 'short':
			return self._short()
		if property == 'descriptions':
			return self.description

		property = property.replace("_", " ").lower()
		# print("getProperty " + self.name+"."+ property)
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property:
				if e['sid'] == self.id:
					return Node(name=e['object'], id=e['oid'])
				elif not strict:
					return Node(name=e['subject'], id=e['sid'])
		if strict:
			return []#None
		for e in self.edges:
			if property in e['predicate'].lower(): # SUBSTRING MATCH!
				if e['oid'] == self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=e['object'], id=e['oid'])
			if not strict and property in e['object']:
				return Node(name=e['object'], id=e['sid'])
		if property == 'parent':
			return self.getProperty('superclass', strict=True) or self.getProperty('type', strict=True)
		if len(self.edges) >= api_limit or len(self.edges) >= 200:
			return self.fetchProperty(property)
		if is_plural(property):
			return self.getProperties(singular(property))

	def __getattr__(self, name):
		# print("get " + name)
		return self.getProperty(name)

	def isA(self, type):
		return self.type == type or type.lower() in self.type.name.lower()



# Node.show_edges = Node.print_csv
# Node._display = Node.show_compact
# Node._render = Node.show_compact
# Node._print = Node.show_compact


def is_plural(name):
	return name.endswith("s")  # todo


def singular(name):
	if name.endswith("ies"):
		return re.sub(r"ies$", "y", name)
	# return name.replace(r"ies$", "y")  # WTF PYTHON !
	if name.endswith("ses"):
		return re.sub(r"ses$", "s", name)
	if name.endswith("s"):
		return re.sub(r"s$", "", name)  # todo
	return name


class Netbase:
	def __init__(self):
		self.cache = {}
		self.caches = {}

	def setGerman(x):
		global api, api_list, api_all
		api = "http://de.netbase.pannous.com/json/all/"
		api_list = "http://de.netbase.pannous.com/json/short/"
		api_all = "http://de.netbase.pannous.com/json/query/all/"

	def types(self, name):
		return self._all(name, instances=False) # select(kind=...)

	# @classmethod
	# noinspection PyTypeChecker
	def _all(self, name, instances=False, deep=False, reload=False):
		if isinstance(name, int):
			n=self.get(name)
			if not n.is_abstract: return n
			else: name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.caches:
			return self.caches[name]
		file = abstracts_netbase + name + ".json"
		if reload or not os.path.exists(file):
			print(api_all + name)
			urlretrieve(api_query + name + limit_string, file)
		data = codecs.open(file, "r", "utf-8", errors='ignore').read()
		# data = open(file,'rb').read()
		# if not isinstance(data,unicode):
		# 	data=data.decode("UTF8", 'ignore')
		#  !!!  'str' object has no attribute 'decode'
		# 	FUCKING PYTHON MADNESS!!
		# http://stackoverflow.com/questions/5096776/unicode-decodeutf-8-ignore-raising-unicodeencodeerror#5096928
		try:
			# data = json.loads(data)
			data = json.loads(data)
		except Exception as ex:
			print(ex)
			os.remove(file)
			# return Node(id=-666, name="ERROR")
		nodes = list()
		for result in data["results"]:
			# print(result)
			node = Node(result)
			nodes.append(node)
			if instances:
				nodes.append(self._all(node.id, False, True, reload))
				nodes.append(node.instances)
		self.caches[name] = nodes
		return nodes

	# @classmethod
	def get(self, name, get_the=False):
		# return all(name)[0]
		if isinstance(name, int):
			name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.cache:
			node= self.cache[name]
			if not get_the or not node.is_abstract:
				return node
			if get_the and node.is_abstract and node.main_id:
				return get(node.main_id)
		# print("getThe "+name)

		file = caches_netbase_ + name + ".json"
		if not os.path.exists(file):
			print(api_all + name)
			urlretrieve(api_all + name + limit_string, file)
		data = codecs.open(file, "rb", "utf-8").read()
		data = json.loads(data)
		results = data['results']
		leng = len(results)
		if leng == 0:
			return None
		if leng == 1:
			node = Node(results[0])
			if node.is_abstract:
				if node.main_id:
					return get(node.main_id)
				# xs=node.instances
				node=node.instances[0]
		else:
			for i in range(leng):
				result = results[i] # first == 'the'
				node = Node(result)
				if not get_the or not node.is_abstract:
					break
		self.cache[name] = node
		return node

	def __dir__(self):
		return cached_names()

	def __getattr__(self, name):
		if name == "net":
			return net
		if name == "world":
			return net
		if name == "all":
			return alle  # use net.all.birds OR net.birds.all / net.bird.232.all
		# return self.all(name)
		# print("get "+name)
		return self.get(name)


class Alle(type):
	def __getattr__(self, name):
		return net._all(name, False, False)


class Alles(Netbase):
	def __getattr__(self, name):
		return net._all(name, False, False)

class The:
	def __getattr__(self, name):
		return net.get(name, get_the=True)


world = net = Netbase()
cache = net.cache
alle = Alles()
the = The()
# All.setNet(net)

def main():
	global net,the
	world = net = Netbase()
	cache = net.cache
	alle = Alles()
	the = The()
	# All.setNet(net)
	# print(the.USA)
	# print(the.USA.name)
	# print(the.USA.short)
	# print(the.USA.count)
	# print(the.USA.predicates)
	# print(the.USA.instances)

	# net.get("Berlin", get_the=True)
	Berlin = the.Berlin
	# print(Berlin.open())
	print(Berlin.population)
	print(Berlin.head)
	print(Berlin.image)
	print(Berlin.language)
	print(Berlin.contains)
	print(Berlin["Vehicles per thousand people"])
	# German district key
	assert "Charité" in Berlin
	# assert Berlin.type == "City"
	assert Berlin.type == "Million city"
	assert Berlin.isA("city")
	assert Berlin.isA("Metropolis")

	# print(Berlin.predicates)
	# for edge in Berlin.edges:
	# 	print(edge)

	# for predicate, object in Berlin:
	# 	print(predicate,":", object)

	# print(net.USA.all)
	# print(net.USA.select.country) # select proxy hack
	return

if __name__ == '__main__':
	main()
