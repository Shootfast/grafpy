from PyQt4 import QtCore, QtGui
 

class v_NodeLabel(QtGui.QGraphicsSimpleTextItem):
	'QgraphicsSimpleTextItem that draws a node label'
	Type = QtGui.QGraphicsSimpleTextItem.UserType + 1
	
	def __init__(self, text):
		super(v_NodeLabel, self).__init__()
		self.setText(text)
		
		# Create a pen with a thin white outline
		pen = QtGui.QPen(QtCore.Qt.white, 0.2)
		
		self.setPen(pen)
		# Set the inside of the text to black
		self.setBrush(QtCore.Qt.black)
		
	def type(self):
		return v_NodeLabel.Type
	
	
	
		
class v_Node(QtGui.QGraphicsItem):
	'QGraphicsItem object that draws a simple node'
	Type = QtGui.QGraphicsItem.UserType + 1
	
	def __init__(self, label):
		super(v_Node, self).__init__()
				
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
		self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
		self.setZValue(1)
		
		# Text
		self.text = v_NodeLabel(label)
		self.text.setParentItem(self)
		centerLabel = self.text.boundingRect().width() / 2
		self.text.setPos(-centerLabel,-35)
		
	
	def type(self):
		return v_Node.Type
			
	def boundingRect(self):
		adjust = 2.0
		return QtCore.QRectF(-10 -adjust, -10 - adjust, 23 + adjust, 23 + adjust)
	
	def shape(self):
		path = QtGui.QPainterPath()
		path.addEllipse(-10, -10, 20, 20) 
		return path
	
	def paint(self, painter, option, widget):
		# Drop Shadow
		#painter.setPen(QtCore.Qt.NoPen)
		#painter.setBrush(QtCore.Qt.darkGray)
		#painter.drawEllipse(-7, -7, 20, 20)
		
		gradient = QtGui.QRadialGradient(-3, -3, 10)
		if option.state & QtGui.QStyle.State_Sunken:
			gradient.setCenter(3, 3)
			gradient.setFocalPoint(3, 3)
			gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.white).light(120))
			gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.lightGray).light(120))
		else:
			gradient.setColorAt(0, QtCore.Qt.white)
			gradient.setColorAt(1, QtCore.Qt.lightGray)
		
		# Node
		painter.setBrush(QtGui.QBrush(gradient))
		painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
		painter.drawEllipse(-10, -10, 20, 20)
		
		
	def mousePressEvent(self, event):
		self.update()
		super(v_Node, self).mousePressEvent(event)
	
	def mouseReleaseEvent(self, event):
		self.update()
		super(v_Node, self).mouseReleaseEvent(event)
			
