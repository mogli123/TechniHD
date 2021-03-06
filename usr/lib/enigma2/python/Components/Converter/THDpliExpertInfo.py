#
#  Coded by Vali, updated by Mirakels for openpli
#

from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Tools.Transponder import ConvertToHumanReadable
from Tools.GetEcmInfo import GetEcmInfo 
from Poll import Poll

class THDpliExpertInfo(Poll, Converter, object):
	SMART_LABEL = 0
	SMART_INFO_H = 1
	SMART_INFO_V = 2
	SERVICE_INFO = 3
	CRYPTO_INFO = 4
	
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = {
				"ShowMe": self.SMART_LABEL,
				"ExpertInfo": self.SMART_INFO_H,
				"ExpertInfoVertical": self.SMART_INFO_V,
				"ServiceInfo": self.SERVICE_INFO,
				"CryptoInfo": self.CRYPTO_INFO
			}[type]
		try:
			self.poll_interval = config.plugins.ValiKSSetup.pollTime.value*1000
		except:
			self.poll_interval = 1000
		self.poll_enabled = True
		self.idnames = (
			( "0x100", "0x1FF","Seca"   ,"Seca", " "),
			( "0x500", "0x5FF","Via"    ,"Viaccess", " "),
			( "0x600", "0x6FF","Irdeto" ,"Irdeto", " "),
			( "0x900", "0x9FF","NDS"    ,"Videoguard", " "),
			( "0xB00", "0xBFF","Conax"  ,"Conax", " "),
			( "0xD00", "0xDFF","CryptoW","Cryptoworks", " "),
			("0x1700","0x17FF","Beta"   ,"Betacrypt", " "),
			("0x1800","0x18FF","Nagra"  ,"Nagravision", " "))
		self.ecmdata = GetEcmInfo()

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""	

		Ret_Text = ""
		Sec_Text = ""
		Res_Text = ""

		if (self.type == self.SMART_INFO_H or self.type == self.SERVICE_INFO or self.type == self.CRYPTO_INFO): # HORIZONTAL
#                        sep = "\n"
#			sep2 = "\n"
			sep = "  "
			sep2 = " - "
		elif (self.type == self.SMART_INFO_V): # VERTIKAL
			sep = "\n"
			sep2 = "\n"
		else:
			return ""	# unsupported orientation
		
		if (self.type == self.SMART_INFO_H or self.type == self.SMART_INFO_V or self.type == self.SERVICE_INFO):
			
			xresol = info.getInfo(iServiceInformation.sVideoWidth)
			yresol = info.getInfo(iServiceInformation.sVideoHeight)
			feinfo = (service and service.frontendInfo())

			prvd = info.getInfoString(iServiceInformation.sProvider)
			Ret_Text = self.short(prvd)

			frontendDataOrg = (feinfo and feinfo.getAll(False))
			if (frontendDataOrg is not None):
				frontendData = ConvertToHumanReadable(frontendDataOrg)
				if ((frontendDataOrg.get("tuner_type") == "DVB-S") or (frontendDataOrg.get("tuner_type") == "DVB-C")):
					frequency = (str((frontendData.get("frequency") / 1000)))
					symbolrate = (str((frontendData.get("symbol_rate") / 1000)))
					fec_inner = frontendData.get("fec_inner")
					if (frontendDataOrg.get("tuner_type") == "DVB-S"):
						Ret_Text += sep + frontendData.get("system")
						Ret_Text += sep + frequency + frontendData.get("polarization")[:1]
						Ret_Text += sep + symbolrate
						Ret_Text += sep + frontendData.get("modulation") + "-" + fec_inner
						orbital_pos = int(frontendDataOrg["orbital_position"])
						if orbital_pos > 1800:
							orb_pos = str((float(3600 - orbital_pos)) / 10.0) + "W"
						elif orbital_pos > 0:
							orb_pos = str((float(orbital_pos)) / 10.0) + "E"
						Ret_Text += sep + orb_pos
					else:
						Ret_Text += sep + "DVB-C " + frequency + " MHz" + sep + fec_inner + sep + symbolrate
				elif (frontendDataOrg.get("tuner_type") == "DVB-T"):
					frequency = (str((frontendData.get("frequency") / 1000)))
					Ret_Text += sep + "DVB-T" + sep + "Frequency:" + sep + frequency + " MHz"

			if (feinfo is not None) and (xresol > 0):
				Res_Text += ("MPEG2 ", "MPEG4 ", "MPEG1 ", "MPEG4-II ", "VC1 ", "VC1-SM ", "")[info.getInfo(iServiceInformation.sVideoType)]
				Res_Text += str(xresol) + "x" + str(yresol) 
				Res_Text += ("i", "p")[info.getInfo(iServiceInformation.sProgressive)]
				Res_Text += (" ") + str((info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)  
                                Res_Text += ("fps")
                                
		if (self.type == self.SMART_INFO_H or self.type == self.SMART_INFO_V or self.type == self.CRYPTO_INFO):

			decCI = "0" 
			Sec_Text = ""
			if (info.getInfo(iServiceInformation.sIsCrypted) == 1):
				data = self.ecmdata.getEcmData()
				Sec_Text = data[0]	
				decCI = data[1]
				provid = data[2]
				pid = data[3]	

				if decCI != '0':
					decCIfull = "%04x" % int(decCI, 16)
					for idline in self.idnames:
						if int(decCI, 16) >= int(idline[0], 16) and int(decCI, 16) <= int(idline[1], 16):
							decCIfull = idline[2] + ":" + decCIfull
							break
					Sec_Text += "\n" + decCIfull
					if provid != '0':
						Sec_Text += ":%04x" % int(provid, 16)
					if pid != '0':
						Sec_Text += sep + "pid:%04x" % int(pid, 16)
			
			else:
				Sec_Text = "FTA"
			res = ""			
			searchIDs = (info.getInfoObject(iServiceInformation.sCAIDs))
			for idline in self.idnames:
				if int(decCI, 16) >= int(idline[0], 16) and int(decCI, 16) <= int(idline[1], 16):                    
					color="\c0000??00"
				else:
					color = "\c007?7?7?"
					try:
						for oneID in searchIDs:
							if oneID >= int(idline[0], 16) and oneID <= int(idline[1], 16):
#								color="\c00????00"
                                                                color = "\c007?7?7?"
					except:
						pass
				res += color + idline[3] + " "
			
			if (self.type != self.CRYPTO_INFO):
				Ret_Text += "\n"
			Ret_Text += res + "\c00?????? " + Sec_Text
		
		if Res_Text != "":
			Ret_Text += sep + Res_Text

		return Ret_Text

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)

	def short(self, langTxt):
		if (self.type == self.SMART_INFO_V and len(langTxt)>23):
			retT = langTxt[:20] + "..."
			return retT
		else:
			return langTxt
