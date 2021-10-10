from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

COLORS = ('Red', 'Lime', 'Blue', 'Gold', '#8533ff')
CENTERS = ('Centroid', 'Circumcenter', 'Orthocenter', 'Incenter', 'Nine-point center')
LINES = ('Medians', 'Perpendicular Bisectors', 'Altitudes', 'Angle Bisectors')
CIRCLES = ('Circumcircle', 'Incircle', 'Nine-point circle')

class Anchor(QGraphicsEllipseItem):

    def __init__(self, r, color, *args, **kwargs):
        super().__init__(-r, -r, r * 2, r * 2, *args, **kwargs)
        color.setAlpha(200)
        self.setPen(QPen(color, 1.5))
        color.setAlpha(75)
        self.setBrush(color)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setCursor(Qt.SizeAllCursor)
        self.label = QGraphicsSimpleTextItem(self.parentItem())
        self.label.setBrush(Qt.magenta)
        font = self.label.font(); font.setPointSize(14); self.label.setFont(font)
        self.label.setZValue(1)
        self.label.hide()
        
    def paint(self, painter, option, widget):
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        painter.setBrush(QColor(*self.pen().color().getRgb()[:3]))
        painter.drawEllipse(self.rect().center(), 1, 1)
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.parentItem().setVertices()


class EulerLine(QGraphicsLineItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gradient = QLinearGradient()
        colors = ('#f00', '#ff9a00', '#d0de21', '#4fdc4a', '#3fdad8', '#2fc9e2',
                  '#1c7fee', '#5f15f2', '#ba0cf8', '#fb07d9', '#f00')
        for i, v in enumerate(colors):
            self._gradient.setColorAt(i / len(colors), QColor(v))
        self._pen = QPen(self._gradient, 8, Qt.SolidLine, Qt.RoundCap)
        self.hide()

    def setLine(self, *args):
        super().setLine(QLineF(*args))
        self._gradient.setStart(args[0])
        self._gradient.setFinalStop(args[1])
        self._pen.setBrush(self._gradient)
        self.setPen(self._pen)


class Triangle(QGraphicsPolygonItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circles = {
            k: self.pathItem(v) for k, v in zip(CIRCLES, COLORS[1:2] + COLORS[3:])
            }
        self.anchors = [Anchor(9, QColor('LightSlateGrey'), self) for i in range(3)]
        self.lines = {k: self.lineGroup(v) for k, v in zip(LINES, COLORS)}
        self.euler = EulerLine(self)
        self.centers = {
            k: self.centerItem(v, COLORS.index(v) < 3) for k, v in zip(CENTERS, COLORS)
            }
        self.setPen(QPen(Qt.black, 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setCursor(Qt.OpenHandCursor)

    def pathItem(self, color):
        path = QGraphicsPathItem(self)
        path.setPen(QPen(QColor(color), 3))
        path.hide()
        return path

    def lineGroup(self, color):
        lines = []
        for i in range(3):
            line = QGraphicsLineItem(self)
            line.setPen(QPen(QColor(color), 4, Qt.SolidLine, Qt.RoundCap))
            line.hide()
            lines.append(line)
        return lines

    def centerItem(self, color, state):
        color = QColor(color)
        ellipse = QGraphicsEllipseItem(-10, -10, 20, 20, self)
        ellipse.setPen(QPen(color, 3))
        color.setAlpha(127)
        ellipse.setBrush(color)
        ellipse.setVisible(state)
        return ellipse

    def setVertices(self):
        points = [x.pos() for x in self.anchors]
        self.setPolygon(QPolygonF(points))
        A, B, C = points
        sides = [QLineF(B, C), QLineF(C, A), QLineF(A, B)]

        centroid = (A + B + C) / 3
        self.centers['Centroid'].setPos(centroid)
        for i, v in enumerate(self.lines['Medians']):
            v.setLine(QLineF(points[i], sides[i].center()))
        
        circum = QPointF(
            A @ 2 * (B - C).y() + B @ 2 * (C - A).y() + C @ 2 * (A - B).y(),
            A @ 2 * (C - B).x() + B @ 2 * (A - C).x() + C @ 2 * (B - A).x()
            ) / (2 * (A.x() * (B - C).y() + B.x() * (C - A).y() + C.x() * (A - B).y()) or 1e-2)
        self.centers['Circumcenter'].setPos(circum)
        
        pointer = QPointF()
        if self.polygon().containsPoint(circum, Qt.OddEvenFill):
            for i, v in enumerate(self.lines['Perpendicular Bisectors']):
                line = QLineF(sides[i].center(), circum)
                line.intersect(sides[(i + 1) % 3], pointer)
                if not self.contains(pointer):
                    line.intersect(sides[(i + 2) % 3], pointer)
                v.setLine(QLineF(sides[i].center(), pointer))
        else:
            for i, v in enumerate(self.lines['Perpendicular Bisectors']):
                v.setLine(QLineF(sides[i].center(), circum))

        path = QPainterPath()
        r = QLineF(A, circum).length()
        path.addEllipse(circum, r, r)
        self.circles['Circumcircle'].setPath(path)

        ortho = centroid * 3 - circum * 2
        self.centers['Orthocenter'].setPos(ortho)
        if ortho in self.boundingRect():
            for i, v in enumerate(self.lines['Altitudes']):
                QLineF(points[i], ortho).intersect(sides[i], pointer)
                v.setLine(QLineF(points[i], pointer))
        else:
            for i, v in enumerate(self.lines['Altitudes']):
                v.setLine(QLineF(points[i], ortho))

        self.euler.setLine(circum, ortho)
        
        a, b, c = (x.length() for x in sides)
        incenter = (a * A + b * B + c * C) / (a + b + c)
        self.centers['Incenter'].setPos(incenter)
        
        if self.contains(incenter):
            for i, v in enumerate(self.lines['Angle Bisectors']):
                v.setLine(QLineF(points[i], incenter))
        else:
            for i, v in enumerate(self.lines['Angle Bisectors']):
                QLineF(points[i], incenter).intersect(sides[i], pointer)
                v.setLine(QLineF(points[i], pointer))
            
        s = (a + b + c) / 2
        r = ((s - a) * (s - b) * (s - c) * (1 / s)) ** 0.5
        path = QPainterPath()
        path.addEllipse(incenter, r - 2, r - 2)
        self.circles['Incircle'].setPath(path)

        npcenter = (circum + ortho) / 2
        self.centers['Nine-point center'].setPos(npcenter)
        r = QLineF(npcenter, sides[0].center()).length()
        path = QPainterPath()
        path.addEllipse(npcenter, r, r)
        self.circles['Nine-point circle'].setPath(path)

        if self.anchors[0].label.isVisible():
            for i, v in enumerate(self.anchors):
                angle = abs(180 - sides[(i + 1) % 3].angleTo(sides[(i + 2) % 3]))
                v.label.setText(f'{angle:.0f}°')
                pos = self.lines['Angle Bisectors'][i].line().pointAt(0.12)
                rect = v.boundingRect()
                rect.moveCenter(self.mapFromItem(v, pos - v.pos()))
                v.label.setPos(rect.topLeft() + QPointF(0, 2))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)

    def shape(self):
        stroker = QPainterPathStroker(self.pen())
        stroker.setWidth(stroker.width() + 6)
        path = QPainterPath()
        path.addPolygon(self.polygon())
        path.closeSubpath()
        return stroker.createStroke(path)

QPointF.__matmul__ = lambda a, b: a.x() ** b + a.y() ** b
