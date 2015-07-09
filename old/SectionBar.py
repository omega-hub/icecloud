from omegaToolkit import *
from omega import *
from euclid import *
import icecloud

instance = None
topMargin = 40
sideMargin = 40
markerSize = 26
minSectionSize = 0.05

#-------------------------------------------------------------------------------
def onSectionBarDraw(w, camera, painter):
    if(instance.data != None):
        for s in instance.data.sections:
            sx = s.start * instance.width
            ex = s.end * instance.width
            color = Color(0.3, 1, 0.3, 1)
            ocolor = Color(0.1, 0.5, 0.1, 1)
            painter.drawRect(Vector2(sx,0), Vector2(ex - sx,instance.height), color)
            painter.drawRect(Vector2(sx,0), Vector2(4,instance.height), ocolor)
            painter.drawRect(Vector2(ex - 4,0), Vector2(4,instance.height), ocolor)
            
        if(instance.tempSelection == True and instance.section != None):
            sx = instance.section.start * instance.width
            ex = instance.section.end * instance.width
            color = Color(0.3, 0.3, 1, 1)
            painter.drawRect(Vector2(sx,0), Vector2(ex - sx,instance.height), color)


class SectionBar(Actor):
    #---------------------------------------------------------------------------
    def __init__(self, uiroot, panel, width, height):
        super(SectionBar, self).__init__("sectionBar")
        global instance
        instance = self
        self.uiroot = uiroot
        self.width = width
        self.height = height
        self.container = Container.create(ContainerLayout.LayoutFree, uiroot)
        self.container.setSize(Vector2(width + sideMargin * 2, height + topMargin))
        self.container.setAutosize(False)
        self.bar = Widget.create(self.container)
        self.bar.setSize(Vector2(width, height))
        self.bar.setPosition(Vector2(sideMargin, topMargin))
        self.bar.setStyle('fill: black; border: 2 white')
        self.bar.setPostDrawCallback(onSectionBarDraw)
        self.setEventsEnabled(True)
        self.setUpdateEnabled(True)
        self.tempSelection = False
        self.section = None
        self.data = None
        self.panel = panel
        
        # This var will be set to the SectionData to be displayed 
        self.data = None
        
        self.endMarker = Image.create(self.container)
        self.endMarker.setData(loadImage('icecloud/etc/end.png'))
        self.endMarker.setSize(Vector2(markerSize, markerSize))
        self.endMarker.setEnabled(True)
        self.endMarker.setDraggable(True)
        self.endMarker.setVisible(False)
        self.startMarker = Image.create(self.container)
        self.startMarker.setData(loadImage('icecloud/etc/start.png'))
        self.startMarker.setSize(Vector2(markerSize, markerSize))
        self.startMarker.setEnabled(True)
        self.startMarker.setDraggable(True)
        self.startMarker.setVisible(False)
        
    #---------------------------------------------------------------------------
    def onUpdate(self, frame, time, dt):
        dragging = False
        if(self.startMarker.isDragging()): dragging = True
        if(self.endMarker.isDragging()): dragging = True
        
        # If any section is dragging, update selected section
        if(dragging and self.section != None):
            start = (self.startMarker.getPosition().x - sideMargin + markerSize)/ self.width
            end = (self.endMarker.getPosition().x - sideMargin) / self.width
            self.updateSection(self.section, start, end)
    
    #---------------------------------------------------------------------------
    def onEvent(self):
        if(instance.data == None): return
        e = getEvent()
        if(e.isKeyDown(ord('p'))):
            # Turn temporary selection into section
            if(self.tempSelection == True and self.section != None):
                self.section = None
                self.tempSelection = False
                self.data.refresh()
        elif(e.isKeyDown(ord('o'))):
            if(self.tempSelection == False and self.section != None):
                self.data.sections.remove(self.section)
                self.section = None
                self.startMarker.setVisible(False)
                self.endMarker.setVisible(False)
                self.data.refresh()
        elif(e.getType() == EventType.Down):
            pos = Vector2(e.getPosition().x, e.getPosition().y)
            if(self.bar.hitTest(pos)):
                p2 = self.bar.transformPoint(pos)
                p2.x = p2.x / self.bar.getWidth()
                # Did we hit a section?
                for s in instance.data.sections:
                    if(p2.x > s.start and p2.x < s.end): 
                        # If a temp section is already allocated, remove it.
                        if(self.tempSelection == True and self.section != None):
                            self.data.sections.remove(self.section)
                            self.data.refresh()
                        self.tempSelection = False
                        self.select(s)
                        return
                # we haven't hit any section, create a temporary selection
                self.allocateSection(p2.x)
                
                
    #---------------------------------------------------------------------------
    def allocateSection(self, pos):
        start = 0
        end = 1
        # If a temp section is already allocated, remove it.
        if(self.tempSelection == True and self.section != None):
            self.data.sections.remove(self.section)
            
        # find bounds
        for s in instance.data.sections: 
            if(s.end < pos and s.end > start): start = s.end
            if(s.start > pos and s.start < end): end = s.start
        self.tempSelection = True
        self.section = icecloud.SectionInfo()
        self.section.setExtent(start, end)
        self.select(self.section)
        self.data.sections.append(self.section)
        self.data.refresh()
    
    #---------------------------------------------------------------------------
    def select(self, section):
        if(self.section != None):
            self.section.flags &= ~icecloud.SECTION_FLAGS_SELECTED
            
        self.startMarker.setVisible(True)
        self.endMarker.setVisible(True)
        self.section = section
        self.section.flags |= icecloud.SECTION_FLAGS_SELECTED
        # place the markers
        my = topMargin - markerSize
        sx = self.section.start * self.width + sideMargin - markerSize
        ex = self.section.end * self.width + sideMargin
        self.startMarker.setPosition(Vector2(sx, my))
        self.endMarker.setPosition(Vector2(ex, my))
        self.data.refresh()
        self.panel.onSectionSelected(section)

    #---------------------------------------------------------------------------
    def updateSection(self, section, start, end):
        if(start < 0): start = 0
        if(start > 1): start = 1
        if(end < 0): end = 0
        if(end > 1): end = 1
        # Only commit a section if it is larger than some minimum size.
        if(end - start > minSectionSize): 
            section.start = start
            section.end = end
        # Update the section (and markers)
        self.select(section)
        self.data.refresh()
        
                