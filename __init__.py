# setup points loader
from omegaToolkit import *
import cyclops
import pointCloud

scene = cyclops.getSceneManager()
scene.addLoader(pointCloud.TextPointsLoader())
scene.addLoader(pointCloud.BinaryPointsLoader())

uiManager = UiModule.createAndInitialize()
uiroot = uiManager.getUi()
menuManager = MenuManager.createAndInitialize()
sectionPanel = None

# Import iceCloud function modules in this namespace
import diveLayer
import sondeLayer
import meshLayer
import sectionManager
import topDown
import windowManager

# Import iceCloud classes in this namespace
from Dive import *
from DiveMenu import *
from LODInfo import *
from SectionData import *
from SectionBar import *
from SectionPanel import *
from PlotPanel import *

getDefaultCamera().setNearFarZ(1, 10000)

# some options
panelBarHeight = 20
