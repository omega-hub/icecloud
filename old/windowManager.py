# Handles icecloud windows, making sure the selected one is on top
# NOTE: windows need to have a dragger widget which is the one that gets
# registered for dragging, and a container widget which is the root container
# for the window.
from omegaToolkit import *

windows = {}

def addWindow(w):
    id = w.container.getName()
    windows[id] = w
    w.dragger.setActivateCommand('icecloud.windowManager.setActiveWindow("{0}")'.format(id))

def removeWindow(w):
    del windows[w.container.getName()]

# Keep track of active window
activeWindow = None
def setActiveWindow(id):
    global activeWindow
    if(activeWindow != None): activeWindow.container.setLayer(WidgetLayer.Middle)
    activeWindow = windows[id]
    activeWindow.container.setLayer(WidgetLayer.Front)
