import sys
import glob
import os
import math
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QSize,Qt
from PyQt6.QtWidgets import  QApplication, QWidget, QSlider, QVBoxLayout, QToolBar, QFileDialog, QLabel, QMainWindow, QStatusBar
from PyQt6.QtGui import QPixmap, QPen,QPainter,QColor, QAction


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class GraphWindow(QWidget):
    def __init__(self,points):
        super().__init__()

        self.setWindowTitle("PointExtract_Plot")
        self.points=np.array(points)
        self.allPoints=np.vstack(self.points)

        #all points calculation for every 5 degree rotation
        for i in range(0,361,5):
            self.allPoints=np.vstack((self.rotate(i),self.allPoints))

        Layout= QVBoxLayout()       
        toolbar = QToolBar()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)

        # Plot graph initially
        self.plotUpdate(self.points,self.allPoints)
        self.show()

        button_rotate= QAction("Rotate", self)
        button_rotate.setStatusTip("Rotate points")
        button_rotate.triggered.connect(self.rotate)
        # slider for rotating the points
        self.slider= QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(360)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.onSliderValueChanged)

        toolbar.addAction(button_rotate)
        toolbar.addWidget(self.slider)
        Layout.addWidget(toolbar)
        Layout.addWidget(self.sc)

        self.setLayout(Layout)
        self.setMinimumSize(QSize(416, 600))

    def rotate(self,degree):
        # degree to radian
        angle=degree*np.pi/180
        #calculate the mean of points
        center = np.mean(self.points, axis=0)
        # minus the mean from all points
        translated_points = self.points - center
        # rotation matrix
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                    [np.sin(angle), np.cos(angle)]])
        # dot product
        rotated_points = np.dot(translated_points, rotation_matrix)
        # rotated points
        rotated_points += center

        return rotated_points

        

    def plotUpdate(self,points,allpoints):
        # clear previous graph
        self.sc.axes.cla()
        self.sc.axes.scatter(points[:, 0], points[:, 1], color='red')

        # Set the axis limits to include all points
        x_min = allpoints[:, 0].min() - 5
        x_max = allpoints[:, 0].max() + 5
        y_min = allpoints[:, 1].min() - 5
        y_max = allpoints[:, 1].max() + 5
        self.sc.axes.set_xlim(x_min, x_max)
        self.sc.axes.set_ylim(y_min, y_max)
        self.sc.axes.set_aspect('equal')
        self.sc.axes.axis('off')
        self.sc.draw()

    # slider value change triggers new graph
    def onSliderValueChanged(self,value):
        rotatedPoints=self.rotate(value)
        self.plotUpdate(rotatedPoints,self.allPoints)

      

class DrawPoint(QLabel):
    def __init__(self, parent=None):
        super(DrawPoint, self).__init__(parent)
        self.points = []
        self.draw=False


    def paintEvent(self, event):  
        super().paintEvent(event)
        qp = QPainter(self)
        pen = QPen(QColor('Red'))
        pen.setWidth(4)
        qp.setPen(pen)
        for point in self.points:
            qp.drawPoint(point[0],point[1])

    def mousePressEvent(self, event):
        if self.draw and event.button() == Qt.MouseButton.LeftButton:
            self.points.append([event.pos().x(),event.pos().y()])
            self.update()



class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PointExtract")
        # this variable stores the graph window
        self.w=None #No window yet
        self.img = DrawPoint()
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.img)        

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_file = QAction("File", self)
        button_file.setStatusTip("Select an Image")
        button_file.triggered.connect(self.onFileButtonClick)

        button_next = QAction("Next",self)
        button_next.setStatusTip("Next Image")
        button_next.triggered.connect(self.onNextButtonClick)

        button_previous = QAction("Previous",self)
        button_previous.setStatusTip("Previous Image")
        button_previous.triggered.connect(self.onPreviousButtonClick)

        self.button_draw = QAction("Draw",self)
        self.button_draw.setStatusTip("Draw Points")
        self.button_draw.setCheckable(True)
        self.button_draw.triggered.connect(self.onDrawButtonClick)

        button_undo = QAction("Undo",self)
        button_undo.setStatusTip("Remove The last point")
        button_undo.triggered.connect(self.onUndoButtonClick)

        button_clear = QAction("Clear",self)
        button_clear.setStatusTip("Clear All Points")
        button_clear.triggered.connect(self.onClearButtonClick)

        button_plot = QAction("Plot",self)
        button_plot.setStatusTip("Plot All Points")
        button_plot.triggered.connect(self.onPlotButtonClick)
        
        toolbar.addAction(button_file)
        toolbar.addAction(button_previous)
        toolbar.addAction(button_next)
        toolbar.addAction(self.button_draw)
        toolbar.addAction(button_undo)
        toolbar.addAction(button_clear)
        toolbar.addAction(button_plot)

        self.setStatusBar(QStatusBar(self))
        self.setMinimumSize(QSize(416, 600))

        self.folderDir=None
        self.imagePath=None
        self.imageFiles=None
        self.index=None


    def onFileButtonClick(self):      
        file_dialog = QFileDialog()
        file_path=file_dialog.getOpenFileName(None, "Window name", "", "Images (*.png *.jpg *.jpeg)")[0]            
        if file_path=='':
            pass
        else:
            # store all the images path in the imagefiles and get the current image's index
            self.imagePath=file_path
            self.folderDir=os.path.dirname(file_path)
            self.imageFiles=glob.glob(self.folderDir+'/*.png')+glob.glob(self.folderDir+'/*.jp*g')

            self.index=self.getIndex()
            self.imageShow(self.index)

    def getIndex(self):
        for i in range(0,len(self.imageFiles)):
            if os.path.basename(self.imageFiles[i])==os.path.basename(self.imagePath):
                return i
            

    def imageShow(self,index):
        pixmap=QPixmap(self.imageFiles[index]).scaledToWidth(416)
        self.img.setPixmap(pixmap)
        self.img.setFixedSize(pixmap.size())
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img.show()
        
               

    def onNextButtonClick(self):
        if (self.index!=None and self.index<len(self.imageFiles)-1):
            self.index +=1
            self.imageShow(self.index)
            

    def onPreviousButtonClick(self):
        if (self.index!=None and self.index>0):
            self.index -= 1
            self.imageShow(self.index)
    
    def onDrawButtonClick(self):
        if self.index!=None:
            self.img.draw=self.button_draw.isChecked()
        else:
            self.button_draw.setChecked(False)

    def onClearButtonClick(self):
        self.img.points=[]
        self.img.update()

    def onUndoButtonClick(self):
        if len(self.img.points)>0:
            self.img.points.pop()
            self.img.update()

    def onPlotButtonClick(self):
        offset=self.img.height()       
        points=[]
        if len(self.img.points)!=0:
            for point in self.img.points:
                points.append([point[0],offset-point[1]])  # image points start from the top left

        self.w = GraphWindow(points)  
        self.w.show() 


if __name__ == '__main__':

    app= QApplication(sys.argv)
    window= MainWindow()
    window.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')