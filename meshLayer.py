from math import *
from euclid import *
from omega import *
from omegaToolkit import *
from cyclops import *

import icecloud

# create a light to illuminate the meshes
light1 = Light.create()
light1.setPosition(-1, 3, 1)
light1.setColor(Color('white'))
light1.setAmbient(Color(0.1,0.1,0.1,1))
#light1.setAttenuation(1, 0.002, 0)
getDefaultCamera().addChild(light1)

meshRoot = SceneNode.create('meshes')
# hacky: meshes need to be rotated.
meshRoot.pitch(radians(90))

mesh = {}

#------------------------------------------------------------------------------
def loadMesh(name, file):
    model = ModelInfo()
    model.name = name
    model.path = file
    model.optimize = True
    model.generateNormals = True
    model.normalizeNormals = True
    cmd = "icecloud.meshLayer.onMeshLoaded('{0}')".format(name)
    icecloud.scene.loadModelAsync(model, cmd)

#------------------------------------------------------------------------------
def onMeshLoaded(name):
    global mesh
    mesh[name] = StaticObject.create(name)
    mesh[name].setEffect("icecloud/shaders/contour -e lime -d #505050 -C -t")
    mesh[name].setVisible(False)
    meshRoot.addChild(mesh[name])

    mm = icecloud.menuManager.getMainMenu()
    cmd = "icecloud.meshLayer.mesh['{0}'].setVisible(%value%)".format(name)
    btn = mm.addButton("{0} visible".format(name), cmd)
    btn.getButton().setCheckable(True)
    btn.getButton().setChecked(False)
