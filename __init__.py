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
import topDown

# Import iceCloud classes in this namespace
from Dive import *
from DiveMenu import *
from LODInfo import *

getDefaultCamera().setNearFarZ(1, 10000)

# some options
panelBarHeight = 20
