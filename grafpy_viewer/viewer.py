import os
import sys
import pickle
import math
from optparse import OptionParser

# PyQt imports
from PyQt4 import QtCore, QtGui
from PyQt4 import uic

# Graphviz
import gv

# Qt widgets
from widgets.graphView import GraphView
from widgets.v_node import v_Node

# Grafpy classes neded for unpickle
from grafpy import DAG, Node 	

		
class MainWindow(QtGui.QMainWindow):
	'The main window of the fdag viewer'
	def __init__(self, dag_file=None):
		super(MainWindow, self).__init__()
		
		# Load the MainWindow ui from Designer UI file
		uic.loadUi("ui/viewer.ui", self)		
	
		# Add graphview object to MainWindow
		self.graphview = GraphView(self)
		layout = self.centralwidget.layout()
		layout.removeWidget(self.replaceMe)
		layout.addWidget(self.graphview)
		layout.update()
		
		
		# Set window Title
		self.setWindowTitle("DAG viewer")
		
		# Set saved state
		# To prompt user if they try to exit or load without saving
		self.saved = True
		
		# Storage of current DAG object filename
		self.dagfile = None
		
		# Storage of current DAG object
		self.dag = None
		
		# Initialise Signals
		self.initSignals()
		
		# Load the dag_file if provided
		if dag_file != None:
			self.openDAG(dag_file)
		else:
			# create an empty DAG
			self.dag = DAG()
	
	def keyPressEvent(self, event):
		key = event.key()
		
		if key == QtCore.Qt.Key_Delete:
			print "setting to unsaved"
			self.saved = False

		
		
		
	def initSignals(self):
		self.actionOpen.triggered.connect(self.onOpenDAGAction)
		self.actionSave.triggered.connect(self.onSaveDAGAction)
		self.actionSave_As.triggered.connect(self.onSaveAsDAGAction)
		self.actionExit.triggered.connect(self.onExitAction)
		self.actionReposition_nodes.triggered.connect(self.onRepositionNodesAction)
		self.actionEvaluate_Node.triggered.connect(self.onEvaluateNodeAction)
		
	def onOpenDAGAction(self):
		filename = QtGui.QFileDialog.getOpenFileName(self, caption="Open DAG", filter="DAG File (*.dag)")
		if not filename:
			return
		if not self.saved:	
			dlg = QtGui.QMessageBox(self)
			dlg.setWindowTitle("Save changes to current DAG before opening new?")
			message = "You haven't saved the current DAG. Do you want to continue opening and lose all unsaved changes?"
			dlg.setText(message)
			dlg.setIcon(QtGui.QMessageBox.Warning)
			
			save = dlg.addButton("Save", QtGui.QMessageBox.AcceptRole)
			nosave = dlg.addButton("Continue without saving", QtGui.QMessageBox.RejectRole)
			cancel = dlg.addButton(QtGui.QMessageBox.Cancel)
			
			# Display the dialog and get reply
			dlg.exec_()
			reply = dlg.clickedButton()
			
			if reply == save:
				i = self.onSaveDAGAction()
				# return if user cancelled save dialog
				if i == False:
					QtGui.QMessageBox.information(self, "Operation cancelled","Opening operation cancelled due to requested save operation being cancelled", QtGui.QMessageBox.Ok)
					return False
			elif reply == cancel:
				print "cancel"
				return
		
		#Open the file
		self.openDAG(filename)
		
		
	def openDAG(self, filename):
		fh = open(str(filename), 'rb')
		dag = pickle.load(fh)
		fh.close()
		
		#Store the dagfile name
		self.dagfile = filename
		
		# Store the unpickled dag object
		self.dag = dag
		
		# File is still the same as on disk, so set it as saved
		self.saved = True
		
		# Set the window title
		self.setWindowTitle("DAG viewer - %s" % self.dagfile)
		
		# Clear the current GraphView
		self.graphview.scene().clear()
		
		# Add nodes from dag
		self._getNodesFromDAG()
		
	def _getNodesFromDAG(self):
		# Get the dotfile from the DAG
		dot = self.dag.get_dot()
		gvo = gv.readstring(dot)
		
		# Bake in the node attributes from 'dot' layout
		gv.layout(gvo, 'dot')
		gv.render(gvo)
		
		# iterate over node attributes to get/set node positions
		# see gv.3python.pdf for more info
		# as well as https://mailman.research.att.com/pipermail/graphviz-interest/2006q1/003182.html
		n = gv.firstnode(gvo)
		
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
			n = gv.nextnode(gvo, n)
						
		# Set the position in all nodes and add them to the graph
		for node, pos in nodepos.iteritems():			
			node.set_position(pos)
			label = self.dag.get_label_from_node(node)
			v_node = v_Node(label)
			v_node.setPos(*pos)
			self.graphview.add(v_node)
			
		bounding = self.graphview.scene().itemsBoundingRect()
		#self.graphview.fitInView(bounding, QtCore.Qt.IgnoreAspectRatio)
		self.graphview.centerOn(bounding.center())
			
	
		
	def onSaveDAGAction(self):
		if not self.dagfile:
			# Prompt for path to save
			filename = QtGui.QFileDialog.getSaveFileName(self, caption="Save DAG", filter="DAG File (*.dag)")
			if not filename:
				return False
			self.dagfile = str(filename)
		self.saveDAG()
		return True
		
	def saveDAG(self):
		'Overwrite the current self.dagfile location with self.dag'
		self.dag.write(self.dagfile)
	
	def onSaveAsDAGAction(self):
		print "save as"
	
	def onExitAction(self):
		self.destroy()
		
	def onRepositionNodesAction(self):
		print "reposition"
	
	def onEvaluateNodeAction(self):
		print "evaluate"

	
	
		
class Application(object):
	def __init__(self, dag_filepath):
		
		app = QtGui.QApplication(sys.argv)
		mainWindow = MainWindow(dag_filepath)
		mainWindow.show()
		
		sys.exit(app.exec_())
		
		


if __name__ == '__main__':
	parser = OptionParser()	
	(options, args) = parser.parse_args()
	
	dag_file = None
	
	if len(args) > 1:
		sys.exit("Error: Can only have one DAG file as argument")
	
	if len(args) == 1:
		dag_file = args[0]
		if not os.path.exists(dag_file):
			sys.exit("Error: No such file or directory '%s'" % dag_file)
		if os.path.isdir(dag_file):
			sys.exit("Error: '%s' is a directory, not a file" % dag_file)
		if not os.access(dag_file, os.R_OK):
			sys.exit("Error: Unable to access file '%s'" % dag_file)
			
	app = Application(dag_file)
	
	
	
	
	
	