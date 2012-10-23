"""
Copyright (C) 2012 Mark Boorer

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
"""


from copy import deepcopy
from pygraph.classes.digraph import digraph as Digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms.sorting import topological_sorting
import pygraph.readwrite.dot
from grafpy import Node

class DAG(object):
	def __init__(self):
		self.digraph = Digraph()
		
		# A map of human readable labels to help users
		self.nodemap = {} # {'label' : <node object> }
		
		# A dictionary of nodes evaluated data. Values will be None if node needs evaluating
		self.cache = {} # {'label' : {data} }
		
		# A dictionary of errors associated with each node
		self.errors = {} # {'label' : [ "errors"]}
		
		# a set of updated nodes since last DAG evaluation
		self.updated = set() # ['labels']
	
	def write(self, location):
		import pickle
		fp = open(location, 'wb')
		pickle.dump(self, fp, protocol=2)
		fp.close()
		
	def get_dot(self):
		'Return string of dotgraph representation'
		d = pygraph.readwrite.dot.write(self.digraph)
		return d
	
	def write_dot(self, filename):
		dot = self.get_dot()
		fh = open(filename, 'w')
		fh.write(dot)
		fh.close()

		
		
	def get_dic(self):
		'Return a dictionary representation of digraph'
		st = breadth_first_search(self.digraph)[0]
		return st
	
	def get_edges(self):
		edges = self.digraph.edges()
		return edges
	
	def add_node(self, node, label):
		'Add a node to the DAG'
		
		# Check for node instance
		if not isinstance(node, Node):
			raise Exception("Provided node must be of type 'Node'")
		
		# Check if node object already in graph
		if self.nodemap.has_key(label):
			if node == self.nodemap[label]:
				# No need to re-enter the same object
				return
			else:
				raise Exception("Label '%s' already in use" % label)
			
		elif node in self.nodemap.values():
				raise Exception("Node already exists in DAG with label '%s'" % self.get_label_from_node(node))
		
		# Register DAG for node notifications
		node.register(self)
		
		# Add node to graph
		self.nodemap[label] = node
		self.cache[label] = None
		self.errors[label] = []
		self.digraph.add_node(label)
		
		
		
	def del_node(self, label):
		'Remove a node from the DAG by label'
		if not isinstance(label, str):
			raise Exception("Provided label not of type 'str'")
		
		if self.nodemap.has_key(label):
			node = self.nodemap[label]
			
			# Unregister DAG from node
			node.unregister(self)
			
			# Remove node
			self.digraph.del_node(label)
			del self.nodemap[label]
			
			if self.cache.has_key(label):
				del self.cache[label]
			if self.errors.has_key(label):
				del self.errors[label]
			if label in self.updated:
				self.updated.remove(label) 
		
		else:
			raise Exception("Provided label not found in DAG")
	
		
		
	def add_edge(self, parent_label, child_label):
		'Add an edge to DAG between parent_label and child_label'
		
		if not self.nodemap.has_key(parent_label):
			raise Exception("Provided parent label not found in DAG")
		elif not self.nodemap.has_key(child_label):
			raise Exception("Provided child label not found in DAG")
				
		
		edge = (parent_label, child_label)
		self.digraph.add_edge(edge)
		
		
		
	def del_edge(self, parent_label, child_label):
		'Remove an edge from DAG between parent_label and child_label'
		
		if not self.nodemap.has_key(parent_label):
			raise Exception("Provided parent label not found in DAG")
		elif not self.nodemap.has_key(child_label):
			raise Exception("Provided child label not found in DAG")
		
		edge = (parent_label, child_label)
		self.digraph.del_edge(edge)
		
		
		
	def get_nodes_from_labels(self, labels):
		if isinstance(labels, list):
			newlist = []
			for label in labels:
				node = self.get_node_from_label(label)
				newlist.append(node)
		elif isinstance(labels, str):
			node = self.get_node_from_label(label)
			return node
				
	
	def evaluate_dag(self):
		'Force every node to be evaluated'
		# First invalidate all changed caches
		self._invalidate_caches()
		
		# Then call update on every node
		sg = topological_sorting(self.digraph) # sorted graph
		for label in sg:
			self._update_node(label)

			
		
	def evaluate_node(self, label):
		'Return the correct data for a node after evaluation'
		
		if isinstance(label, Node):
			label = self.get_label_from_node(label)
		elif not isinstance(label, str):
			raise Exception("Provided label not of type 'str' or 'Node'")
		
		if not self.nodemap.has_key(label):
			raise Exception("Could not find node with label '%s' in DAG" % label)
		
		# first we invalidate the caches for nodes that have changed
		self._invalidate_caches()
		
		# then update the node
		self._update_node(label)
		
		# 
		if self.cache[label] == None:
			errors = self.errors[label]
			plural = ""
			if len(errors) > 1:
				plural = "s"
			msg = "Node '%s' could not be evaluated due to the following error%s:\n" % (label, plural)
			for error in errors:
				msg += "\t - %s\n" % error 
			raise Exception(msg)
		else:
			return self.cache[label]
		
	
	
	def mark_updated(self, node):
		'Method to add a node to the invalidated list - so it can be checked on next execution'
		label = self.get_label_from_node(node)
		self.updated.add(label)
		
	
	
	def _invalidate_caches(self):
		'invalidate the downstream caches of updated nodes'
		
		if len(self.updated) == 0:
			return
			
		# Sort the nodes in worklist and remove duplicates
		sg = topological_sorting(self.digraph) # sorted graph
		
		worklist = []
		# insert nodes into worklist in sorted order
		for node in sg:
			if node in self.updated:
				worklist.append(node)
		self.updated.clear()
		
		# iterate through worklist
		while worklist:
			node = worklist.pop() # one item at a time
			downstream = breadth_first_search(self.digraph, root=node)[1] # get all downstream labels
			for n in downstream:
				if n in worklist:
					# remove labels that will already be done
					worklist.remove(n)
				# remove cache entries
				self.cache[n] = None
				
		
			
	def _update_node(self, label, rgraph=None):
		'Recursively updates nodes up the graph'
		
		# If cache already exists, this node is ok
		if self.cache[label] != None:
			return
		
		# reverse digraph then get parents
		if rgraph is None:
			rgraph = self.digraph.reverse()
		parents = rgraph.neighbors(label)
		
		# recursively evaluate all parent nodes to check if updates are required
		for i in parents:
			self._update_node(i, rgraph)
		
		# If we are here, cache needs to be generated
		
		# default state of cache entry is None
		self.cache[label] = None
		self.errors[label] = []
		
		# temp variables for final node attributes
		errors = []
		cache = {}
		
		node = self.get_node_from_label(label)
		
		while parents:
			node1 = parents.pop() # Compare one parent node against all others at a time
			if parents == []:
				# merge evaluated node1 if nothing to compare with
				c = self.cache[node1]
				if c == None:
					errors.append("Node '%s' could not be evaluated due to errors in upstream node '%s'" % (label, node1) )
					# break because the error is upstream
					break
				cache.update(c)
			else:# clear the update
				for node2 in parents:
					# get merge and conflict info
					lhs = self.cache[node1]
					if lhs == None:
						errors.append("Node '%s' could not be evaluated due to errors in upstream node '%s'" % (label, node1) )
						# break because the error is upstream
						break
					rhs = self.cache[node2]
					if rhs == None:
						errors.append("Node '%s' could not be evaluated due to errors in upstream node '%s'" % (label, node2) )
						# break because the error is upstream
						break
					merge, conflicts = self._dict_merge(lhs, rhs)
					for key in conflicts:
						# Ignore conflict if it would be overwritten anyway
						if key in node._data.keys():
							pass
						else:
							errors.append("Key conflict between '%s' and '%s' for key '%s'" % (node1, node2, key))
							# Dont break, because we can list all that is wront with this node by continuing
					# update the cache with the merge
					cache.update(merge)
					
		# finally update the cache dic with the node data
		cache.update(node._data)
		
		# If there were any erros, append them to the object
		self.errors[label] = errors
		
		# write the cache entry
		if self.errors[label] == []:
			self.cache[label] = deepcopy(cache)		
		


	def _dict_merge(self, lhs, rhs):
		'Merge two nodes data, returning the merged data and any conflicting keys'		
		merge = {} # merged dics
		conflicts = [] # list of conflicting keys
		
		for key in lhs.keys():
			# auto-merge for missing key on right-hand-side.
			if (not rhs.has_key(key)):
				merge[key] = lhs[key]
			# on collision, raise exception
			elif (lhs[key] != rhs[key]):
				conflicts.append(key)
		for key in rhs.keys():
			# auto-merge for missing key on left-hand-side.
			if (not lhs.has_key(key)):
				merge[key] = rhs[key]
		return merge, conflicts
		
		
				
	def get_nodes(self):
		'Return all node objects in DAG'
		return self.nodemap.values()
	
	def get_labels(self):
		'Return labels for all nodes in DAG'
		return self.nodemap.keys()
	
	def get_dict(self):
		'Return a dictionary of {\'label\' : <node object>}'
		return self.nodemap
	
	def get_node_from_label(self, label):
		'Return the node for given label'
		if self.nodemap.has_key(label):
			return self.nodemap[label]
		else:
			raise Exception("Could not find node in DAG with label '%s'" % label)
		
	def get_label_from_node(self, node):
		'Return the label for given node'
		for k,v in self.nodemap.iteritems():
			if v == node:
				return k
		raise Exception("Could not find node in DAG")
		
		
		
	def show(self):
		'Simple method to generate a dotgraph and render it with graphviz'
		import gv
		import os
		import time
		
		dot = self.get_dot()
		# write the dotfile out for testing
		self.write_dot('/tmp/dag.dot')
		
		# Apply the dot layout to the graph
		gvo = gv.readstring(dot) # graphviz object
		gv.layout(gvo, 'dot')
		
		# render the layout into the node attributes
		gv.render(gvo)
		
		# write to a temp file and display in default viewer
		fileout = '/tmp/out.png'
		if os.path.exists(fileout):
			os.remove(fileout)
		gv.render(gvo, 'png', fileout)
		time.sleep(1)
		os.system('xdg-open %s 2> /dev/null' % fileout)
		
		