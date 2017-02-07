api = "http://netbase.pannous.com/json/all/"
api_limit = " limit 100"

import json
import extensions
try:
	from urllib2 import urlopen
except ImportError:
	from urllib.request import urlopen # py3 HELL


def download(url):  # to memory
	return urlopen(url).read()

class Edges(extensions.xlist):
	pass


class Node:

	def __init__(self,*args,**kwargs):
		# print(args)
		if not kwargs: kwargs=args[0]
		# print(kwargs)
		# self.id = args['id']
		# self.name = args['name']
		# self.statements = Edges(args['statements'])
		self.id = kwargs['id']
		self.name = kwargs['name']
		if 'statements' in kwargs:
			self.edges = Edges(kwargs['statements'])

	def __str__(self):
		return self.name or self.id

	def __repr__(self):
		return self.name + str(self.id)

	def _predicates(self):
		all=[]
		for e in self.edges:
			predicate=e['predicate']
			if not predicate in all:
				all.append(predicate)
		return all

	def _load_edges(self):
		url = api + str(self.id)
		print(url)
		data = download(url)
		data = json.loads(data.decode('utf8', 'ignore'))  # FUCK PY3 !!!
		# data = json.loads(str(data, "UTF8"))  # FUCK PY3 !!!
		result = data['results'][0]
		self.edges=Edges(result['statements'])
		return self.edges

	def getProperty(self,property):
		if property == 'predicates': return self._predicates()
		if property == 'edges': return self._load_edges()
		property= property.replace("_"," ").lower()
		# print("getProperty " + self.name+"."+ property)
		for e in self.edges:
			if e['predicate'].lower() is property:
				if e['oid'] is self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=e['object'],id=e['oid'])
		for e in self.edges:
			if property in e['predicate'].lower():
				if e['oid'] is self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=e['object'], id=e['oid'])

	def __getattr__(self, name):
		# print("get " + name)
		return self.getProperty(name)


class Netbase:
	def __init__(self):
		self.cache={}

	def getThe(self,name):
		if name in self.cache:
			return self.cache[name]
		# print("getThe "+name)
		print(api + name)
		data = download(api + name)
		data = json.loads(data.decode("UTF8", 'ignore'))  # FUCK PY3 !!!
		# data = json.loads(str(data,"UTF8"))  # TypeError: str() takes at most 1 argument (2 given) FUUUCK PY3 !!!
		# print(data)
		# print(data['results'])
		result = data['results'][0]
		# print(result)
		node=Node(result)
		self.cache[name]=node
		return node

	def __getattr__(self, name):
		# print("get "+name)
		return self.getThe(name)


def main():
	net=Netbase()
	print(net.Germany.name)
	# print(net.Germany.edges)
	print(net.Germany.predicates)
	print(net.Germany.type)
	print(net.Germany.saint)
	print(net.Germany.time_zone)
	print(net.Germany.country_code)
	# print(net.Germany.image)
	print(net.Germany.flag.image)
	print(net.Germany.born.edges)


# print(net.Germany.capital)


if __name__ == '__main__':
	main()
