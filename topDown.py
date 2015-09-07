from math import *
from euclid import *
from omega import *
from omegaToolkit import *
from cyclops import *

import icecloud

cmd = "icecloud.topDown.setEnabled(%value%)"
mm = icecloud.menuManager.getMainMenu()
btn = mm.addButton("Top Down Mode", cmd)
btn.getButton().setCheckable(True)
btn.getButton().setChecked(False)

cameraP = None
cameraO = None

originalStereoMode = None


#------------------------------------------------------------------------------
def setEnabled(value):
    global cameraP
    global cameraO
    global originalStereoMode
    c = getDefaultCamera()
    dcfg = getDisplayConfig()
    c.setControllerEnabled(not value)
    if(value):
        # save current camera info
        cameraP = c.getPosition()
        cameraO = c.getOrientation()

        c.setPosition(200, 2500, 600)
        c.lookAt(Vector3(0,0,0), Vector3(0.7,0,-0.3))
        c.setTrackingEnabled(False)
        originalStereoMode = dcfg.stereoMode
        dcfg.stereoMode = StereoMode.Mono
    else:
        # restore camera
        c.setPosition(cameraP)
        c.setOrientation(cameraO)
        c.setTrackingEnabled(True)
        dcfg.stereoMode = originalStereoMode

#------------------------------------------------------------------------------
def onEvent():
    e = getEvent()


setEventFunction(onEvent)