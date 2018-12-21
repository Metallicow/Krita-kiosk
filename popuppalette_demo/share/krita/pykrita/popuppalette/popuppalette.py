"""
This is a example of a Python program/script/plugin for Krita.
It demonstrates how to set up a custom popup frame that also works as a
standalone program if needbe so developers can have a basic bridge for their
artwork/data when working with external programs.


This program/script/plugin is licensed CC 0 1.0, so that you can learn from it.

------ CC 0 1.0 ---------------

The person who associated a work with this deed has dedicated the work to the public domain by waiving all of his or her rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law.

You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""

#--PyQt5 Imports -- https://pypi.org/project/PyQt5/
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCursor

#--Krita Imports -- https://krita.org/
import krita
from krita import Krita, Extension

#--Local Imports
from . import popuppalette_demo


class PopupPaletteExtension(Extension):
    """"""
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        self.kritaInstance = Krita.instance()
        self.actions = []
        self.popupframe = None

    def setup(self):
        """"""
        pass

    def createActions(self, window):
        """"""
        action = window.createAction("showpopuppalette", i18n("Popup Palette"))
        # The action shortcut is defined in the 'popuppalette.action' file for
        # the Extension class.
        action.triggered.connect(self.showhide)
        self.initialize()

    def initialize(self):
        """"""
        # Since this is the extension class we will want to parent our child
        #  to the nun and sometimes trade it with the krita mainframe to maintain
        #  'Always on Top' style flag when toggling the GL art canvas.
        mainWindow = self.kritaInstance.activeWindow().qwindow()
        self.popupframe = popuppalette_demo.PopupPaletteFrame(None)
        self.popupframe.hide()

        # When the krita mainframe close button is pressed,
        #  the menu item "Quit" is triggered,
        #  or the keyboard shortcut associated with "Quit" is pressed,
        #  we will want to collect all our data before krita destroys itself(object).
        #  In the standalone application this normally would call the closeEvent.
        ##TODO: Need a way to save data before Yes/No/Cancel questionnaire as objects will be dead after the questionnaire.
        krita.qApp.aboutToQuit.connect(self.saveData)  # This saves data after krita asks Yes/No/Cancel Modification questions.

        self.kritaInstance.action('view_show_canvas_only').triggered.connect(self.onShowCanvasOnly)

    def showhide(self):
        """"""
        if self.popupframe.isVisible():
            self.popupframe.setParent(None)
            self.popupframe.hide()
        else:
            # Center the frame on the cursor point.
            cursorPos = QCursor.pos()
            textureWidth, textureHeight = 512, 512
            cursorWidth, cursorHeight = 24, 24
            self.popupframe.move(cursorPos.x() - textureWidth//2,
                                 cursorPos.y() - textureHeight//2 - cursorHeight)
            mainWindow = Krita().instance().activeWindow().qwindow()
            self.popupframe.setParent(mainWindow)
            self.popupframe.show()
            self.popupframe.activateWindow()

    def saveData(self):
        """"""
        self.popupframe.saveData()

    def onShowCanvasOnly(self):
        """"""
        QTimer.singleShot(1, self.reparentPopup)  # Call After

    def reparentPopup(self):
        """"""
        # Need to keep the popup from getting covered up by the GLCanvas when
        # switching back and forth from canvas only view.
        if self.popupframe.isVisible():
            self.popupframe.setParent(None)
            self.popupframe.hide()
            self.popupframe.setParent(Krita().instance().activeWindow().qwindow())
            self.popupframe.show()
            self.popupframe.setFocus()


# Initialize and add the extension.
Scripter.addExtension(PopupPaletteExtension(Krita.instance()))
