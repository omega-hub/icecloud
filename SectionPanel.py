from omegaToolkit import *
from omega import *
from euclid import *
import icecloud

class SectionPanel:
    #---------------------------------------------------------------------------
    def __init__(self, uiroot, width):
        icecloud.sectionPanel = self
        
        s = 1.0#Platform.scale
        
        self.uiroot = uiroot
        self.width = width * s
        self.barHeight = 64 * s
        self.container = Container.create(ContainerLayout.LayoutFree, uiroot)
        self.container.setStyle("fill: #202025; border: 1 #aaaaff")
        self.container.setAutosize(False)
        self.container.setScale(Platform.scale)

        self.dragger = Label.create(self.container)
        self.dragger.setText("Section Panel")
        self.dragger.setColor(Color('black'))
        self.dragger.setStyle('fill: #aaaaff')
        self.dragger.setEnabled(True)
        self.dragger.setDraggable(True)
        
        dsize = Vector2(width + icecloud.sideMargin * 2 * s, icecloud.panelBarHeight * s)
        self.dragger.setSize(dsize)
        self.dragger.setPinned(True)
        self.dragger.setAutosize(False)
        
        icecloud.windowManager.addWindow(self)
        
        self.divesButton = Button.create(self.container)
        self.divesButton.setText("Select Dive")
        self.divesButton.setStyle('border-bottom: 4 black')
        self.divesButton.setPosition(Vector2(width - 40 * s, self.dragger.getHeight() + 5 * s))
        self.divesButton.getLabel().setStyle('align: middle-left;')
        evt = 'icecloud.sectionPanel.showDivesMenu()';
        self.divesButton.setUIEventCommand(evt)
        
        
        self.bar = icecloud.SectionBar(self.container, self, width, self.barHeight)
        self.bar.container.setPosition(Vector2(0, 50 * s))
        
        self.diveMenu = icecloud.menuManager.createMenu('sectionDives')
        icecloud.uiroot.removeChild(self.diveMenu.getContainer())
        self.container.addChild(self.diveMenu.getContainer())
        
        # Dive menu stuff
        self.groups = {}
        self.groupMenuButtons = {}
        self.dives = {}
        self.dive = None

        
        # Dive params stuff
        self.paramButton = Button.create(self.container)
        self.paramButton.setText("Active Parameter")
        self.paramButton.setStyle('border-bottom: 4 black')
        sbc = self.bar.container
        self.paramButton.setPosition(Vector2(width - 60 * s, sbc.getPosition().y + sbc.getHeight() + 5 * s))
        self.paramButton.getLabel().setStyle('align: middle-left;')
        evt = 'icecloud.sectionPanel.showParamMenu()';
        self.paramButton.setUIEventCommand(evt)
        self.curParam = 0
        self.paramMin = 0
        self.paramMax = 0
        self.paramName = "Parameter"

        # Setup the parameter selection menu
        self.paramMenu = icecloud.menuManager.createMenu('paramMenu')
        self.paramMenu.getContainer().setLayer(WidgetLayer.Front)
        icecloud.uiroot.removeChild(self.paramMenu.getContainer())
        self.container.addChild(self.paramMenu.getContainer())
        
        b = self.paramMenu.addButton('Beam Angle', 'icecloud.sectionPanel.onParamSelect(0)')
        b.getButton().setCheckable(True)
        b.getButton().setRadio(True)
        b = self.paramMenu.addButton('Beam Range', 'icecloud.sectionPanel.onParamSelect(1)')
        b.getButton().setCheckable(True)
        b.getButton().setRadio(True)
        b = self.paramMenu.addButton('Depth Range', 'icecloud.sectionPanel.onParamSelect(2)')
        b.getButton().setCheckable(True)
        b.getButton().setRadio(True)
        
        # Setup the parameter sliders
        pad = 24 * s
        self.paramStartLabel = Label.create(self.container)
        self.paramStartLabel.setText("Start Param Name Value")
        self.paramStartLabel.setStyle('align: middle-left')
        self.paramStartLabel.setPosition(Vector2(10 * s, self.paramButton.getPosition().y + pad))
        self.paramStartSlider = Slider.create(self.container)
        self.paramStartSlider.setPosition(Vector2(260 * s, self.paramButton.getPosition().y + pad))
        self.paramStartSlider.setWidth(200 * s)
        self.paramStartSlider.setUIEventCommand("icecloud.sectionPanel.onParamValueChange()")

        self.paramEndLabel = Label.create(self.container)
        self.paramEndLabel.setText("End Param Name Value")
        self.paramEndLabel.setPosition(Vector2(10 * s, self.paramStartSlider.getPosition().y + pad))
        self.paramEndLabel.setStyle('align: middle-left')
        self.paramEndSlider = Slider.create(self.container)
        self.paramEndSlider.setPosition(Vector2(260 * s, self.paramStartSlider.getPosition().y + pad))
        self.paramEndSlider.setWidth(200 * s)
        self.paramEndSlider.setUIEventCommand("icecloud.sectionPanel.onParamValueChange()")
        
        self.container.setSize(Vector2(width + icecloud.sideMargin * 2 * s, self.paramEndSlider.getPosition().y + pad))
        
        self.onSectionSelected(None)
        
    #---------------------------------------------------------------------------
    def addDives(self, dives):
        for d in dives:
            self.addDive(d)
    
    #---------------------------------------------------------------------------
    def addDive(self, dive):
        self.dives[dive.id] = dive
        groupName = dive.id.split('-')[0]
        if(not groupName in self.groups):
            evt = 'icecloud.sectionPanel.groups["{0}"].show()'.format(groupName)
            self.diveMenu.addButton(groupName, evt)
            groupMenu = icecloud.menuManager.createMenu('sections-' + groupName)
            groupMenu.getContainer().setPosition(Vector2(self.divesButton.getPosition().x, self.divesButton.getPosition().y + self.divesButton.getHeight()))
            icecloud.uiroot.removeChild(groupMenu.getContainer())
            self.container.addChild(groupMenu.getContainer())
            self.groups[groupName] = groupMenu
            self.groupMenuButtons[groupName] = []
        
        evt = 'icecloud.sectionPanel.onDiveSelect("{0}")'.format(dive.id)
        b = self.groups[groupName].addButton(dive.label, evt)
        b.getButton().setCheckable(True)
        b.getButton().setRadio(True)
        b.getButton().setName(dive.id)
        self.groupMenuButtons[groupName].append(b.getButton())
        self.dives[dive.id] = dive
    
    #---------------------------------------------------------------------------
    def showDivesMenu(self):
        if(self.diveMenu.isVisible()):
            self.diveMenu.hide()
        else:
            # Hide all group menus
            for key,m in self.groups.iteritems():
                m.hide()
                
            self.diveMenu.show()
            mc = self.diveMenu.getContainer()
            #mc.setPosition(self.container.getPosition() + Vector2(self.container.getWidth(), 0))
            s = Platform.scale
            mc.setPosition(Vector2(self.divesButton.getPosition().x, 46 * s))
        
    #---------------------------------------------------------------------------
    def onDiveSelect(self, name):
        d = self.dives[name]
        self.bar.data = d.sectionData
        self.dive = d
        self.dragger.setText('Selected Dive:' + d.label)
        # Hide all menus
        self.diveMenu.hide()
        for key,m in self.groups.iteritems():
            m.hide()
            
    #---------------------------------------------------------------------------
    def onParamSelect(self, id):
        self.curParam = id
        self.paramMenu.hide()
        if(self.dive != None):
            if(self.curParam == 0):
                self.paramMin = self.dive.angleMin
                self.paramMax = self.dive.angleMax
                self.paramName = "Beam Angle"
            elif(self.curParam == 1):
                self.paramMin = self.dive.rangeMin
                self.paramMax = self.dive.rangeMax
                self.paramName = "Beam Range"
            elif(self.curParam == 2):
                self.paramMin = self.dive.depthMin
                self.paramMax = self.dive.depthMax
                self.paramName = "Depth Range"
        # Update sliders reading value from the selected section
        if(self.bar.section != None):
            vmin = 0
            vmax = 0
            if(self.curParam == 0):
                vmin = float(self.bar.section.angleMin)
                vmax = float(self.bar.section.angleMax)
            elif(self.curParam == 1):
                vmin = float(self.bar.section.rangeMin)
                vmax = float(self.bar.section.rangeMax)
            elif(self.curParam == 2):
                vmin = float(self.bar.section.depthMin)
                vmax = float(self.bar.section.depthMax)
                print("vmin " + str(vmin))
                print("vmax " + str(vmax))
            d = self.paramMax - self.paramMin
            vmin = ((vmin - self.paramMin) / d) * 100
            vmax = ((vmax - self.paramMin) / d) * 100
            self.paramStartSlider.setValue(int(vmin))
            self.paramEndSlider.setValue(int(vmax))
        self.onParamValueChange()
            
    
    #---------------------------------------------------------------------------
    def showParamMenu(self):
        if(self.paramMenu.isVisible()):
            self.paramMenu.hide()
        else:
            self.paramMenu.show()
            mc = self.paramMenu.getContainer()
            #mc.setPosition(self.container.getPosition() + Vector2(self.container.getWidth(), 0))
            s = Platform.scale
            mc.setPosition(self.paramButton.getPosition() + Vector2(0, self.paramButton.getHeight()))
        
    #---------------------------------------------------------------------------
    def onParamValueChange(self):
        d = self.paramMax - self.paramMin
        v = self.paramStartSlider.getValue()
        self.updateParamLabel(self.paramStartLabel, "Min {0}".format(self.paramName), v)
        if(self.bar.section != None):
            v = v * d / 100 + self.paramMin
            if(self.curParam == 0):
                self.bar.section.angleMin = v
            elif(self.curParam == 1):
                self.bar.section.rangeMin = v
            elif(self.curParam == 2):
                self.bar.section.depthMin = v
                print("vmin " + str(v))
            
        
        v = self.paramEndSlider.getValue()
        self.updateParamLabel(self.paramEndLabel, "Max {0}".format(self.paramName), v)
        if(self.bar.section != None):
            v = v * d / 100 + self.paramMin
            if(self.curParam == 0):
                self.bar.section.angleMax = v
            elif(self.curParam == 1):
                self.bar.section.rangeMax = v
            elif(self.curParam == 2):
                self.bar.section.depthMax = v
                print("vmax " + str(v))
        self.bar.data.refresh()
        

    #---------------------------------------------------------------------------
    def updateParamLabel(self, label, text, v):
        d = self.paramMax - self.paramMin
        v = v * d / 100 + self.paramMin
        label.setText("{0}: {1}".format(text, v))
        
    #---------------------------------------------------------------------------
    def onSectionSelected(self, section):
        if(section != None):
            self.paramStartLabel.setVisible(True)
            self.paramStartSlider.setVisible(True)
            self.paramEndLabel.setVisible(True)
            self.paramEndSlider.setVisible(True)
            self.paramButton.setVisible(True)
        else:
            self.paramStartLabel.setVisible(False)
            self.paramStartSlider.setVisible(False)
            self.paramEndLabel.setVisible(False)
            self.paramEndSlider.setVisible(False)
            self.paramEndSlider.setVisible(False)
            self.paramButton.setVisible(False)
    
        