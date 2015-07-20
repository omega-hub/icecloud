from math import *
from euclid import *
from omega import *
from omegaToolkit import *
from cyclops import *

import icecloud

# load the plot GPU program
shaderPath = "icecloud/shaders/";

plotProgram = ProgramAsset()
plotProgram.name = "plot"
plotProgram.vertexShaderName = shaderPath + "plot.vert"
plotProgram.fragmentShaderName = shaderPath + "plot.frag"
plotProgram.geometryShaderName = shaderPath + "plot.geom"
plotProgram.geometryOutVertices = 4
plotProgram.geometryInput = PrimitiveType.Points
plotProgram.geometryOutput = PrimitiveType.TriangleStrip
getSceneManager().addProgram(plotProgram)

pointScale = Uniform.create('pointScale', UniformType.Float, 1)

pointScale.setFloat(0.005)

PLOT_PANEL_COLOR = "#aaaaff"

plotWidth = 400
plotHeight = 400
container = Container.create(ContainerLayout.LayoutFree, icecloud.uiroot)
container.setStyle("fill: #202025; border: 1 {0}".format(PLOT_PANEL_COLOR))
#container.setAutosize(True)
container.setPosition(Vector2(10, 10))
container.setSize(Vector2(plotWidth, plotHeight))

enabled = False

# create camera
camera = getOrCreateCamera('selectionCamera')
camera.setEnabled(enabled)
camera.setFlag(Material.CameraDrawExplicitMaterials)
coutput = PixelData.create(plotWidth, plotHeight, PixelFormat.FormatRgba)

disabledCamera = getOrCreateCamera('disabledCamera')
disabledCamera.setEnabled(False)

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

img = Image.create(icecloud.uiroot)
img.setData(coutput)
img.setPosition(Vector2(0,0))
    
xboundsu = Uniform.create('unif_XBounds', UniformType.Vector2f, 1)
yboundsu = Uniform.create('unif_YBounds', UniformType.Vector2f, 1)
xu = Uniform.create('unif_XAxisId', UniformType.Int, 1)
yu = Uniform.create('unif_YAxisId', UniformType.Int, 1)


def setActiveDive(dive):
    print "active dive = " + dive.label