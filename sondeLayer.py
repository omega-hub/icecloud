from math import *
from euclid import *
from omega import *
from omegaToolkit import *
from cyclops import *

import csv

#sondeDropsFile = "SondeBasedBathymetry28-Mar-2013.csv"
sondeDropsFile = "SondeBasedBathymetry28-Mar-2013_10-Jul-2013.csv"
#sondeDropsFile = "SondeAndPickedBathymetry-19July13_MO_corrected.csv"
sondeDropsDir = "D:/Workspace/omegalib/apps/endurance"
#sondeDropsDir = "F:/ENDURANCE/test-dives/bonney_2009/vis/appData/endurance"

sondeDropsPath = sondeDropsDir + "/" + sondeDropsFile

oldSondeDrops = LineSet.create()
oldSondeDrops.setEffect('colored -e #f04040 -C')
newSondeDrops = LineSet.create()
newSondeDrops.setEffect('colored -e #40f040 -C')
pickedSondeDrops = LineSet.create()
pickedSondeDrops.setEffect('colored -e #f06020 -C')

sondeDrops = SceneNode.create('sondeDrops')
sondeDrops.addChild(oldSondeDrops)
sondeDrops.addChild(newSondeDrops)
sondeDrops.addChild(pickedSondeDrops)

# HACK: dive needs to be re-oriented
sondeDrops.pitch(radians(90))


numPoints = 0

def createSondeDrop(data, i, correctmh):
    stname = data[0]
    stx = float(data[2])
    sty = float(data[3])
    # UTM >> melthole coords
    if(correctmh):
        stx -= 1371377
        sty -= 435670
    depth = float(data[4])
    #print("Station " + stname + " X + " + str(stx) + " Y = " + str(sty))
    if(i < 186):
        stline = oldSondeDrops.addLine()
    else:
        stline = pickedSondeDrops.addLine()
        
    stline.setStart(Vector3(stx, sty, 0))
    stline.setEnd(Vector3(stx, sty, depth))
    stline.setThickness(0.5)
    if(i > 1000):
        stline.setThickness(1.5)
    stname = Text3D.create('fonts/arial.ttf', 2, stname)
    stname.setFacingCamera(getDefaultCamera())
    stname.setPosition(Vector3(stx + 1, sty, 2))
    stname.getMaterial().setDepthTestEnabled(False)
    stname.getMaterial().setTransparent(True)
    stname.setFixedSize(False)
    stname.setFontSize(1)

    #dpname = Text3D.create('fonts/arial.ttf', 2, str(depth))
    #dpname.setFacingCamera(getDefaultCamera())
    #dpname.setPosition(Vector3(stx + 2, sty, depth))
    #dpname.getMaterial().setDepthTestEnabled(False)
    #dpname.getMaterial().setTransparent(True)
    #dpname.setFixedSize(True)
    #dpname.setFontSize(60)

    dpsp = SphereShape.create(1, 2)
    dpsp.setEffect('colored -e #404090')
    dpsp.setPosition(Vector3(stx, sty, depth))

    sondeDrops.addChild(stname)
    #sondeDrops.addChild(dpname)
    sondeDrops.addChild(dpsp)

#-------------------------------------------------------------------------------	
def load():
    i = 0
    path = ofindFile(sondeDropsPath)
    with open(path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        headerLine = True
        for row in reader:
            if(not headerLine):
                createSondeDrop(row, i, True)
            else:
                headerLine = False
            i+=1
    global numPoints
    numPoints = i
