import diveLayer
import os.path

from math import *
from cyclops import *
from omega import *
from euclid import *

# Table used to assign colors to dives.
colorTable = [
    [Color('#900000'), False],
    [Color('#009000'), False],
    [Color('#000090'), False],
    [Color('#909000'), False],
    [Color('#900090'), False],
    [Color('#009090'), False],
    [Color('#904040'), False],
    [Color('#009040'), False],
    [Color('#409040'), False],
    [Color('#404090'), False],
    [Color('#909040'), False],
    [Color('#009000'), False],
    [Color('#AFBD16'), False],
    [Color('#FFBD16'), False],
    [Color('#FF7F99'), False],
    [Color('#C09BFF'), False],
    [Color('#3FFFB5'), False],
    [Color('#8CFF00'), False],
    [Color('#AABF0D'), False]]


dives = {}

class Dive:
    #---------------------------------------------------------------------------
    def __init__(self, id, label, diveFile, poseFile, lod):
        dives[id] = self
        self.id = id
        self.label = label
        self.diveFile = diveFile
        self.poseFile = poseFile
        self.lod = lod
        self.loaded = False
        self.group = None
        self.poseModel = None
        self.poseObject = None
        self.pointsModel = None
        self.pointsObject = None
        self.diveInfo = None
        self.colorId = 0
        self.plotMaterial = []
        
        # Data ranges
        self.angleMin = 0
        self.angleMax = 0
        self.rangeMin = 0
        self.rangeMax = 0
        self.depthMin = 0
        self.depthMax = 0
        self.timestampMin = 0
        self.timestampMax = 0
        
    #---------------------------------------------------------------------------
    def loadPose(self):
        if(not os.path.exists(self.poseFile)):
            print("could not find pose file " + self.poseFile)
            return
        # see if we need to generate a binary file.
        poseBinaryFile = os.path.basename(self.poseFile)
        # make sure we remove all '.'from the filename since that is used as a 
        # special parameter separator in the binary point cloud loader
        poseBinaryFile = poseBinaryFile.replace(".", "-")
        # txt -> xyzb extension
        poseBinaryFile = diveLayer.poseBinaryCachePath + poseBinaryFile.replace("-txt", ".xyzb")
        if(not os.path.exists(poseBinaryFile)):
            print("creating pose binary file " + poseBinaryFile)
            diveLayer.generatePoseFile(self.poseFile, poseBinaryFile)
            
        # Now we have the pose binary file ready, load it.
        sm = getSceneManager()
        poseModel = ModelInfo()
        poseModel.name = self.id + "-pose"
        poseModel.path = poseBinaryFile
        poseModel.options = "1000 0:100:2 100:1000:20 1000:1000000:100"
        sm.loadModel(poseModel)
        self.poseModel = poseModel
        print("Pose model loaded: " + self.poseModel.name)

    #---------------------------------------------------------------------------
    def showPose(self):
        if(self.poseModel == None):
            self.loadPose()
        
        # Create pose object if we don't have one.
        if(self.poseObject == None):
            self.poseObject = StaticObject.create(self.poseModel.name)
            diveLayer.diveSceneRoot.addChild(self.poseObject)
            pointScale = Uniform.create('pointScale', UniformType.Float, 1)
            pointScale.setFloat(0.2)
            # setup pose file material
            mat = self.poseObject.getMaterial()
            mat.setProgram(diveLayer.poseBasicProgram.name)
            mat.attachUniform(pointScale)
            mat.setColor(Color('yellow'), Color('yellow'))
        
        self.poseObject.setVisible(True)
        
    #---------------------------------------------------------------------------
    def hidePose(self):
        if(self.poseObject != None):
            self.poseObject.setVisible(False)

    #---------------------------------------------------------------------------
    def loadPoints(self):
        # Now we have the pose binary file ready, load it.
        sm = getSceneManager()
        pointsModel = ModelInfo()
        pointsModel.name = self.id + "-points"
        pointsModel.path = self.diveFile
        pointsModel.options = self.lod.lodOptionString
        sm.loadModel(pointsModel)
        self.pointsModel = pointsModel

        # parse loader results and update attribute bounds
        self.diveInfo = eval(self.pointsModel.loaderOutput)
        minr = self.diveInfo['minR']
        maxr = self.diveInfo['maxR']
        ming = self.diveInfo['minG']
        maxg = self.diveInfo['maxG']
        minb = self.diveInfo['minB']
        maxb = self.diveInfo['maxB']

        # HACK: point cloud mode does not export depth bounds, so we hardcode
        # reasonable values for the ENDURANCE data here.
        minz = -10
        maxz = 60
        
        if(minr < diveLayer.attribMinBound.x): diveLayer.attribMinBound.x = minr
        if(ming < diveLayer.attribMinBound.y): diveLayer.attribMinBound.y = ming
        if(minb < diveLayer.attribMinBound.z): diveLayer.attribMinBound.z = minb	
        if(maxr > diveLayer.attribMaxBound.x): diveLayer.attribMaxBound.x = maxr
        if(maxg > diveLayer.attribMaxBound.y): diveLayer.attribMaxBound.y = maxg
        if(maxb > diveLayer.attribMaxBound.z): diveLayer.attribMaxBound.z = maxb
        # save ranges
        self.angleMin = minr
        self.angleMax = maxr
        self.rangeMin = ming
        self.rangeMax = maxg
        self.timestampMin = minb
        self.timestampMax = maxb
        self.depthMin = minz
        self.depthMax = maxz
        
        # Not sure this is the best position but do this here: update the attribute min/max
        # shader uniforms to the current bounds.
        diveLayer.minAttrib.setVector3f(Vector3(
            diveLayer.attribMinBound.x,
            diveLayer.attribMinBound.y,
            minz))

        diveLayer.maxAttrib.setVector3f(Vector3(
            diveLayer.attribMaxBound.x,
            diveLayer.attribMaxBound.y,
            maxz))
        
        print("Points loaded: " + self.pointsModel.name)

    #---------------------------------------------------------------------------
    def showPoints(self):
        if(self.pointsModel == None):
            self.loadPoints()
        
        # Create pose object if we don't have one.
        if(self.pointsObject == None):
            self.pointsObject = StaticObject.create(self.pointsModel.name)
            diveLayer.diveSceneRoot.addChild(self.pointsObject)
            # setup pose file material
            mat = self.pointsObject.getMaterial()
            mat.setProgram(diveLayer.pointsSectionProgram.name)
            mat.attachUniform(diveLayer.pointScale)
            mat.attachUniform(diveLayer.fieldMin)
            mat.attachUniform(diveLayer.fieldMax)
            mat.attachUniform(diveLayer.w1)
            mat.attachUniform(diveLayer.w2)
            mat.attachUniform(diveLayer.w3)
            mat.attachUniform(diveLayer.w4)
            #mat.attachUniform(diveLayer.minAttrib)
            #mat.attachUniform(diveLayer.maxAttrib)
            
            # HACK: dive needs to be re-oriented
            self.pointsObject.pitch(radians(90))
            if(len(self.plotMaterial) > 0):
                for m in self.plotMaterial:
                    self.pointsObject.addMaterial(m)
        
        cl = self.allocColor()
        self.colorId = cl[1]
        self.pointsObject.getMaterial().setColor(cl[0], Color(0,0,0,0))
        self.pointsObject.setVisible(True)

        # Update axes of 2D plots
        #PlotPanel.refreshPlotAxes()


    #---------------------------------------------------------------------------
    def hidePoints(self):
        if(self.pointsObject != None):
            self.pointsObject.setVisible(False)
            self.freeColor()
            # Update axes of 2D plots
            #PlotPanel.refreshPlotAxes()

    #---------------------------------------------------------------------------
    def allocColor(self):
        a = 0
        for cl in colorTable:
            if(cl[1] == False):
                cl[1] = True
                return (cl[0], a)
            a = a + 1
        print("Dive allocColor - no more colors available")
        return (Color('white'), -1)

    #---------------------------------------------------------------------------
    def freeColor(self):
        if(self.colorId != -1):
            colorTable[self.colorId][1] = False
        