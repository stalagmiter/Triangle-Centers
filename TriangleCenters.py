import sys, math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from TriangleGraphics import *

class TriangleCenters(QWidget):

    def __init__(self):
        super().__init__()
        pix = QPixmap(25, 25)
        pix.fill(Qt.white)
        qp = QPainter(pix)
        qp.setPen(QColor(0, 0, 255, 50))
        qp.drawRect(pix.rect())
        qp.end()
        
        scene = QGraphicsScene(0, 0, 1000, 1000)
        scene.setBackgroundBrush(QBrush(pix))
        self.triangle = Triangle()
        scene.addItem(self.triangle)
        view = QGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)

        grid = QGridLayout(self)
        grid.setVerticalSpacing(20)
        grid.addWidget(QPushButton(icon=tricon((28, 27), (2, 27), (15, 5)),
                                   clicked=self.equilateral), 0, 0, Qt.AlignLeft)
        grid.addWidget(QPushButton(icon=tricon((25, 5), (25, 27), (3, 27)),
                                   clicked=self.right), 0, 1, Qt.AlignCenter)
        grid.addWidget(QPushButton(icon=tricon((5, 27), (15, 3), (25, 27)),
                                   clicked=self.isosceles), 0, 2, Qt.AlignRight)
        group = QButtonGroup(self, exclusive=False)
        group.buttonToggled[QAbstractButton, bool].connect(self.toggle_elements)
        for i, v in enumerate(CENTERS):
            w = QWidget(objectName='Block', styleSheet=f'border-color: {COLORS[i]}')
            vbox = QVBoxLayout(w)
            cb = QCheckBox(v, checked=i<3, styleSheet='font-size: 16pt; font-weight: bold')
            vbox.addWidget(cb); group.addButton(cb)
            cb = QCheckBox(LINES[i] if i < 4 else CIRCLES[-1])
            vbox.addWidget(cb); group.addButton(cb)
            if i % 2:
                cb = QCheckBox(CIRCLES[i > 1])
                vbox.addWidget(cb); group.addButton(cb)
            grid.addWidget(w, i + 1, 0, 1, 3)
            
        grid.addWidget(QCheckBox('Euler Line', toggled=self.triangle.euler.setVisible,
                                 styleSheet='font-size: 16pt; font-weight: bold'), 6, 0, 1, 3)
        grid.setRowStretch(7, 8)
        grid.addWidget(QCheckBox('Angles', toggled=self.toggle_angles), 8, 0, 1, 3)
        grid.addWidget(view, 0, 3, 9, 1)

        self.equilateral()
        for x in self.findChildren(QCheckBox) + self.findChildren(QPushButton):
            x.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet('''
        #Block {border: 3px solid}
        QPushButton {
            icon-size: 30px;
            border: none;
            padding: 6px;
        } QPushButton:hover {border: 2px solid SlateBlue}
        QPushButton:pressed {background-color: rgba(0, 0, 255, 50)}''')

    def equilateral(self):
        for i, v in enumerate(self.triangle.anchors):
            v.setPos(220 * math.sin(math.radians(120 * i + 60)),
                     220 * math.cos(math.radians(120 * i + 60)))
        self.update_triangle()
        
    def right(self):
        for i, v in enumerate([(350, 0), (350, 350), (0, 350)]):
            self.triangle.anchors[i].setPos(*v)
        self.update_triangle()
        
    def isosceles(self):
        for i, v in enumerate([(0, 410), (150, 0), (300, 410)]):
            self.triangle.anchors[i].setPos(*v)
        self.update_triangle()

    def update_triangle(self):
        self.triangle.setVertices()
        center = self.triangle.scene().sceneRect().center()
        self.triangle.setPos(center - self.triangle.boundingRect().center())
        self.findChild(QGraphicsView).centerOn(center)

    def toggle_elements(self, button, state):
        key = button.text()
        if key in self.triangle.centers:
            self.triangle.centers[key].setVisible(state)
        elif key in self.triangle.circles:
            self.triangle.circles[key].setVisible(state)
        else:
            for x in self.triangle.lines[key]:
                x.setVisible(state)

    def toggle_angles(self, state):
        for x in self.triangle.anchors:
            x.label.setVisible(state)
        if state:
            self.triangle.setVertices()


def tricon(*points):
    pix = QPixmap(30, 30)
    pix.fill(Qt.transparent)
    qp = QPainter(pix)
    qp.setRenderHint(QPainter.Antialiasing)
    qp.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
    qp.drawPolygon(QPolygon(QPoint(*x) for x in points))
    qp.end()
    return QIcon(pix)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TriangleCenters()
    window.showMaximized()
    sys.exit(app.exec_())
