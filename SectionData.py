from omega import *
from cyclops import *
from euclid import *
import json
import os

SECTION_FLAGS_NONE = 0
SECTION_FLAGS_SELECTED = 1

MAX_SECTIONS = 14

mc = getMissionControlClient()

#-------------------------------------------------------------------------------
class SectionInfo:
    def __init__(self):
        self.angleMin = 0
        self.angleMax = 0
        self.rangeMin = 0
        self.rangeMax = 0
        self.depthMin = 0
        self.depthMax = 0
        self.start = 0
        self.end = 0
        self.flags = 0
        
    #---------------------------------------------------------------------------
    def reset(self, dive):
        """Resets this SectionInfo to cover the full extents of the specified dive"""
        self.angleMin = dive.angleMin
        self.angleMax = dive.angleMax
        self.rangeMin = dive.rangeMin
        self.rangeMax = dive.rangeMax
        self.depthMin = dive.depthMin
        self.depthMax = dive.depthMax
        #print("depth {0} {1}".format(self.depthMin, self.depthMax))
        self.start = 0
        self.end = 1

    #---------------------------------------------------------------------------
    def setExtent(self, start, end):
        """Sets the extent of this section using normalized start/end points"""
        self.start =  start
        self.end = end

#-------------------------------------------------------------------------------
class SectionJSONCodec(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SectionInfo):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

def SectionJSONCodec_decode(dct):
    s = SectionInfo()
    s.__dict__ = dct
    return s
        

#-------------------------------------------------------------------------------
class SectionData:
    def __init__(self):
        self.sections = [0]
        
        #Uniforms
        self.numSectionsU = Uniform.create('unif_NumSections', UniformType.Int, 1)
        self.sectionBoundsU = Uniform.create('unif_SectionBounds', UniformType.Vector2f, MAX_SECTIONS)
        self.sectionMinAttribU = Uniform.create('unif_MinAttrib', UniformType.Vector3f, MAX_SECTIONS)
        self.sectionMaxAttribU = Uniform.create('unif_MaxAttrib', UniformType.Vector3f, MAX_SECTIONS)
        self.sectionFlagsU = Uniform.create('unif_SectionFlags', UniformType.Int, MAX_SECTIONS)
        self.dive = None
        self.modified = False
    
    #---------------------------------------------------------------------------
    def refresh(self, sendUpdate = True):
        self.modified = True
        # Upload section data to the gpu. If we are not attached to a dive, there
        # is nothing to do here.
        if(self.dive != None and self.dive.pointsObject != None):
            if(self.numSectionsU == None or 
            self.numSectionsU.getInt() != len(self.sections)):
                self.numSectionsU.setInt(len(self.sections))
                # Attach the uniforms to the dive points material
                m = self.dive.pointsObject.getMaterial()
                m.attachUniform(self.numSectionsU)
                m.attachUniform(self.sectionBoundsU)
                m.attachUniform(self.sectionFlagsU)
                m.attachUniform(self.sectionMinAttribU)
                m.attachUniform(self.sectionMaxAttribU)
                
            a = 0
            self.numSectionsU.setInt(len(self.sections))
            for s in self.sections:
                tl = self.dive.timestampMax - self.dive.timestampMin
                tMin = self.dive.timestampMin + tl * s.start
                tMax = self.dive.timestampMin + tl * s.end
                self.sectionBoundsU.setVector2fElement(Vector2(tMin, tMax), a)
                self.sectionFlagsU.setIntElement(s.flags, a)
                self.sectionMinAttribU.setVector3fElement(Vector3(s.angleMin, s.rangeMin, s.depthMin), a)
                self.sectionMaxAttribU.setVector3fElement(Vector3(s.angleMax, s.rangeMax, s.depthMax), a)
                a = a + 1

        # If we are connected to a mission control server, send refresh update
        if(mc != None and sendUpdate):
            data = []
            data.append(len(self.sections))
            for s in self.sections:
                data.append(s.start)
                data.append(s.end)
                data.append(s.angleMin)
                data.append(s.angleMax)
                data.append(s.rangeMin)
                data.append(s.rangeMax)
                data.append(s.depthMin)
                data.append(s.depthMax)

            c = 'icecloud.dives["{0}"].sectionData.remoteUpdate({1})'.format(self.dive.id, data)
            mc.postCommand(c)
                
    #---------------------------------------------------------------------------
    def remoteUpdate(self, data):
        #print('received sections: {0}'.format(data[0]))
        self.sections = []
        s = 8
        for a in range(0, data[0]):
            o = s * a + 1
            si = SectionInfo()
            si.setExtent(data[o], data[o + 1])
            si.angleMin = data[o + 2]
            si.angleMax = data[o + 3]
            si.rangeMin = data[o + 4]
            si.rangeMax = data[o + 5]
            si.depthMin = data[o + 6]
            si.depthMax = data[o + 7]
            self.sections.append(si)
        self.refresh(False)


    #---------------------------------------------------------------------------
    def jsonEncode(self):
        return json.dumps(self.sections, cls=SectionJSONCodec)
        
    #---------------------------------------------------------------------------
    def jsonDecode(self, str):
        self.sections = json.loads(str, object_hook=SectionJSONCodec_decode)
        
    #---------------------------------------------------------------------------
    def save(self,filename):
        print("saving " + filename)
        f = open(filename, 'w')
        f.write(self.jsonEncode())
        f.close()

    #---------------------------------------------------------------------------
    def load(self,filename):
        if(os.path.isfile(filename)):
            f = open(filename, 'r')
            json = f.read()
            self.jsonDecode(json)
            f.close()
        