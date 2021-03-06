#######################################################################
#
#    TechniHD Setup
#    Original Source Coded by Vali (c)2011 (FlexControl)
#
#######################################################################
                                                          

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
from skin import parseColor
from os import system


config.technihd = ConfigSubsection()
config.technihd.SecondInfobar = ConfigSelection(default="NowAndNextInfo", choices = [("TunerAndCryptInfos", _("TunerState, Crypt, SNR,...")),("NowAndNextInfo", _("Now and Next EventInfo"))])
config.technihd.Infobar = ConfigSelection(default="NextEventInfo", choices = [("BouquetInfo", _("BouquetInfo")),("NextEventInfo", _("Next EventInfo"))])
config.technihd.InfobarSatPos = ConfigYesNo(default=False)
config.technihd.channellist = ConfigSelection(default="left", choices = [("right", _("right")),("left", _("left"))])
config.technihd.cooltvguide = ConfigYesNo(default=False)

class TechniHDSetup(ConfigListScreen, Screen):
	skin = """
		<screen name="TechniHDSetup" position="center,center" size="600,580" title="TechniHD Setup">
			<ePixmap alphatest="blend" pixmap="TechniHD/buttons/red.png" position="67,528" size="40,40" zPosition="2" />
			<ePixmap alphatest="blend" pixmap="TechniHD/buttons/green.png" position="322,528" size="40,40" zPosition="2" />
			<eLabel font="Regular;20" halign="left" position="100,529" size="180,26" text="Cancel" transparent="1" />
			<eLabel font="Regular;20" halign="left" position="354,529" size="180,26" text="Save" transparent="1" />
			<widget itemHeight="30" name="config" position="51,339" scrollbarMode="showOnDemand" size="492,165" font="Regular; 16" />
		        <eLabel position="48,30" size="492,253" zPosition="1" backgroundColor="grey" />
                        <eLabel position="50,32" size="488,249" zPosition="2" backgroundColor="dblau" />
                        <widget name="preview" zPosition="3" position="60,41" size="469,230" alphatest="blend" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/TechniHD/skin.xml"
		self.data = "/usr/lib/enigma2/python/Plugins/Extensions/TechniHDSetup/preview/"
		self["preview"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("Show SecondInfobar with:"), config.technihd.SecondInfobar))
		list.append(getConfigListEntry(_("Show Infobar with:"), config.technihd.Infobar))
		list.append(getConfigListEntry(_("Show Infobar with OrbitalPosition:"), config.technihd.InfobarSatPos))
		list.append(getConfigListEntry(_("Show Channel Selection ScrollBarMode:"), config.technihd.channellist))
		if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo') and not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/CoolInfoGuide.pyo'):
                        list.append(getConfigListEntry(_("Show TechniHD - CoolTVGuide Skin:"), config.technihd.cooltvguide))
		ConfigListScreen.__init__(self, list, on_change = self.UpdateComponents)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
									{
									"red": self.exit, 
									"green": self.save,
									"cancel": self.exit
									}, -1)
		self.onLayoutFinish.append(self.UpdateComponents)

	def UpdateComponents(self):
		prev = self.data + "sib-" + config.technihd.SecondInfobar.value + ".png"
                if fileExists(prev):
			self["preview"].instance.setPixmapFromFile(prev)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		try:
			skin_lines = []
			skn_file = self.datei
			skFile = open(skn_file, "r")
			file_lines = skFile.readlines()
			for x in file_lines:
				if 'name="SecondInfoBarDisabled"' in x:
					if config.technihd.SecondInfobar.value == "TunerAndCryptInfos":
						x = '<screen name="SecondInfoBar" title="Second InfoBar Normal" position="0,0" zPosition="11" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">\n'
				elif 'title="Second InfoBar Normal"' in x:	
                                        if config.technihd.SecondInfobar.value == "NowAndNextInfo":
						x = '<screen name="SecondInfoBarDisabled" title="Second InfoBar Normal" position="0,0" zPosition="11" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">\n'
				elif 'EventNextInformation' in x:
					if config.technihd.Infobar.value == "BouquetInfo":
						x = '<!-- BouquetInformation!! do not change this line --><widget source="session.CurrentService" render="Label" position="255,608" size="760,27" font="hd;22" halign="left" backgroundColor="hblau" transparent="1"><convert type="BouquetInfo">Bouquet</convert></widget>\n'
				elif 'BouquetInformation' in x:	
                                        if config.technihd.Infobar.value == "NextEventInfo":
						x = '<!-- EventNowAndNextInformation!! do not change this line --><widget source="session.Event_Next" render="Label" position="241,607" size="91,25" font="Regular2; 20" halign="center" backgroundColor="hblau" transparent="1"><convert type="EventTime">StartTime</convert><convert type="ClockToText">Format:%H:%M</convert></widget><widget source="session.Event_Next" render="Label" position="319,607" size="86,25" font="Regular2; 20" halign="center" backgroundColor="hblau" transparent="1"><convert type="EventTime">EndTime</convert><convert type="ClockToText">Format:- %H:%M</convert></widget><widget source="session.Event_Next" render="Label" position="414,608" size="600,25" font="hd;22" halign="left" backgroundColor="hblau" transparent="1"><convert type="EventName">Name</convert></widget>\n'
				elif 'ChannelNameInformation' in x:
					if config.technihd.InfobarSatPos.value == True:
						x = '<!-- OrbitPosAndChanNameInformation!! do not change this line --><widget source="session.CurrentService" render="Label" position="254,648" size="91,25" font="Regular2; 20" valign="center" backgroundColor="background" transparent="1"><convert type="ServiceOrbitalPosition">Short</convert></widget><widget source="session.CurrentService" render="Label" position="335,642" size="494,37" font="Regular; 30" valign="center" backgroundColor="background" transparent="1" zPosition="1"><convert type="ServiceName">Name</convert></widget>\n'
				elif 'OrbitPosAndChanNameInformation' in x:
					if config.technihd.InfobarSatPos.value == False:
						x = '<!-- ChannelNameInformation!! do not change this line --><widget source="session.CurrentService" render="Label" position="255,642" size="572,37" font="Regular; 30" valign="center" backgroundColor="background" transparent="1" zPosition="1"><convert type="ServiceName">Name</convert></widget>\n'
				elif 'ScrollBarLeft' in x:
					if config.technihd.channellist.value == "right":
						x = '<!-- ScrollBarRight!! do not change this line --><widget name="list" selectionPixmap="TechniHD/menu/sel1280x40.png" picServiceEventProgressbar="TechniHD/progressbar.png" position="20,171" size="1237,442" zPosition="3" scrollbarMode="showOnDemand" backgroundColor="dblau" foregroundColorServiceNotAvail="grey" serviceItemHeight="40" serviceNumberFont="Regular2;24" colorServiceDescription="white" serviceNameFont="Regular2;29" serviceInfoFont="Regular3;23" transparent="1" colorServiceDescriptionSelected="dblau" colorEventProgressbar="yellow" colorEventProgressbarSelected="dblau" colorEventProgressbarBorder="grey" colorEventProgressbarBorderSelected="black"></widget>\n'
				elif 'ScrollBarRight' in x:
					if config.technihd.channellist.value == "left":
						x = '<!-- ScrollBarLeft!! do not change this line --><widget name="list" selectionPixmap="TechniHD/menu/sel1280x40.png" picServiceEventProgressbar="TechniHD/progressbar.png" position="20,171" size="1237,442" zPosition="3" scrollbarMode="showLeft" backgroundColor="dblau" foregroundColorServiceNotAvail="grey" serviceItemHeight="40" serviceNumberFont="Regular2;24" colorServiceDescription="white" serviceNameFont="Regular2;29" serviceInfoFont="Regular3;23" transparent="1" colorServiceDescriptionSelected="dblau" colorEventProgressbar="yellow" colorEventProgressbarSelected="dblau" colorEventProgressbarBorder="grey" colorEventProgressbarBorderSelected="black"></widget>\n'
				elif 'name="CoolChannelGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolChannelGuide" position="0,0" size="1280,720" title="Cool Channel Guide" flags="wfNoBorder" backgroundColor="transparent">\n' 
				elif 'name="CoolChannelGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolChannelGuideDisabled" position="0,0" size="1280,720" title="Cool Channel Guide" flags="wfNoBorder" backgroundColor="transparent">\n'
                                elif 'name="CoolInfoGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolInfoGuide" position="0,0" size="1280,720" title="Cool Info Guide" flags="wfNoBorder" backgroundColor="transparent" zPosition="7">\n' 
				elif 'name="CoolInfoGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolInfoGuideDisabled" position="0,0" size="1280,720" title="Cool Info Guide" flags="wfNoBorder" backgroundColor="transparent" zPosition="7">\n'
                                elif 'name="CoolMultiGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolMultiGuide" position="0,0" size="1280,720" title="Cool Multi Guide" flags="wfNoBorder" backgroundColor="transparent">\n' 
				elif 'name="CoolMultiGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolMultiGuideDisabled" position="0,0" size="1280,720" title="Cool Multi Guide" flags="wfNoBorder" backgroundColor="transparent">\n'
                                elif 'name="CoolNiceGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolNiceGuide" position="0,0" size="1280,720" title="Cool Nice Guide" flags="wfNoBorder" backgroundColor="transparent">\n' 
				elif 'name="CoolNiceGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolNiceGuideDisabled" position="0,0" size="1280,720" title="Cool Nice Guide" flags="wfNoBorder" backgroundColor="transparent">\n'
                                elif 'name="CoolEasyGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolEasyGuide" position="0,0" size="1280,720" title="Cool Easy Guide" flags="wfNoBorder" backgroundColor="transparent">\n' 
				elif 'name="CoolEasyGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolEasyGuideDisabled" position="0,0" size="1280,720" title="Cool Easy Guide" flags="wfNoBorder" backgroundColor="transparent">\n'
                                elif 'name="CoolTVGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolTVGuide" position="0,0" size="1280,720" title="Cool TV Guide" backgroundColor="transparent" flags="wfNoBorder" zPosition="10">\n' 
				elif 'name="CoolTVGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolTVGuideDisabled" position="0,0" size="1280,720" title="Cool TV Guide" backgroundColor="transparent" flags="wfNoBorder" zPosition="10">\n'
                                elif 'name="CoolTinyGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolTinyGuide" position="0,0" size="1280,720" title="Cool Tiny Guide" backgroundColor="transparent" flags="wfNoBorder" zPosition="10">\n' 
				elif 'name="CoolTinyGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolTinyGuideDisabled" position="0,0" size="1280,720" title="Cool Tiny Guide" backgroundColor="transparent" flags="wfNoBorder" zPosition="10">\n'
                                elif 'name="CoolSearchDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolSearch" position="0,0" size="1280,720" title="Cool Search" flags="wfNoBorder" backgroundColor="transparent" zPosition="7">\n' 
				elif 'name="CoolSearch"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolSearchDisabled" position="0,0" size="1280,720" title="Cool Search" flags="wfNoBorder" backgroundColor="transparent" zPosition="7">\n'
                                elif 'name="CoolSingleGuideDisabled"' in x:				
                                        if config.technihd.cooltvguide.value == True:
                                                x = '<screen name="CoolSingleGuide" position="0,0" size="1280,720" title="Cool Single Guide" flags="wfNoBorder" backgroundColor="transparent">\n' 
				elif 'name="CoolSingleGuide"' in x:
					if config.technihd.cooltvguide.value == False:
					        x = '<screen name="CoolSingleGuideDisabled" position="0,0" size="1280,720" title="Cool Single Guide" flags="wfNoBorder" backgroundColor="transparent">\n'                                
                                skFile.close()
                                skin_lines.append(x)
			xFile = open(self.datei, "w")
			for x in skin_lines:
				xFile.writelines(x)
			xFile.close()
		except:
			self.session.open(MessageBox, _("Error"), MessageBox.TYPE_ERROR)
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("TechniHD needs a restart to apply."), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart?"))

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()


def main(session, **kwargs):
	session.open(TechniHDSetup)
	
def setup(menuid):
    if config.skin.primary_skin.value == 'TechniHD/skin.xml': 
        if menuid == 'mainmenu':
            return [(_('TechniHD') + " " + _('Setup'),
              main,
              'TechniHDSetup',
              45)]
        return []
    else:
        return []

def Plugins(**kwargs):
	return PluginDescriptor(name="TechniHDSetup", description=_("Setup for TechniHD-skin"), where = PluginDescriptor.WHERE_MENU, fnc=setup)
