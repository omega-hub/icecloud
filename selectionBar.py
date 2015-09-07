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
pointScale.setFloat(0.002)

selectionPlotMaterial = Material.create()
selectionPlotMaterial.setProgram('plot2')
selectionPlotMaterial.attachUniform(pointScale)
selectionPlotMaterial.attachUniform(xboundsu)
selectionPlotMaterial.attachUniform(yboundsu)
selectionPlotMaterial.attachUniform(xu)
selectionPlotMaterial.attachUniform(yu)
selectionPlotMaterial.setDepthTestEnabled(False)
selectionPlotMaterial.setAdditive(True)
selectionPlotMaterial.setTransparent(True)

activeDive = None


PLOT_PANEL_COLOR = "#aaaaff"
SELECTOR_COLOR = "#8888ffff"

# axis constants
AXIS_X = 0
AXIS_Y = 1
AXIS_DEPTH = 2
AXIS_ANGLE = 3
AXIS_RANGE = 4
AXIS_TIMESTAMP = 5

plotWidth = 2000
plotHeight = 480
container = Container.create(ContainerLayout.LayoutFree, icecloud.uiroot)
container.setStyle("fill: #000000; border: 1 {0}".format(PLOT_PANEL_COLOR))
container.setAutosize(True)
container.setPosition(Vector2(16, 16))
container.setEnabled(False)
#container.setScale(4)
container.setCenter(Vector2(2000,2000))
container.setDraggable(True)

# create camera
camera = getOrCreateCamera('selectionCamera')
camera.setEnabled(True)
coutput = PixelData.create(plotWidth, plotHeight, PixelFormat.FormatRgba)

camera.getOutput(0).setReadbackTarget(coutput)
camera.getOutput(0).setEnabled(True)
camera.setFlag(Material.CameraDrawExplicitMaterials)
camera.setBackgroundColor(Color(0,0,0,1))
camera.clearColor(True)
camera.setCullingEnabled(False)
# Update bar every 2 seconds.
camera.setMaxFps(0.5)
selectionPlotMaterial.setCamera(camera)

img = Image.create(container)
img.setData(coutput)
offs = container.getMargin() + container.getPadding() / 2
img.setPosition(Vector2(offs,offs))

selector = Widget.create(container)
selector.setStyle('fill: {0}'.format(SELECTOR_COLOR))
selector.setAlpha(0.5)
selector.setLayer(WidgetLayer.Front)
selector.setSize(Vector2(100, plotHeight))
selector.setPosition(Vector2(offs,offs))
selectionStart = 0
selectionEnd = 0

diveName = Label.create(container)
diveName.setLayer(WidgetLayer.Front)
diveName.setPosition(Vector2(offs,offs))
diveName.setText("")

def setActiveDive(dive):
    global activeDive
    if(activeDive != None):
        activeDive.pointsObject.removeMaterial(selectionPlotMaterial)
    activeDive = dive
    if(activeDive != None):
        diveName.setText(activeDive.label)
        activeDive.pointsObject.addMaterial(selectionPlotMaterial)
        tmin = activeDive.diveInfo['minB']
        tmax = activeDive.diveInfo['maxB']
        
        xboundsu.setVector2f(Vector2(tmin, tmax))
        print("bounds: {0}  {1}".format(tmin, tmax))
        # Hardcoded depth bounds
        yboundsu.setVector2f(Vector2(-10, 60))
        xu.setInt(AXIS_TIMESTAMP)
        yu.setInt(AXIS_DEPTH)
    
    
def setSelection(start, end):
    global selectionStart
    global selectionEnd
    global selection
    selectionStart = start
    selectionEnd = end
    
    if(activeDive != None):
        activeDive.selection.setVector2f(Vector2(selectionStart, selectionEnd))
        mcc = getMissionControlClient()
        if(mcc): 
            mcc.postCommand('@endurance*:icecloud.dives["{0}"].setActive(True)'.format(activeDive.id))
            mcc.postCommand('@endurance*:icecloud.dives["{0}"].selection.setVector2f(Vector2({1}, {2}))'.format(
                activeDive.id, selectionStart, selectionEnd))
    
    # Adjust selection widget
    ssx = selectionStart * plotWidth
    sex = selectionEnd * plotWidth
    selector.setPosition(Vector2(ssx + offs, offs))
    selector.setWidth(sex - ssx)

setSelection(0.0, 0.0)

#-------------------------------------------------------------------------------
# Selection bar interaction
selectionMoveSpeed = 0
selectionSizeSpeed = 0

def onEvent():
    global selectionMoveSpeed
    global selectionSizeSpeed 
    e = getEvent()
    if(e.isButtonDown(EventFlags.ButtonLeft)):
        selectionMoveSpeed = -0.2
    elif(e.isButtonDown(EventFlags.ButtonRight)):
        selectionMoveSpeed = 0.2
    elif(e.isButtonDown(EventFlags.ButtonUp)):
        selectionSizeSpeed = 0.2
    elif(e.isButtonDown(EventFlags.ButtonDown)):
        selectionSizeSpeed = -0.2
    elif(e.getType() == EventType.Up):
        selectionMoveSpeed = 0.0
        selectionSizeSpeed = 0.0
    
def onUpdate(frame, time, dt):
    global selectionMoveSpeed
    global selectionSizeSpeed 
    global selectionStart
    global selectionEnd
    
    size = selectionEnd - selectionStart
    center = selectionStart + size / 2
        
    center += selectionMoveSpeed * dt
    size += selectionSizeSpeed * dt
    
    if(size <= 0.01): size = 0.01
    if(center < 0 ): center = 0
    if(center > 1): center = 1
    
    start = center - size / 2
    end = center + size / 2
    
    setSelection(start, end)
    
    # Animate selection color
    if(activeDive != None):
        cv = abs(sin(time * 2))
        sc = Color(1 - cv, 1, 0, 1)
        activeDive.selectionColor.setColor(sc)
    

setEventFunction(onEvent)
setUpdateFunction(onUpdate)