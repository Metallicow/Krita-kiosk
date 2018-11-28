"""
This is a simple example of a Python script for Krita.
It demonstrates how to set up a custom popup!
"""

from PyQt5.QtGui import QCursor

from krita import Krita, Extension

from . import popuppalette_demo


class PopupPaletteExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

        self.actions = []
        self.popupframe = None

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("showpopuppalette", i18n("Popup Palette"))
        action.setShortcut('Z')
        action.triggered.connect(self.showhide)
        self.initialize()

    def initialize(self):
        self.popupframe = popuppalette_demo.PopupPaletteFrame()

    def showhide(self):
        if self.popupframe.isVisible():
            self.popupframe.hide()
        else:
            cursorPos = QCursor.pos()
            self.popupframe.move(cursorPos.x() - 256, cursorPos.y() - 256)
            self.popupframe.show()
            self.popupframe.activateWindow()


# Initialize and add the extension
Scripter.addExtension(PopupPaletteExtension(Krita.instance()))
