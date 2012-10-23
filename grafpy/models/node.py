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

class Node(object):
	'A class to represent Nodes in our digraph'
	def __init__(self):
		# an dic to store this nodes _data
		self._data = {}
				
		# A set of dags to notify on updates
		self._dags = set()
		
		# position is None by default (used only by viewer) 
		# it is the position reported by graphviz, not clutter 
		self._position = None
		
	def register(self, dag):
		self._dags.add(dag)
		
	def unregister(self, dag):
		self._dags.remove(dag)
		
	def set_position(self, position):
		if not isinstance(position, tuple):
			raise Exception("Provided position must be a tuple (x,y)")
		if len(position) > 2:
			raise Exception("Provided position tuple must only contain 2 values")
		x = position[0]
		y = position[1]
		if not isinstance(x, float):
			raise Exception("X value in provided tuple must be a float")
		if not isinstance(y, float):
			raise Exception("Y value in provided tuple must be a float")
		self._position = (x,y)
		
	def get_position(self):
		return self._position
		
	def _notify(self):
		for dag in self._dags:
			dag.mark_updated(self)
				
	def __getitem__(self, key):
		return self._data[key]
	
	def __setitem__(self, key, val):
		self._data[key] = val
		self._notify()
	
	def __delitem__(self, key):
		del self._data[key]
		self._notify()