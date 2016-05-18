"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 18 May 2016
# Objective: 	Sensor Observation Service GetCapability parser
# 		To construct Describe Sensor and Get Observation requests
# Tested on: 
# 1. National Data Buoy Center SOS  (http://sdf.ndbc.noaa.gov/sos/server.php)
# 2. ISTSOS Demo SOS (http://istsos.org/istsos/demo)
#-----------------------------------------------------------------------
"""
import re, os, fnmatch, time, datetime
from colorama import Fore, Back, Style
import xmltodict
import requests
import dateutil.parser
from pytz import timezone
#-----------------------------------------------------------------------
def parseSOScap(url):
	"""
	function to parse SOS get capabilities request	
	
	url [str] SOS GetCapabilities request
		e.g. http://istsos.org/istsos/demo?request=getCapabilities&section=contents&service=SOS

	output {dict} of service details contains
		
		offering:	SOS offering 
				(e.g. temporary, system1, etc.)
		timeEndPosition: Time of last SOS update formatted as %Y-%m-%dT%H:%M:%S%z
				(e.g. 2014-05-03T16:30:00+0200)
		timeBeginPosition: Time of first SOS update formatted as %Y-%m-%dT%H:%M:%S%z
				(e.g. 2014-05-03T16:30:00+0200)
		# Note: for NDBC data lat lon are bounding box
		coordinates:	point lat lon
				(lat, lon) e.g. (u'22.670000000000002,51.25')
		lowerCorner:	Lower corner lat lon of bounding box
				(lat, lon) e.g. (u'-77.466,-179.995')
		upperCorner:	Upper corner lat lon of bounding box
				(lat, lon) e.g. (u'80.81,180')
		#		
		observedProperties: single or multiple observed properties
				e.g. {0: u'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity:relative', ... }
		procedure: single or mupltiple procedures
				e.g. {u'urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA', ...}

	Note: 	1. output may contain mupltiple nested dictionaries
		2. Not tested with http://localhost/service
	"""
	new = {} # e.g. detailsDict['water']=100
	# import request class
	import requests as requests
	# Check and verify Get Capabilities request
	verify = verifyGCReq(url)
	if verify == 'VALID':
		# Send request
		res = requests.get(url)
		#print(res, res.text)
		try:
			jj = xmltodict.parse(res.text)
			oOffer = jj['Capabilities']['Contents']['ObservationOfferingList']['ObservationOffering']
			# list all sensors
			for i in range(len(oOffer)):
				detailsDict = {}	
				detailsDict['offering'] = oOffer[i]['@gml:id']
				detailsDict['coordinates'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:coordinates'] # for ISTSOS
				detailsDict['lowerCorner'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:coordinates'] # for NDBC	
				detailsDict['upperCorner'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:coordinates'] # for NDBC
				#
				startPosition = dateutil.parser.parse(oOffer[i]['time']['gml:TimePeriod']['gml:beginPosition'])
				detailsDict['timeBeginPosition'] = startPosition.strftime('%Y-%m-%dT%H:%M:%S%z')
				#				
				endPosition = dateutil.parser.parse(oOffer[i]['time']['gml:TimePeriod']['gml:endPosition'])				
				detailsDict['timeEndPosition'] = endPosition.strftime('%Y-%m-%dT%H:%M:%S%z')
				# for multiple procedure list
				allProcedures = oOffer[i]['sos:procedure']
				if len(allProcedures) == 1: 
					detailsDict['procedure'] = allProcedures['@xlink:href']
				else:
					lProcedures = {}
					for pr in range(len(allProcedures)):
						lProcedures[pr] = allProcedures[pr]['@xlink:href']
					detailsDict['procedure'] = lProcedures
				# for multimple observed properties
				obsPropList = oOffer[i]['sos:observedProperty']
				if len(obsPropList) == 1:
					detailsDict['observedProperties'] = obsPropList['@xlink:href']
				else:
					obsProp = {}
					for p in range(len(obsPropList)):
						obsProp[p] = obsPropList[p]['@xlink:href']
					detailsDict['observedProperties'] =  obsProp
				#
				new[i]=detailsDict
		except:
			pass
		try:
			jj = xmltodict.parse(res.text)
			oOffer = jj['sos:Capabilities']['sos:Contents']['sos:ObservationOfferingList']['sos:ObservationOffering']
			# list all sensors
			for i in range(len(oOffer)):
				detailsDict = {}	
				detailsDict['offering'] = oOffer[i]['@gml:id']
				detailsDict['coordinates'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:lowerCorner'] # for ISTSOS
				detailsDict['coordinates'] = detailsDict['coordinates'].replace(' ',',')
				detailsDict['lowerCorner'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:lowerCorner'] # for NDBC
				detailsDict['lowerCorner'] = detailsDict['lowerCorner'].replace(' ',',')	
				detailsDict['upperCorner'] = oOffer[i]['gml:boundedBy']['gml:Envelope']['gml:upperCorner'] # for NDBC
				detailsDict['upperCorner'] = detailsDict['upperCorner'].replace(' ',',')
				#			
				startPosition = dateutil.parser.parse(oOffer[i]['sos:time']['gml:TimePeriod']['gml:beginPosition'])
				detailsDict['timeBeginPosition'] = startPosition.strftime('%Y-%m-%dT%H:%M:%S%z')
				# problem with list of all offerings
				tmpVar = oOffer[i]['sos:time']['gml:TimePeriod']['gml:endPosition']
				sudoVar = u'psudo unicode Variable'
				if type(sudoVar) != type(tmpVar):
					endPosition = datetime.datetime.now()
					detailsDict['timeEndPosition'] = endPosition.replace(tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
				else:
					endPosition =  dateutil.parser.parse(oOffer[i]['sos:time']['gml:TimePeriod']['gml:endPosition'])
					detailsDict['timeEndPosition'] = endPosition.strftime('%Y-%m-%dT%H:%M:%S%z')
				# for multiple procedure list
				allProcedures = oOffer[i]['sos:procedure']
				if len(allProcedures) == 1:
					detailsDict['procedure'] = allProcedures['@xlink:href']
				else:
					lProcedures = {}
					for pr in range(len(allProcedures)):
						lProcedures[pr] = allProcedures[pr]['@xlink:href']
					detailsDict['procedure'] = lProcedures
				# for multimple observed properties
				obsPropList = oOffer[i]['sos:observedProperty']
				if len(obsPropList) == 1:
					detailsDict['observedProperties'] = obsPropList['@xlink:href']
				else:
					obsProp = {}
					for p in range(len(obsPropList)):
						obsProp[p] = obsPropList[p]['@xlink:href']
					detailsDict['observedProperties'] =  obsProp
				#				
				new[i]=detailsDict
		except:
			pass
	#print(Fore.RED+"Some Error in Get Capabilities parsing"+Fore.RESET)
	elif verify == 'INVALID':
		print(Fore.RED+"URL is Invalid check URL content for 'http:','request','getcapabilities', 'SOS' and 'service'"+Fore.RESET)	
	else:
		print(Fore.RED+"There is unknown problem with URL"+Fore.RESET)
	return new
#-----------------------------------------------------------------------
def verifyGCReq(url):
	"""
	Check and verify Get Capabilities request

	url [str] URL / service GetCapabilities request
	
	output VALID/ INVALID / ERROR

	"""
	verify = "ERROR"
	splitURL = re.split("/|=|&|\\?|\\.", url)
	for i in range(len(splitURL)): splitURL[i] = splitURL[i].lower()
	#print(splitURL)
	findThis = ['http:','request','getcapabilities', 'sos', 'service']
	foundThis = []
	for i in range(len(findThis)):
		me = fnmatch.filter(splitURL, '*'+findThis[i]+'*')
		if me != []:
			foundThis.append(me[0])
	if len(findThis) == len(foundThis):
		verify = "VALID"
		print(Fore.GREEN+"Valid URL"+Fore.RESET)
	else:
		verify = "INVALID"
		print(Fore.RED+"invalid URL"+Fore.RESET)
	#print (findThis)
	#print (foundThis)
	return verify
#-----------------------------------------------------------------------
# implementation

# To do
# 1. Push data through Telegram Bot
# 2. Check feasibility for localhost

#Approach 3
# List of things I need from Get Observation Request
 
url = 'http://istsos.org/istsos/demo?request=getCapabilities&section=contents&service=SOS'
url2 = 'http://sdf.ndbc.noaa.gov/sos/server.php?request=GetCapabilities&service=SOS' 

#details = parseSOScap(url)
#print(details)

    



