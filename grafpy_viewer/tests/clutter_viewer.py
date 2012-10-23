import os
import sys
import pickle
from math import pi
from optparse import OptionParser

import clutter
import gv

from fdag import DAG, Node # Needed for unpickle

ICONTRAY_WIDTH = 50

class NodeActor(clutter.Box):
	def __init__(self, label):
		layoutManager = clutter.BoxLayout()
		layoutManager.set_vertical(True)
		layoutManager.set_homogeneous(False)
		layoutManager.set_pack_start(False)

		super(NodeActor, self).__init__(layoutManager)
		
		# enable dragging
		self.set_reactive(True)
		self.add_action(clutter.DragAction())
		
		# Color for textures
		text_color = clutter.Color(255, 255, 255, 255)
		node_color = clutter.Color(180, 180, 180, 255)
		
		# Set label for node
		text = clutter.Text("Sans 12", label, text_color)
		
		# for Sans 12, every char is 10 size increments, + 1 char padding
		xlen = (len(label) * 10) + 10
		text.set_size(xlen, 30)
		
		# Set Icon for node
		icon = clutter.CairoTexture(width=20, height=20)
		context = icon.cairo_create()
		context.scale(20, 20)
		context.save()
		context.set_line_width(0.02)
		context.set_source_color(node_color)
		context.translate(0.5, 0.5)
		context.arc(0, 0, 0.4, 0, pi*2)
		context.fill_preserve()
		context.stroke()
		del(context)

		icon.set_size(20,20)
		self.add(text, icon)
		
		
class Graphview(clutter.Group):
	def __init__(self):
		super(Graphview, self).__init__()
		
		# Create the internal group that will hold the nodes
		self.group = clutter.Group()
		self.group.set_position(0,0)
		super(Graphview, self).add(self.group)
		self.set_reactive(True) # NEED TO DO THIS OTHERWISE IT WONT RECIEVE EVENTS
		
		# Make group dragable, need to make this work with middle mouse 
		self.group.add_action(clutter.DragAction())
		self.group.set_reactive(True)
				
		self.connect('button-press-event', self.on_button_press_event)
		self.connect('scroll-event', self.on_scroll_event)
		
	def add(self, *args):
		self.group.add(*args)	
		
	def reset(self):
		'Reset position and scale for self.group'
		self.group.set_anchor_point(0,0)
		self.group.set_position(0,0)
		self.group.set_scale(1.0,1.0)		
		
	def on_button_press_event (self, actor, event):
		button = event.button
		b = button
		if button == 1:
			b = "left button"
		elif button == 2:
			b = "middle button"
		elif button == 3:
			b = "right button"

		#actor = stage.get_actor_at_pos(clutter.PICK_ALL, int(event.x), int(event.y))
		try:
			(X,Y) = self.group.transform_stage_point(event.x,event.y)
		except clutter.Exception:
			return
				
		print "Event:", event.x, event.y
		print "Relative", X, Y
		print

		return True
	

		
	def on_scroll_event(self, graphview, event):
		'Event handler for mouse scroll events on graphview object'
		direction =  event.get_scroll_direction()
		
		scale = self.group.get_scale()[0]
				
		if direction == clutter.SCROLL_UP:
			scale += .1
		elif direction == clutter.SCROLL_DOWN:
			scale -= .1
			
		#bounds checking
		if scale <= 0.1:
			scale = 0.1
		
		# Get relative position of event location
		(X,Y) = self.group.transform_stage_point(event.x, event.y)
		
		# Get the current scaled size of the group
		(oldscalesizex, oldscalesizey) = self.group.get_transformed_size()
		#Initiate the scale animation
		self.group.set_scale(scale, scale)
		# Get the new scaled size of the group
		(newscalesizex, newscalesizey) = self.group.get_transformed_size()
		
		# Get the pixel difference between the old scale and the new scale
		pdifx = newscalesizex - oldscalesizex
		pdify = newscalesizey - oldscalesizey
		
		# Get the current position and size of the group
		(posx, posy) = self.group.get_position()
		(sizex, sizey) = self.group.get_size()
		
		# Calculate the final offset for the position of group
		# multiply pixel difference in scale by the ratio of relative event position vs size
		offsetx = (pdifx * (X / sizex))
		offsety = (pdify * (Y / sizey)) 
		
		# apply offset
		posx -= offsetx
		posy -= offsety
		
		# Move position of group so the event position appears to be the zoom center
		self.group.set_position(posx, posy)

		
		
		
class IconTray(clutter.Box):
	def __init__(self):
		
		icontraylayout = clutter.BoxLayout()
		icontraylayout.set_vertical(True)
		icontraylayout.set_homogeneous(False)
		icontraylayout.set_pack_start(False)

		super(IconTray, self).__init__(icontraylayout)
		self.set_position(0,0)
		self.set_color(clutter.Color(255, 255, 255, 125))
		
		
