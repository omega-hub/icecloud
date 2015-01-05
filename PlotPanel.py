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

# axis constants
AXIS_X = 0
AXIS_Y = 1
AXIS_DEPTH = 2
AXIS_ANGLE = 3
AXIS_RANGE = 4
AXIS_TIMESTAMP = 5

plotPanels = {}

PLOT_PANEL_COLOR = "#aaaaff"

# global function to update the axes of all plot panels. Used when dives are
# turned on/off
def refreshPlotAxes():
    for key, plot in plotPanels.iteritems():
        plot.setAxes(plot.xAxis, plot.yAxis)

# Temporary: add a button on the system menu to add a new plot.
mm = MenuManager.createAndInitialize()
bt = mm.getMainMenu().addButton('New Plot', 'icecloud.createPlotPanel()')
def createPlotPanel():
        p = PlotPanel(icecloud.uiroot, 400, 400, True)
        p.addDives(icecloud.dives.values())

class PlotPanel:
    #---------------------------------------------------------------------------
    def __init__(self, uiroot, width, height, e):
        self.dives = []
        self.uiroot = uiroot
        self.plotWidth = width
        self.plotHeight = height
        self.container = Container.create(ContainerLayout.LayoutFree, uiroot)
        self.container.setStyle("fill: #202025; border: 1 {0}".format(PLOT_PANEL_COLOR))
        self.container.setAutosize(False)
        self.container.setPosition(Vector2(0, 100))

        self.id = self.container.getName()
        plotPanels[self.id] = self
        panelInstance = 'icecloud.plotPanels["{0}"]'.format(self.id)

        self.dragger = Label.create(self.container)
        self.dragger.setText("Plot Panel")
        self.dragger.setColor(Color('black'))
        self.dragger.setStyle('fill: {0}; border: 1 {0}'.format(PLOT_PANEL_COLOR))
        self.dragger.setEnabled(True)
        self.dragger.setDraggable(True)
        self.dragger.setPosition(Vector2(0, -icecloud.panelBarHeight))
        self.dragger.setPinned(True)
        self.dragger.setSize(Vector2(width + 35, icecloud.panelBarHeight))
        self.dragger.setAutosize(False)

        icecloud.windowManager.addWindow(self)

        self.closeButton = Button.create(self.container)
        self.closeButton.setText('X')
        self.closeButton.setPosition(Vector2(width, -icecloud.panelBarHeight + 5))
        self.closeButton.getLabel().setColor(Color('black'))
        self.closeButton.setUIEventCommand(panelInstance + '.close()')
        self.closeButton.setLayer(WidgetLayer.Front)

        self.container.setSize(Vector2(width + 35,height + 65))

        # create camera
        self.camera = getOrCreateCamera('plotCamera-' + self.id)
        self.camera.setEnabled(e)
        self.coutput = PixelData.create(
            self.plotWidth, self.plotHeight, PixelFormat.FormatRgba)

        if(e):
            self.camera.getOutput(0).setReadbackTarget(self.coutput)
            self.camera.getOutput(0).setEnabled(True)
            self.camera.setFlag(Material.CameraDrawExplicitMaterials)
            self.camera.setPosition(200, 250, 600)
            self.camera.lookAt(Vector3(0,0,0), Vector3(0.7,0,-0.3))
            self.camera.setBackgroundColor(Color(0,0,0,1))
            self.camera.clearColor(True)
            dtc = self.camera.getCustomTileConfig()
            dtc.enabled = True
            dtc.topLeft = Vector3(-1, 0.5, -2)
            dtc.bottomLeft = Vector3(-1, -0.5, -2)
            dtc.bottomRight = Vector3(1, -0.5, -2)

        self.img = Image.create(self.container)
        self.img.setData(self.coutput)
        self.img.setPosition(Vector2(30,40))

        self.xboundsu = Uniform.create('unif_XBounds', UniformType.Vector2f, 1)
        self.yboundsu = Uniform.create('unif_YBounds', UniformType.Vector2f, 1)
        self.xu = Uniform.create('unif_XAxisId', UniformType.Int, 1)
        self.yu = Uniform.create('unif_YAxisId', UniformType.Int, 1)

        # create x axis selection combo boxes
        self.xButton = Button.create(self.container)
        self.xButton.setText("X Axis")
        self.xButton.setStyle('border-bottom: 4 black')
        self.xButton.setPosition(Vector2(5, 5))
        self.xButton.getLabel().setStyle('align: middle-left;')

        self.xButton.setUIEventCommand(panelInstance + '.showXAxisMenu()')
        self.xMenu = icecloud.menuManager.createMenu('{0}-xmenu'.format(self.id))

        self.xMenu.addButton('X', '{0}.xAxis = icecloud.AXIS_X; {0}.updateAxes()'.format(panelInstance))
        self.xMenu.addButton('Y', '{0}.xAxis = icecloud.AXIS_Y; {0}.updateAxes()'.format(panelInstance))
        self.xMenu.addButton('Depth', '{0}.xAxis = icecloud.AXIS_DEPTH; {0}.updateAxes()'.format(panelInstance))
        self.xMenu.addButton('Angle', '{0}.xAxis = icecloud.AXIS_ANGLE; {0}.updateAxes()'.format(panelInstance))
        self.xMenu.addButton('Range', '{0}.xAxis = icecloud.AXIS_RANGE; {0}.updateAxes()'.format(panelInstance))
        self.xMenu.addButton('Timestamp', '{0}.xAxis = icecloud.AXIS_TIMESTAMP; {0}.updateAxes()'.format(panelInstance))
        xmc = self.xMenu.getContainer()
        icecloud.uiroot.removeChild(xmc)
        self.container.addChild(xmc)

        # create y axis selection combo boxes
        self.yButton = Button.create(self.container)
        self.yButton.setText("Y Axis")
        self.yButton.setStyle('border-bottom: 4 black')
        self.yButton.setPosition(Vector2(50, 5))
        self.yButton.getLabel().setStyle('align: middle-left;')

        panelInstance = 'icecloud.plotPanels["{0}"]'.format(self.id)
        self.yButton.setUIEventCommand(panelInstance + '.showYAxisMenu()')
        self.yMenu = icecloud.menuManager.createMenu('{0}-ymenu'.format(self.id))

        self.yMenu.addButton('X', '{0}.yAxis = icecloud.AXIS_X; {0}.updateAxes()'.format(panelInstance))
        self.yMenu.addButton('Y', '{0}.yAxis = icecloud.AXIS_Y; {0}.updateAxes()'.format(panelInstance))
        self.yMenu.addButton('Depth', '{0}.yAxis = icecloud.AXIS_DEPTH; {0}.updateAxes()'.format(panelInstance))
        self.yMenu.addButton('Angle', '{0}.yAxis = icecloud.AXIS_ANGLE; {0}.updateAxes()'.format(panelInstance))
        self.yMenu.addButton('Range', '{0}.yAxis = icecloud.AXIS_RANGE; {0}.updateAxes()'.format(panelInstance))
        self.yMenu.addButton('Timestamp', '{0}.yAxis = icecloud.AXIS_TIMESTAMP; {0}.updateAxes()'.format(panelInstance))
        xmc = self.yMenu.getContainer()
        icecloud.uiroot.removeChild(xmc)
        self.container.addChild(xmc)

        # set default axes
        self.xAxis = AXIS_X
        self.yAxis = AXIS_Y

        self.xLabel = Label.create(self.container)
        self.xLabel.setText('Test')
        self.xLabel.setStyle('align: middle-center')
        self.xLabel.setFont('fonts/arial.ttf 20')
        self.xLabel.setAutosize(False)
        self.xLabel.setSize(Vector2(self.plotWidth, 20))
        self.xLabel.setCenter(Vector2(20 + self.plotWidth / 2, 50 + self.plotHeight))
        self.yLabel = Label.create(self.container)
        self.yLabel.setText('Test')
        self.yLabel.setStyle('align: middle-center')
        self.yLabel.setAutosize(False)
        self.yLabel.setSize(Vector2(self.plotHeight, 20))
        self.yLabel.setCenter(Vector2(20, 40 + self.plotHeight / 2))
        self.yLabel.setFont('fonts/arial.ttf 20')
        self.yLabel.setRotation(90)


        #getDefaultCamera().addChild(self.camera)

    #---------------------------------------------------------------------------
    def close(self):
        del icecloud.plotPanels[self.id]
        self.uiroot.removeChild(self.container)
        deleteCamera(self.camera)
        icecloud.windowManager.removeWindow(self)


    #---------------------------------------------------------------------------
    def addDives(self, dives):
        self.dives = dives
        for d in self.dives:
            # attach the plot material to each dive.
            material = Material.create()
            material.setCamera(self.camera)
            material.setProgram('plot')
            material.attachUniform(pointScale)
            material.attachUniform(d.sectionData.numSectionsU)
            material.attachUniform(d.sectionData.sectionBoundsU)
            material.attachUniform(d.sectionData.sectionFlagsU)
            material.attachUniform(d.sectionData.sectionMinAttribU)
            material.attachUniform(d.sectionData.sectionMaxAttribU)
            material.attachUniform(self.xboundsu)
            material.attachUniform(self.yboundsu)
            material.attachUniform(self.xu)
            material.attachUniform(self.yu)
            # If dive points are already loaded, attach material here,
            # otherwise save it to dive to allow it to be attached later
            d.plotMaterial.append(material)
            if(d.pointsObject != None):
                d.pointsObject.addMaterial(material)

        self.setAxes(AXIS_X, AXIS_Y)

    #---------------------------------------------------------------------------
    def setAxes(self, x, y):
        dsr = icecloud.diveLayer.diveSceneRoot
        mina = icecloud.diveLayer.attribMinBound
        maxa = icecloud.diveLayer.attribMaxBound

        tmin = 10000000000
        tmax = -10000000000

        # Timestamp bounds are adjusted based on what dives are on
        for key,d in icecloud.dives.iteritems():
            if(d.pointsObject != None and d.pointsObject.isVisible()):
                dtmin = d.diveInfo['minB']
                dtmax = d.diveInfo['maxB']
                tmin = min(tmin, dtmin)
                tmax = max(tmax, dtmax)

        #print('tbounds = {0}   {1}'.format(tmin, tmax))

        # hack, hard coded bounds for ENDURANCE
        if(x == AXIS_X):
            xmin = -750 #dsr.getBoundMinimum().x
            xmax = 750 # dsr.getBoundMaximum().x
            self.xLabel.setText('UTM X (from melthole)')
        elif(x == AXIS_Y):
            xmin = -450 #dsr.getBoundMinimum().y
            xmax = 1750 #dsr.getBoundMaximum().y
            self.xLabel.setText('UTM Y (from melthole)')
        elif(x == AXIS_DEPTH):
            xmin = -10 #dsr.getBoundMinimum().z
            xmax = 60 #dsr.getBoundMaximum().z
            self.xLabel.setText('Depth')
        elif(x == AXIS_ANGLE):
            xmin = mina.x
            xmax = maxa.x
            self.xLabel.setText('Beam Angle')
        elif(x == AXIS_RANGE):
            xmin = mina.y
            xmax = maxa.y
            self.xLabel.setText('Beam Range')
        elif(x == AXIS_TIMESTAMP):
            xmin = tmin #mina.z
            xmax = tmax #maxa.z
            self.xLabel.setText('Timestamp')

        if(y == AXIS_X):
            ymin = -750 #dsr.getBoundMinimum().x
            ymax = 750 #dsr.getBoundMaximum().x
            self.yLabel.setText('UTM X (from melthole)')
        elif(y == AXIS_Y):
            ymin = -450 #dsr.getBoundMinimum().y
            ymax = 1750 #dsr.getBoundMaximum().y
            self.yLabel.setText('UTM Y (from melthole)')
        elif(y == AXIS_DEPTH):
            ymin = -10 #dsr.getBoundMinimum().z
            ymax = 60 #dsr.getBoundMaximum().z
            self.yLabel.setText('Depth')
        elif(y == AXIS_ANGLE):
            ymin = mina.x
            ymax = maxa.x
            self.yLabel.setText('Beam Angle')
        elif(y == AXIS_RANGE):
            ymin = mina.y
            ymax = maxa.y
            self.yLabel.setText('Beam Range')
        elif(y == AXIS_TIMESTAMP):
            ymin = mina.z
            ymax = maxa.z
            self.yLabel.setText('Timestamp')

        self.xboundsu.setVector2f(Vector2(xmin, xmax))
        self.yboundsu.setVector2f(Vector2(ymin, ymax))
        self.xu.setInt(x)
        self.yu.setInt(y)

    #---------------------------------------------------------------------------
    def showXAxisMenu(self):
        xmc = self.xMenu.getContainer()
        xmc.setPosition(self.xButton.getPosition() + Vector2(0, self.xButton.getHeight()))
        self.xMenu.show()
        self.yMenu.hide()

    #---------------------------------------------------------------------------
    def showYAxisMenu(self):
        xmc = self.yMenu.getContainer()
        xmc.setPosition(self.yButton.getPosition() + Vector2(0, self.yButton.getHeight()))
        self.yMenu.show()
        self.xMenu.hide()

    #---------------------------------------------------------------------------
    def updateAxes(self):
        self.xMenu.hide()
        self.yMenu.hide()
        self.setAxes(self.xAxis, self.yAxis)
