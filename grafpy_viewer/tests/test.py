import sys
import math
from PyQt4 import QtGui, QtCore


class MyQGraphicsView(QtGui.QGraphicsView):
	def __init__(self, parent):
		super(MyQGraphicsView, self).__init__(parent)
		
		self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
		self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		
		scene = QtGui.QGraphicsScene(self)
		scene.setBackgroundBrush(QtCore.Qt.white)
		self.setScene(scene)
		
		# Draw graph
		x = 0
		while x < 10000:
			y = 0
			while y < 10000:
				
				if (x % 100 == 0) and (y % 100 == 0):
					scene.addRect(x, y, 2, 2)
					i = QtGui.QGraphicsSimpleTextItem()
					i.setText("(%s,%s)" % (x,y))
					i.setPos(x,y)
					scene.addItem(i)
				else:
					scene.addRect(x,y,1,1)
				y += 25
			x += 25
		
		
		#self.(0,0,self.width(),self.height())
		self.fitInView (5000 - self.width() / 2,
					5000 - self.height() / 2, 
					self.width(), self.height(),
					QtCore.Qt.IgnoreAspectRatio)
		#self.translate(5000.0, 5000.0)
		#self.currentCenterPoint = QtCore.QPointF() 
		#self.centerOn(QtCore.QPointF(200.0, 300.0))
		self.scaleLevel = 1.0
		
		# bool to hold whether we are panning or not
		self._panning = False
		# panning info
		self._panStartX = 0.0
		self._panStartY = 0.0
		
		# Remove scroll bars
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		#self.horizontalScrollBar()

	#def ensureVisible(self):
	#	pass
	
	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.MiddleButton:
			self._panning = True
			self._panStartX = event.x()
			self._panStartY = event.y()
			self.setCursor(QtCore.Qt.ClosedHandCursor)
			event.accept()
		else:
			event.ignore()
		
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.MiddleButton:
			self._panning = False
			self.setCursor(QtCore.Qt.ArrowCursor)
			event.accept()
		else:
			event.ignore()
	
	def mouseMoveEvent(self, event):
		if self._panning:
			transx = (event.x() - self._panStartX)
			transy = (event.y() - self._panStartY)
			print "translate", transx, transy
			self.translate(transx, transy)
			self._panStartX = event.x()
			self._panStartY = event.y()
			event.accept()
		else:
			event.ignore()
		super(MyQGraphicsView, self).mouseMoveEvent(event)
		
		
	def keyPressEvent(self, event):
		key = event.key()
		
		if key == QtCore.Qt.Key_Home:
			self.setScale(7.10)
			#print self.sceneRect()
			self.setSceneRect(self.scene().itemsBoundingRect())
	
	
	def wheelEvent(self, event):
		#scaleLevel = math.pow(2.0, event.delta() / 1080.0)
		level = 1.02
		if event.delta() < 0:
			scaleFactor = 1.0 / level
		else:
			scaleFactor = level
		
		self.scaleView(scaleFactor)
		return		
				
	def scaleView(self, scaleFactor):
		factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0,0,1,1)).width()
		
		if factor < 1.00:
			return
		
		self.scale(scaleFactor, scaleFactor)
		
	def setScale(self, scaleFactor):
		current = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0,0,1,1)).width()
		# revert to nothing
		self.scale(1.0 / current, 1.0 / current)
		
		# Apply the matrix
		self.setMatrix(self.matrix().scale(scaleFactor, scaleFactor))
		
		# apply new scale
		self.scaleView(scaleFactor)
		
		
		
			
	
		
	'''	
	def resizeEvent(self, event):
		visibleArea = self.mapToScene(self.rect()).boundingRect()
		#self.setCenter(visibleArea.center())
	
		#super(MyQGraphicsView, self).resizeEvent(event)
	'''


		

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	view = MyQGraphicsView(None)
	view.show()
	sys.exit(app.exec_())