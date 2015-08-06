from omega import *
from euclid import *
from cyclops import *
import csv
import struct
import sys

# Path to the directory that will store the binary versions of the pose files.
poseBinaryCachePath = "./"

# Decimation used by the text -> binary pose file converter
poseDecimation = 10

# Position bias used by pose text->binary data converter. Used to convert i.e.
# from UTM coodrdinates to a local reference frame.
poseTranslation = [ 1371377, 435670, 0 ]

# Root scene node for dive objects. By default this is a node attached to the scene 
# root, but user can set it to something else
diveSceneRoot = SceneNode.create("diveRoot")

# Stores the currently active dive
activeDive = None

#------------------------------------------------------------------------------
# Load GLSL shaders used to render dive point clouds
shaderPath = "icecloud/shaders/";

pointsSectionProgram = ProgramAsset()
pointsSectionProgram.name = "points-section"
pointsSectionProgram.vertexShaderName = shaderPath + "sonarPoint.vert"
pointsSectionProgram.fragmentShaderName = shaderPath + "sonarPoint.frag"
pointsSectionProgram.geometryShaderName = shaderPath + "sonarPoint.geom"
pointsSectionProgram.geometryOutVertices = 4
pointsSectionProgram.geometryInput = PrimitiveType.Points
pointsSectionProgram.geometryOutput = PrimitiveType.TriangleStrip
getSceneManager().addProgram(pointsSectionProgram)

pointsActiveProgram = ProgramAsset()
pointsActiveProgram.name = "points-active"
pointsActiveProgram.vertexShaderName = shaderPath + "sonarPoint-active.vert"
pointsActiveProgram.fragmentShaderName = shaderPath + "sonarPoint.frag"
pointsActiveProgram.geometryShaderName = shaderPath + "sonarPoint.geom"
pointsActiveProgram.geometryOutVertices = 4
pointsActiveProgram.geometryInput = PrimitiveType.Points
pointsActiveProgram.geometryOutput = PrimitiveType.TriangleStrip
getSceneManager().addProgram(pointsActiveProgram)


pointScale = Uniform.create('pointScale', UniformType.Float, 1)
fieldMin = Uniform.create('unif_FieldMin', UniformType.Float, 1)
fieldMax = Uniform.create('unif_FieldMax', UniformType.Float, 1)

w1 = Uniform.create('unif_W1', UniformType.Float, 1)
w2 = Uniform.create('unif_W2', UniformType.Float, 1)
w3 = Uniform.create('unif_W3', UniformType.Float, 1)
w4 = Uniform.create('unif_W4', UniformType.Float, 1)

fieldMin.setFloat(10)
fieldMax.setFloat(50.0)
pointScale.setFloat(0.1)

w1.setFloat(1)
w2.setFloat(0)
w3.setFloat(0)
w4.setFloat(0)

# These variables store the bounds of the three attributes associated with each dive.
attribMinBound = Vector3(sys.float_info.max,sys.float_info.max, sys.float_info.max)
attribMaxBound = Vector3(-sys.float_info.max,-sys.float_info.max, -sys.float_info.max)

minAttrib = Uniform.create('unif_AttribMinBound', UniformType.Vector3f, 1)
maxAttrib = Uniform.create('unif_AttribMaxBound', UniformType.Vector3f, 1)

#-------------------------------------------------------------------------------
# This is the program used to display pose data
poseBasicProgram = ProgramAsset()
poseBasicProgram.name = "pose-basic"
poseBasicProgram.vertexShaderName = shaderPath + "posePoint.vert"
poseBasicProgram.fragmentShaderName = shaderPath +  "posePoint.frag"
poseBasicProgram.geometryShaderName = shaderPath + "posePoint.geom"
poseBasicProgram.geometryOutVertices = 4
poseBasicProgram.geometryInput = PrimitiveType.Points
poseBasicProgram.geometryOutput = PrimitiveType.TriangleStrip
getSceneManager().addProgram(poseBasicProgram)

#-------------------------------------------------------------------------------
# Read telemetry CSV and generate binary file
def generatePoseFile(infilename, outfilename):
    f = open(infilename) # input file
    reader = csv.reader(f, delimiter="\t")

    file = open(outfilename, 'wb') # output file

    curRow = 0
    for row in reader:
        row = row[0].split(" ")
        # timestamp orientation pose
        # timestamp (s) is time since 00:00, 1970 Jan 01
        # orientation (rad) is [pitch, roll, yaw]
        # pose (m) is [UTM North, UTM East, Depth from 2008 Dec 10 lake level]
        if( curRow > 4 and curRow % poseDecimation == 0):
            timestamp = 0;
            fields = [0,0,0,0,0,0,0];
            curField = 0;
            for col in row:
                if( len(col) > 0 ):
                    fields[curField] = col;
                    curField += 1;
            
            # shift fields to x, y, z, rx, ry, rz, timestamp
            x =  float(fields[4]) - float(poseTranslation[0])
            y =  float(fields[5]) - float(poseTranslation[1])
            z =  float(fields[6]) - float(poseTranslation[2])

            fields[4] = x;
            fields[5] = -z;
            fields[6] = y;
            
            dataBytes = struct.pack('ddddddd', float(fields[4]), float(fields[5]), float(fields[6]), float(fields[1]), float(fields[2]), float(fields[3]), float(fields[0]) )
            file.write(dataBytes)
        curRow += 1
    f.close()
    file.close()
