from math import *
from euclid import *
from omega import *
from omegaToolkit import *
from cyclops import *

import icecloud

# load the plot GPU program
shaderPath = "icecloud/shaders/";

plotProgram = ProgramAsset()
plotProgram.name = "plot2"
plotProgram.vertexShaderName = shaderPath + "plot.vert"
plotProgram.fragmentShaderName = shaderPath + "plot.frag"
plotProgram.geometryShaderName = shaderPath + "plot.geom"
plotProgram.geometryOutVertices = 4
plotProgram.geometryInput = PrimitiveType.Points
plotProgram.geometryOutput = PrimitiveType.TriangleStrip
getSceneManager().addProgram(plotProgram)

# Create the material and uniforms used to draw the selection bar
xboundsu = Uniform.create('unif_XBounds', UniformType.Vector2f, 1)
yboundsu = Uniform.create('unif_YBounds', UniformType.Vector2f, 1)
xu = Uniform.create('unif_XAxisId', UniformType.Int, 1)
yu = Uniform.create('unif_YAxisId', UniformType.Int, 1)

pointScale = Uniform.create('pointScale', UniformType.Float, 1)
pointScale.setFloat(0.005)

selectionPlotMaterial = Material.create()
selectionPlotMaterial.setProgram('plot2')
selectionPlotMaterial.attachUniform(pointScale)
selectionPlotMaterial.attachUniform(xboundsu)
selectionPlotMaterial.attachUniform(yboundsu)
selectionPlotMaterial.attachUniform(xu)
selectionPlotMaterial.attachUniform(yu)
selectionPlotMaterial.setDepthTestEnabled(False)

activeDive = None


PLOT_PANEL_COLOR = "#aaaaff"

# axis constants
AXIS_X = 0
AXIS_Y = 1
AXIS_DEPTH = 2
AXIS_ANGLE = 3
AXIS_RANGE = 4
AXIS_TIMESTAMP = 5

plotWidth = 400
plotHeight = 160
container = Container.create(ContainerLayout.LayoutFree, icecloud.uiroot)
container.setStyle("fill: #202025; border: 1 {0}".format(PLOT_PANEL_COLOR))
#container.setAutosize(True)
container.setPosition(Vector2(16, 16))
container.setSize(Vector2(plotWidth + 2, plotHeight + 2))

enabled = True

# create camera
camera = getOrCreateCamera('selectionCamera')
camera.setEnabled(enabled)
coutput = PixelData.create(plotWidth, plotHeight, PixelFormat.FormatRgba)

if(enabled):
    camera.getOutput(0).setReadbackTarget(coutput)
    camera.getOutput(0).setEnabled(True)
    camera.setFlag(Material.CameraDrawExplicitMaterials)
    camera.setPosition(200, 250, 600)
    camera.lookAt(Vector3(0,0,0), Vector3(0.7,0,-0.3))
    camera.setBackgroundColor(Color(0,0,0,1))
    camera.clearColor(True)
    dtc = camera.getCustomTileConfig()
    dtc.enabled = True
    dtc.topLeft = Vector3(-1, 0.5, -2)
    dtc.bottomLeft = Vector3(-1, -0.5, -2)
    dtc.bottomRight = Vector3(1, -0.5, -2)
    selectionPlotMaterial.setCamera(camera)

img = Image.create(icecloud.uiroot)
img.setData(coutput)
img.setPosition(Vector2(0,0))

def setActiveDive(dive):
    global activeDive
    if(activeDive != None):
        activeDive.pointsObject.removeMaterial(selectionPlotMaterial)
    activeDive = dive
    if(activeDive != None):
        activeDive.pointsObject.addMaterial(selectionPlotMaterial)
        tmin = activeDive.diveInfo['minB']
        tmax = activeDive.diveInfo['maxB']
        
        xboundsu.setVector2f(Vector2(tmin, tmax))
        print("bounds: {0}  {1}".format(tmin, tmax))
        # Hardcoded depth bounds
        yboundsu.setVector2f(Vector2(-10, 60))
        xu.setInt(AXIS_TIMESTAMP)
        yu.setInt(AXIS_DEPTH)
    
    