class Application(object):
	def __init__(self, dag_filepath):
		
		# Get the stage and set its size and color
		self.stage = clutter.Stage()
		self.stage.set_title("DAG viewer")
		self.stagex = 800.0
		self.stagey = 600.0
		self.stage.set_size(self.stagex, self.stagey)
		self.stage_color = clutter.Color(127, 127, 127, 255) # grey
		self.stage.set_color(self.stage_color)
		
		# Get DAG object from dagfile
		self.dagfile = dag_filepath
		self.dag = self.load_dag(self.dagfile)
		
		# Create graphviz object from dot
		dot = self.dag.get_dot()
		self.gvo = gv.readstring(dot)
			
		# Icon tray
		self.icontray = IconTray()
		self.icontray.set_size(ICONTRAY_WIDTH, self.stagey)
		self.stage.add(self.icontray)
		self.icontray.raise_top()
		
		# Graph view
		self.graphview = Graphview()
		self.graphview.set_position(ICONTRAY_WIDTH,0)
		self.graphview.set_size(self.stagex - ICONTRAY_WIDTH, self.stagey)
		self.stage.add(self.graphview)
				
		# Add nodes
		self.initialise_nodes()
		nodeActors = self.get_nodeActors()
		# Add each item from nodeactors to graphview
		self.graphview.add(*nodeActors)
		

		# Show the stage
		self.stage.connect("destroy", clutter.main_quit)
		self.stage.connect("key-press-event", self.on_key_press_event)
		self.stage.show_all()


	def load_dag(self, path):
		fh = open(path,'rb')
		dag = pickle.load(fh)
		fh.close()	
		return dag
		
		
	def initialise_nodes(self):
		# Bake in the node attributes from 'dot' layout
		gv.layout(self.gvo, 'dot')
		gv.render(self.gvo)
		
		# iterate over node attributes to get/set node positions
		# see gv.3python.pdf for more info
		# as well as https://mailman.research.att.com/pipermail/graphviz-interest/2006q1/003182.html
		n = gv.firstnode(self.gvo)
		
		#store min and max x and y
		minx = 0
		miny = 0
		maxx = None
		maxy = None
		
		# store the node label and position as reported by Dot layout
		nodepos = {} # {<node object>:(x,y)}
		
		while gv.ok(n) : # check that the iterator returned by firstnode is ok
			label = gv.nameof(n)
			
			spos = gv.getv(n,'pos').split(',') # list of strings 
			(xpos,ypos) = [float(i) for i in spos] # convert to float
			
			node = self.dag.get_node_from_label(label)
			pos = node.get_position()
			
			if pos != None:
				# Set xpos and ypos if they are already defined in node.get_position()
				(xpos,ypos) = pos				
			
			print xpos, ypos
			# set min and max values
			if minx > xpos:
				minx = xpos
			if maxx < xpos:
				maxx = xpos
			if miny > ypos:
				miny = ypos
			if maxy < ypos:
				maxy = ypos
			
			nodepos[node] = (xpos, ypos)
			
			#change node before iteration
			n = gv.nextnode(self.gvo, n)
			
		print "min", minx, miny
		print "max", maxx, maxy
			
		# Set the position in all nodes
		for node, pos in nodepos.iteritems():			
			node.set_position(pos)
									
			
		
			
	def main(self):
		clutter.main()
		
		
		
	def on_key_press_event(self, actor, event):
		#actor = stage.get_actor_at_pos(clutter.PICK_ALL, int(event.x), int(event.y))
		if event.keyval == clutter.keysyms.Home:
			self.graphview.reset()
		if event.keyval == clutter.keysyms.Escape:
			clutter.main_quit()
		return True

		
		
	def get_nodeActors(self):
		# Create NodeActors in their correct positions
		nodeActors = []
		for node in self.dag.get_nodes():
			label = self.dag.get_label_from_node(node)
	
			(xpos, ypos) = node.get_position()
			
			# Create node my dot to the stage
			dot = NodeActor(label)
			dot.set_size(100,50)
			dot.set_position(xpos, ypos)
			nodeActors.append(dot)
			
		return nodeActors





if __name__ == '__main__':
	parser = OptionParser()	
	(options, args) = parser.parse_args()
	
	if len(args) != 1:
		sys.exit("Error: Must have one DAG file as argument")
	
	'''
	dag_file = args[0]
	if not os.path.exists(dag_file):
		sys.exit("Error: No such file or directory '%s'" % dag_file)
	if os.path.isdir(dag_file):
		sys.exit("Error: '%s' is a directory, not a file" % dag_file)
	if not os.access(dag_file, os.R_OK):
		sys.exit("Error: Unable to access file '%s'" % dag_file)
	'''
	dag_file = 'dag.pkl'
	
	app = Application(dag_file)
	sys.exit(app.main())
	
	