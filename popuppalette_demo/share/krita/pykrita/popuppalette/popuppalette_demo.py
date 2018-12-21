#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a example of a Python program/script/plugin for Krita.
It demonstrates how to set up a custom popup frame that also works as a
standalone program if needbe so developers can have a basic bridge for their
artwork/data when working with external programs.
THIS file is the standalone program.


This program/script/plugin is licensed CC 0 1.0, so that you can learn from it.

------ CC 0 1.0 ---------------

The person who associated a work with this deed has dedicated the work to the public domain by waiving all of his or her rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law.

You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""

#--Python Imports. https://www.python.org/
import os
import sys
## import datetime

try:
    gFileDir = os.path.dirname(os.path.abspath(__file__))
except:
    gFileDir = os.path.dirname(os.path.abspath(sys.argv[0]))
gImgDir = gFileDir + os.sep + 'images'
gPyKritaDir = os.path.dirname(gFileDir)
gKritaDir = os.path.dirname(gPyKritaDir)
gPicsDir = gKritaDir + os.sep + 'pics'
gShareDir = os.path.dirname(gKritaDir)

#--PySide/PyQt Imports. https://pypi.org/project/PyQt5/
from PyQt5.QtGui import  QBitmap, QBrush, QColor, QCursor, QImage, QLinearGradient, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
from PyQt5.QtWidgets import QAbstractButton, QAction, QApplication, QDialog, QMenu, QMessageBox, QWidget, QTextEdit

#--Krita Imports -- https://krita.org/
try:
    import krita
except ImportError:
    krita = None
    print('FAILED to import krita')


## def get_modification_date(filename):
##     timestamp = os.path.getmtime(filename)
##     return datetime.datetime.fromtimestamp(timestamp)


class ImageButton(QAbstractButton):
    def __init__(self, image, image_hover, image_pressed, parent=None):
        super(ImageButton, self).__init__(parent)
        self.image = image
        self.image_hover = image_hover
        self.image_pressed = image_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        img = self.image_hover if self.underMouse() else self.image
        if self.isDown():
            img = self.image_pressed

        painter = QPainter(self)
        painter.drawImage(event.rect(), img)

    def enterEvent(self, event):
        self.update()
        # QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        QApplication.setOverrideCursor(QCursor(QPixmap(gImgDir + os.sep + 'paperairplane_arrow_white24.png'), hotX=0, hotY=0))

    def leaveEvent(self, event):
        self.update()
        QApplication.restoreOverrideCursor()

    def sizeHint(self):
        return QSize(self.image.width(), self.image.height())


