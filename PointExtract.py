import sys
import glob
import os
sys.dont_write_bytecode=True
import os
from PyQt6.QtCore import QSize,Qt,QPoint
from PyQt6.QtWidgets import  QApplication, QWidget, QPushButton, QVBoxLayout, QToolBar, QFileDialog, QLabel, QHBoxLayout, QMainWindow, QStatusBar
from PyQt6.QtGui import QPixmap, QPen,QPainter,QColor, QAction, QPolygon

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.points = QPolygon()
        self.draw=False


    def paintEvent(self, event):  
        super().paintEvent(event)
        qp = QPainter(self)
        pen = QPen(QColor('Red'))
        pen.setWidth(4)
        qp.setPen(pen)
        qp.drawPoints(self.points)

    def mousePressEvent(self, event):
        if self.draw and event.button() == Qt.MouseButton.LeftButton:
            self.points.append(event.pos())
            self.update()

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PointExtract")

        self.img = ImageLabel()
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
        
        toolbar.addAction(button_file)
        toolbar.addAction(button_previous)
        toolbar.addAction(button_next)
        toolbar.addAction(self.button_draw)
        toolbar.addAction(button_undo)
        toolbar.addAction(button_clear)

        self.setStatusBar(QStatusBar(self))
        self.setMinimumSize(QSize(600, 600))

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
        pixmap=QPixmap(self.imageFiles[index]).scaledToWidth(512)
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

    def onClearButtonClick(self):
        self.img.points=QPolygon()
        self.img.update()

    def onUndoButtonClick(self):
        if not self.img.points.isEmpty():
            self.img.points.remove(self.img.points.size()-1)
            self.img.update()


    
       
  


if __name__ == '__main__':

    app= QApplication(sys.argv)
    window= MainWindow()
    window.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')