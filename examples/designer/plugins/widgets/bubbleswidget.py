#!/usr/bin/env python

"""
bubbleswidget.py

A PyQt custom widget example for Qt Designer.

Copyright (C) 2006 David Boddie <david@boddie.org.uk>
Copyright (C) 2005-2006 Trolltech ASA. All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import random
from PySide import QtCore, QtGui


class BaseClass(QtGui.QWidget):

    """BaseClass(QtGui.QWidget)

    Provides a base custom widget class to show that properties implemented
    in Python can be inherited and shown as belonging to distinct classes
    in Qt Designer's Property Editor.
    """

    def __init__(self, parent = None):

        QtGui.QWidget.__init__(self, parent)
        self.resetAuthor()

    # Define getter, setter and resetter methods for the author property.

    def getAuthor(self):
        return self._author

    def setAuthor(self, name):
        self._author = name

    def resetAuthor(self):
        self._author = "David Boddie"

    author = QtCore.Property("QString", getAuthor, setAuthor, resetAuthor)


class Bubble:

    """Bubble

    Provides a class to represent individual bubbles in a BubblesWidget.
    Each Bubble instance can render itself onto a paint device using a
    QPainter passed to its drawBubble() method.
    """

    def __init__(self, position, radius, speed, innerColor, outerColor):

        self.position = position
        self.radius = radius
        self.speed = speed
        self.innerColor = innerColor
        self.outerColor = outerColor
        self.updateBrush()

    def updateBrush(self):

        gradient = QtGui.QRadialGradient(
                QtCore.QPointF(self.radius, self.radius), self.radius,
                QtCore.QPointF(self.radius*0.5, self.radius*0.5))

        gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 255))
        gradient.setColorAt(0.25, self.innerColor)
        gradient.setColorAt(1, self.outerColor)
        self.brush = QtGui.QBrush(gradient)

    def drawBubble(self, painter):

        painter.save()
        painter.translate(self.position.x() - self.radius,
                          self.position.y() - self.radius)
        painter.setBrush(self.brush)
        painter.drawEllipse(0.0, 0.0, 2*self.radius, 2*self.radius)
        painter.restore()


class BubblesWidget(BaseClass):

    """BubblesWidget(BaseClass)

    Provides a custom widget that shows a number of rising bubbles.
    Various properties are defined so that the user can customize the
    appearance of the widget, and change the number and behaviour of the
    bubbles shown.
    """

    # We define two signals that are used to indicate changes to the status
    # of the widget.
    __pyqtSignals__ = ("bubbleLeft()", "bubblesRemaining(int)")

    def __init__(self, parent = None):

        BaseClass.__init__(self, parent)
        self.pen = QtGui.QPen(QtGui.QColor("#cccccc"))
        self.bubbles = []
        self.backgroundColor1 = self.randomColor()
        self.backgroundColor2 = self.randomColor().darker(150)
        self.newBubble = None

        random.seed()

        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.setSingleShot(False)
        self.connect(self.animation_timer, QtCore.SIGNAL("timeout()"), self.animate)
        self.animation_timer.start(25)

        self.bubbleTimer = QtCore.QTimer()
        self.bubbleTimer.setSingleShot(False)
        self.connect(self.bubbleTimer, QtCore.SIGNAL("timeout()"), self.expandBubble)

        self.setMouseTracking(True)
        self.setMinimumSize(QtCore.QSize(200, 200))
        self.setWindowTitle(self.tr("Bubble Maker"))

    def paintEvent(self, event):

        background = QtGui.QRadialGradient(
                QtCore.QPointF(self.rect().topLeft()), 500,
                QtCore.QPointF(self.rect().bottomRight()))
        background.setColorAt(0, self.backgroundColor1)
        background.setColorAt(1, self.backgroundColor2)

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(event.rect(), QtGui.QBrush(background))

        painter.setPen(self.pen)

        for bubble in self.bubbles:

            if QtCore.QRectF(bubble.position - QtCore.QPointF(bubble.radius, bubble.radius),
                      QtCore.QSizeF(2*bubble.radius, 2*bubble.radius)).intersects(QtCore.QRectF(event.rect())):
                bubble.drawBubble(painter)

        if self.newBubble:

            self.newBubble.drawBubble(painter)

        painter.end()

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton and self.newBubble is None:

            self.newBubble = Bubble(QtCore.QPointF(event.pos()), 4.0,
                                    1.0 + random.random() * 7,
                                    self.randomColor(), self.randomColor())
            self.bubbleTimer.start(50)
            event.accept()

    def mouseMoveEvent(self, event):

        if self.newBubble:

            self.update(
                QtCore.QRectF(self.newBubble.position - \
                       QtCore.QPointF(self.newBubble.radius + 1, self.newBubble.radius + 1),
                       QtCore.QSizeF(2*self.newBubble.radius + 2, 2*self.newBubble.radius + 2)).toRect()
                )
            self.newBubble.position = QtCore.QPointF(event.pos())
            self.update(
                QtCore.QRectF(self.newBubble.position - \
                       QtCore.QPointF(self.newBubble.radius + 1, self.newBubble.radius + 1),
                       QtCore.QSizeF(2*self.newBubble.radius + 2, 2*self.newBubble.radius + 2)).toRect()
                )

        event.accept()

    def mouseReleaseEvent(self, event):

        if self.newBubble:

            self.bubbles.append(self.newBubble)
            self.newBubble = None
            self.bubbleTimer.stop()
            self.emit(QtCore.SIGNAL("bubblesRemaining(int)"), len(self.bubbles))

        event.accept()

    def expandBubble(self):

        if self.newBubble:

            self.newBubble.radius = min(self.newBubble.radius + 4.0,
                                        self.width()/8.0, self.height()/8.0)
            self.update(
                QtCore.QRectF(self.newBubble.position - \
                       QtCore.QPointF(self.newBubble.radius + 1, self.newBubble.radius + 1),
                       QtCore.QSizeF(2*self.newBubble.radius + 2, 2*self.newBubble.radius + 2)).toRect()
                )
            self.newBubble.updateBrush()

    def randomColor(self):

        red = 205 + random.random() * 50
        green = 205 + random.random() * 50
        blue = 205 + random.random() * 50
        alpha = 91 + random.random() * 100

        return QtGui.QColor(red, green, blue, alpha)

    def animate(self):

        bubbles = []
        left = False
        for bubble in self.bubbles:

            bubble.position = bubble.position + QtCore.QPointF(0, -bubble.speed)

            self.update(
                QtCore.QRectF(bubble.position - \
                       QtCore.QPointF(bubble.radius + 1, bubble.radius + 1),
                       QtCore.QSizeF(2*bubble.radius + 2, 2*bubble.radius + 2 + bubble.speed)).toRect()
                )

            if bubble.position.y() + bubble.radius > 0:
                bubbles.append(bubble)
            else:
                self.emit(QtCore.SIGNAL("bubbleLeft()"))
                left = True

        if self.newBubble:
            self.update(
                QtCore.QRectF(self.newBubble.position - \
                       QtCore.QPointF(self.newBubble.radius + 1, self.newBubble.radius + 1),
                       QtCore.QSizeF(2*self.newBubble.radius + 2, 2*self.newBubble.radius + 2)).toRect()
                )

        self.bubbles = bubbles
        if left:
            self.emit(QtCore.SIGNAL("bubblesRemaining(int)"), len(self.bubbles))

    def sizeHint(self):

        return QtCore.QSize(200, 200)

    # We provide getter and setter methods for the numberOfBubbles property.
    def getBubbles(self):

        return len(self.bubbles)

    # The setBubbles() method can also be used as a slot.
    @QtCore.Slot(int)
    def setBubbles(self, value):

        value = max(0, value)

        while len(self.bubbles) < value:

            newBubble = Bubble(QtCore.QPointF(random.random() * self.width(),
                                       random.random() * self.height()),
                               4.0 + random.random() * 20,
                               1.0 + random.random() * 7,
                               self.randomColor(), self.randomColor())
            newBubble.updateBrush()
            self.bubbles.append(newBubble)

        self.bubbles = self.bubbles[:value]
        self.emit(QtCore.SIGNAL("bubblesRemaining(int)"), value)
        self.update()

    numberOfBubbles = QtCore.Property("int", getBubbles, setBubbles)

    # We provide getter and setter methods for the color1 and color2
    # properties. The red, green and blue components for the QColor
    # values stored in these properties can be edited individually in
    # Qt Designer.

    def getColor1(self):

        return self.backgroundColor1

    def setColor1(self, value):

        self.backgroundColor1 = QtGui.QColor(value)
        self.update()

    color1 = QtCore.Property("QColor", getColor1, setColor1)

    def getColor2(self):

        return self.backgroundColor2

    def setColor2(self, value):

        self.backgroundColor2 = QtGui.QColor(value)
        self.update()

    color2 = QtCore.Property("QColor", getColor2, setColor2)

    # The stop() and start() slots provide simple control over the animation
    # of the bubbles in the widget.

    @QtCore.Slot()
    def stop(self):

        self.animation_timer.stop()

    @QtCore.Slot()
    def start(self):

        self.animation_timer.start(25)


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    widget = BubblesWidget()
    widget.show()
    sys.exit(app.exec_())
