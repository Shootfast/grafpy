from PyQt4 import QtCore, QtGui


class GraphView(QtGui.QGraphicsView):
	'The QGraphicsView object to view an FDAG node graph'
	def __init__(self, parent):
		super(GraphView, self).__init__(parent)
		
		# Hints for the QGraphicsView
		self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		
		# Performance improving settings
		self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
		self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
		
		# Settings for mouse centric transformation / scaling
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		
		# Remove scroll bars
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		# Scene to contain our QGraphicsItems
		scene = QtGui.QGraphicsScene(self)
		scene.setBackgroundBrush(QtCore.Qt.darkGray)
		self.setScene(scene)
		#self.setSceneRect(-1000.0, -1000.0, 1000.0, 1000.0)
		#self.translate(0,0)
		
				
		# Variables for middle mouse panning		
		self._panning = False
		self._panStartX = 0.0
		self._panStartY = 0.0
		
	
	def mousePressEvent(self, event):
		'Event fired when a mouse button is pressed'
		#print self.mapToScene()
		
		# Check for middle mouse events, to begin dragging / panning
		if event.button() == QtCore.Qt.MiddleButton:
			self._panning = True
			self._panStartX = event.x()
			self._panStartY = event.y()
			self.setCursor(QtCore.Qt.ClosedHandCursor)
			event.accept()
		else:
			event.ignore()
		# Also call inherrited methods (required for mouse selecting)
		super(GraphView, self).mousePressEvent(event)
		
	def mouseReleaseEvent(self, event):
		'Event fired when a mouse button is released'
		# Check for middle mouse events, to end dragging / panning
		if event.button() == QtCore.Qt.MiddleButton:
			self._panning = False
			self.setCursor(QtCore.Qt.ArrowCursor)
			event.accept()
		else:
			event.ignore()
		# Also call inherrited methods (required for mouse selecting)
		super(GraphView, self).mouseReleaseEvent(event)
	
	def mouseMoveEvent(self, event):
		'Event fired whenever the mouse is moved'
		# See if we are currently panning, and translate as required
		if self._panning:
			transx = (event.x() - self._panStartX)
			transy = (event.y() - self._panStartY)
			self.translate(transx, transy)
			self._panStartX = event.x()
			self._panStartY = event.y()
			event.accept()
		else:
			event.ignore()
			
		# Also call inherrited methods (required for mouse centered scaling)
		super(GraphView, self).mouseMoveEvent(event)
		
		
	
	
	def wheelEvent(self, event):
		'Event fired when mouse is scrolled'
		
		# Zoom ratio
		level = 1.02
		if event.delta() < 0:
			# invert ratio for zooming out
			scaleFactor = 1.0 / level
		else:
			scaleFactor = level
		
		self.scaleView(scaleFactor)
		return		
				
	def scaleView(self, scaleFactor):
		'Check that a scale operation will be will not go beyond 100%'
		factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0,0,1,1)).width()
		
		if factor < 1.00:
			return
		self.scale(scaleFactor, scaleFactor)
		
	def setScale(self, scaleFactor):
		'Directly apply a scale to the scene'
		current = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0,0,1,1)).width()
		# revert to nothing
		self.scale(1.0 / current, 1.0 / current)
		
		# Apply the matrix
		self.setMatrix(self.matrix().scale(scaleFactor, scaleFactor))
		
		# apply new scale
		self.scaleView(scaleFactor)
		
	def add(self, node):
		self.scene().addItem(node)
		