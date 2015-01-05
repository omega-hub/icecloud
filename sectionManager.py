from omega import *
import icecloud

# stores dives whose sections we want to manager
dives = []

lastUpdateTime = 0
updateInterval = 1

#------------------------------------------------------------------------------
def updateSections():
    global dives
    for d in dives:
        if d.sectionData != None and d.sectionData.modified:
            d.sectionData.modified = False
            d.sectionData.save(d.id + ".json")


#------------------------------------------------------------------------------
def onUpdate(frame, time, dt):
    global lastUpdateTime
    global updateInterval

    if(time - lastUpdateTime > updateInterval):
        #print("section updating at " + str(time))
        updateSections()
        lastUpdateTime = time

setUpdateFunction(onUpdate)