class PopupPaletteFrame(QDialog):
    def __init__(self, parent=None, f=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint):
        super(PopupPaletteFrame, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setGeometry(0, 0, 512, 512)

        self.offset = QPoint(0, 0)

        self.local_image = QImage(512, 512, QImage.Format_ARGB32)
        self.fgcolor = '#FFFFFF'
        self.bgcolor = '#000000'

        # This is how to load the merged image from a .kra file.
        ## import zipfile
        ## archive = zipfile.ZipFile(gImgDir + os.sep + 'myPopupPaletteWorkshop.kra', 'r')
        ## img_data = archive.read('mergedimage.png')
        ## img = QImage()
        ## img.loadFromData(img_data)
        ## self.texture = img

        self.texture = QImage(gImgDir + os.sep + 'colorwheel_pixel_palette.png')
        self.defaultblackwhiteImg = QImage(gImgDir + os.sep + 'defaultblackwhite10.png')
        self.switcharrowsImg = QImage(gImgDir + os.sep + 'switcharrows16.png')
        self.colorboxImg = QImage(gImgDir + os.sep + 'colorbox28.png')

        lHiColorDir = gShareDir + os.sep + 'icons' + os.sep + 'hicolor'

        # Text box.
        self.textbox = QTextEdit("Test QTextEdit", parent=self)
        self.textbox.move(192, 160)
        self.textbox.setGeometry(192, 160, 128, 32)

        # Big Button in middle.
        self.btnImage = btnImage = QImage(lHiColorDir + os.sep + '128x128' + os.sep + 'apps' + os.sep + 'calligrakrita.png')
        self.button = ImageButton(btnImage, btnImage, btnImage, self)
        self.button.move(256 - 64, 256 - 64)
        self.button.pressed.connect(self.buttonPressed)
        self.button.released.connect(self.buttonReleased)
        self.button.setToolTip('Right Click for Context Menu')
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.show_context_menu)

        # Create popup context menu.
        self._context_menu = QMenu(self)
        self._context_menu.addAction('Invert', self.invertTexture)
        self._context_menu.addAction('Mirror Horizontal', self.mirrorTextureHorizontal)
        self._context_menu.addAction('Mirror Vertical', self.mirrorTextureVertical)

        # 4 smaller buttons.
        self.btnImage1 = btnImage1 = QImage(lHiColorDir + os.sep + '32x32' + os.sep + 'apps' + os.sep + 'calligrakrita.png')
        self.button1 = ImageButton(btnImage1, btnImage1, btnImage1, self)
        self.button1.move(192, 320)
        self.button1.released.connect(self.button1Released)
        self.button1.setToolTip('test button')

        self.btnImage2 = btnImage2 = QImage(lHiColorDir + os.sep + '32x32' + os.sep + 'apps' + os.sep + 'calligrakrita.png')
        self.button2 = ImageButton(btnImage2, btnImage2, btnImage2, self)
        self.button2.move(224, 320)
        self.button2.released.connect(self.button2Released)
        self.button2.setToolTip('rotate_canvas_left')

        self.btnImage3 = btnImage3 = QImage(lHiColorDir + os.sep + '32x32' + os.sep + 'apps' + os.sep + 'calligrakrita.png')
        self.button3 = ImageButton(btnImage3, btnImage3, btnImage3, self)
        self.button3.move(256, 320)
        self.button3.released.connect(self.button3Released)
        self.button3.setToolTip('rotate_canvas_right')

        self.btnImage4 = btnImage4 = QImage(lHiColorDir + os.sep + '32x32' + os.sep + 'apps' + os.sep + 'calligrakrita.png')
        self.button4 = ImageButton(btnImage4, btnImage4, btnImage4, self)
        self.button4.move(288, 320)
        self.button4.released.connect(self.button4Released)
        self.button4.setToolTip('Im a painter button')

        # Fore/Back color stuff
        self.arrowsBtn = ImageButton(self.switcharrowsImg, self.switcharrowsImg, self.switcharrowsImg, parent=self)
        self.arrowsBtn.move(464, 453)
        self.arrowsBtn.pressed.connect(self.swapFG_BG_Colors)

        self.defblackwhiteBtn = ImageButton(self.defaultblackwhiteImg, self.defaultblackwhiteImg, self.defaultblackwhiteImg, parent=self)
        self.defblackwhiteBtn.move(436, 486)
        self.defblackwhiteBtn.pressed.connect(self.defaultFG_BG_Colors)

        if not krita:
            quitAction = QAction("E&xit", self, shortcut="Z",
                                 triggered=self.close)
            self.button.addAction(quitAction)
            self.button.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Mask - Anything not black (0, 0, 0, 0-255) in this image will not be shown when drawn out.
        self.setMask(QBitmap(gImgDir + os.sep + "pixel_palette_mask512.png"))
        self.drawGUI()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.setMouseTracking(True)

    def __del__(self):
        print('__del__ %s' % self.__class__.__name__)

    def mirrorTextureHorizontal(self):
        self.texture = self.texture.mirrored(horizontal=True, vertical=False)
        self.drawGUI()
        self.update()

    def mirrorTextureVertical(self):
        self.texture = self.texture.mirrored(horizontal=False, vertical=True)
        self.drawGUI()
        self.update()

    def invertTexture(self):
        self.texture.invertPixels()
        self.drawGUI()
        self.update()

    def swapFG_BG_Colors(self):
        self.fgcolor, self.bgcolor = self.bgcolor, self.fgcolor
        self.drawGUI()
        self.update()

    def defaultFG_BG_Colors(self):
        self.fgcolor = '#FFFFFF'
        self.bgcolor = '#000000'
        self.drawGUI()
        self.update()

    def show_context_menu(self, point):
        self._context_menu.exec_(self.button.mapToGlobal(point))

    def buttonPressed(self):
        pass

    def buttonReleased(self):
        QApplication.beep()

    def button1Released(self):
        QMessageBox.information(QWidget(self), i18n("Test Btn1"),
                                i18n("Hello! This is Krita version %s\n\nwidth %s height %s") % (Application.version(), self.width(), self.height()))

    def button2Released(self):
        krita.Krita.instance().action('rotate_canvas_left').trigger()

    def button3Released(self):
        krita.Krita.instance().action('rotate_canvas_right').trigger()

    def button4Released(self):
        QMessageBox.information(QWidget(self), i18n("Test Btn4"),
                                i18n('"The position of the artist is humble. He is essentially a channel." Piet Mondrian'))

    def saveData(self):
        with open(gFileDir + os.sep + 'test.txt', 'w') as f:
            f.write('I Closed Cleanly and wrote out some data')

    def closeEvent(self, event):
        self.saveData()
        event.accept()

    def sizeHint(self):
        return QSize(512, 512)

    def drawGUI(self):
        # Draw everything to an image first so we can have a local copy
        # available for pixel RGBA access.
        qimage = QImage(QSize(512, 512), QImage.Format_ARGB32)
        qp = QPainter(qimage)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setPen(Qt.NoPen)

        # Draw the texture.
        qp.drawImage(0, 0, self.texture)

        # Draw the graydient bar
        myQRect = QRect(497, 1, 14, 510)
        gradient = QLinearGradient(0, 0, 0, 512)
        gradient.setColorAt(0, QColor(self.fgcolor))
        gradient.setColorAt(1, QColor(self.bgcolor))
        qp.fillRect(myQRect, gradient)
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1))
        qp.setBrush(QBrush(QColor(0, 0, 0, 0)))
        qp.drawRect(497, 1, 14, 510)

        # Draw the fore/back color boxes
        qp.setPen(Qt.NoPen)
        qp.drawImage(464, 453, self.switcharrowsImg)
        qp.drawImage(436, 486, self.defaultblackwhiteImg)
        qp.setBrush(QColor(self.bgcolor))
        qp.drawRect(452, 468, 28, 28)
        qp.drawImage(452, 468, self.colorboxImg)
        qp.setBrush(QColor(self.fgcolor))
        qp.drawRect(436, 452, 28, 28)
        qp.drawImage(436, 452, self.colorboxImg)

        # Save a copy of the finished image locally.
        self.local_image = qimage

    def paintEvent(self, event):
        # Draw the completed image to the widget/window frame.
        qp = QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, self.local_image)
        qp.end()

    def updateKritaForeGroundColor(self, color):
        instance = krita.Krita.instance()
        views = instance.views()
        view0 = views[0]

        managedColor = krita.ManagedColor("RGBA", "U8", "")
        colorComponents = managedColor.components()
        colorComponents[0] = color.blueF()    # b
        colorComponents[1] = color.greenF()   # g
        colorComponents[2] = color.redF()     # r
        colorComponents[3] = color.alphaF()   # a
        managedColor.setComponents(colorComponents)

        view0.setForeGroundColor(managedColor)

    def updateKritaBackGroundColor(self, color):
        instance = krita.Krita.instance()
        views = instance.views()
        view0 = views[0]

        managedColor = krita.ManagedColor("RGBA", "U8", "")
        colorComponents = managedColor.components()
        colorComponents[0] = color.blueF()    # b
        colorComponents[1] = color.greenF()   # g
        colorComponents[2] = color.redF()     # r
        colorComponents[3] = color.alphaF()   # a
        managedColor.setComponents(colorComponents)

        view0.setBackGroundColor(managedColor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            ## print(self.offset)
        elif event.button() == Qt.LeftButton:
            position = QPoint(event.pos().x(), event.pos().y())
            color = QColor.fromRgb(self.local_image.pixel(position))
            self.fgcolor = color
            ## print(color.redF(), color.greenF(), color.blueF(), color.alphaF())  # print values from a QColor
            if krita:
                self.updateKritaForeGroundColor(color)
            self.drawGUI()
            self.update()  # Refresh the drawn colors.
        elif event.button() == Qt.RightButton:
            position = QPoint(event.pos().x(), event.pos().y())
            color = QColor.fromRgb(self.local_image.pixel(position))
            self.bgcolor = color
            ## print(color.redF(), color.greenF(), color.blueF(), color.alphaF())  # print values from a QColor
            if krita:
                self.updateKritaBackGroundColor(color)
            self.drawGUI()
            self.update()  # Refresh the drawn colors.
        elif event.buttons() == Qt.XButton1:
            QApplication.beep()
            # Do something here... Change a texture/mask/page, call a function, etc....
        elif event.buttons() == Qt.XButton2:
            QApplication.beep()
            # Do something here... Change a texture/mask/page, call a function, etc....

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MiddleButton:
            self.move(event.globalPos() - self.offset)
            event.accept()
        self.textbox.setPlainText('x = %s, y = %s' % (event.x(), event.y()))

    ## def wheelEvent(self, event):
    ##     event.accept()

    def enterEvent(self, event):
        self.update()
        ## QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        QApplication.setOverrideCursor(QCursor(QPixmap(gImgDir + os.sep + 'paperairplane_arrow_white24.png'), hotX=0, hotY=0))

    def leaveEvent(self, event):
        self.update()
        QApplication.restoreOverrideCursor()

    def event(self, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            ## print("Tab pressed")
            if krita:
                krita.Krita.instance().action('view_show_canvas_only').trigger()
            return False
        return QWidget.event(self, event)


def main():
    frame = PopupPaletteFrame()
    frame.show()
    frame.activateWindow()
    try:
        frame.exec_()
    except Exception as exc:
        raise exc


if __name__ == '__main__':
    app = QApplication([])
    frame = PopupPaletteFrame()
    frame.show()
    app.exec_()
