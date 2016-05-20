"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 20 May 2016 >> 21 May 2016
# Objective: 	Sensor Observation Service Describe sensor parser
# 		To get more information about sensor
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
from sosParseCap import exceptionHandler
#-----------------------------------------------------------------------
def parseSOSDSensor(url):
	"""
	function to parse SOS describe sensor request	
	
	url [str] SOS DescribeSensor request
		

	output {dict} of sensor details

		For ISTSOS and NDBC Sensors
		1. sensorId (sensor identification number)
		2. sensorDescription (short sensor description)
		3. sensorName (sensor name from SensorML)
		4. sensorIdentification (Identification URI)
		5. sensorClassificaion (System Type and Sensor Type)
		6. sensorLocation (sensor location information as
			spatial reference system (srs),
			coordinates lat, lon, alt
			sensor GML id)

		7. sensor output / components (sml sensorFields)
			sensor definition (i.e. URI)
			sensor name (e.g. solar-radiation, air-relative-humidity)	
			sensor unit of measurement (uom) e.g. W/m2, %, etc.
			Note: For NDBC Station Components information is considered
					
		Following sections of NDBC sensors are not covered in this parser
		8. sml:capabilities 
		7. sml:validTime
		8. sml:contact /s
		9. sml:history
		
	Note: 	1. output may contain mupltiple nested dictionaries
		2. Not tested with http://localhost/service
	"""
	new = {}
	# import request class
	import requests as requests
	# Check and verify Describe Sensor request
	verify = verifyDSReq(url)
	if verify == 'VALID':
		# Send request
		res = requests.get(url)
		#print(res, res.text)
		try:
			jj = xmltodict.parse(res.text)
			detailsDict = {}
			# oOffer = jj['Capabilities']['Contents']['ObservationOfferingList']['ObservationOffering']
			# Description
			detailsDict['sensorId'] = jj['sml:SensorML']['sml:member']['sml:System']['@gml:id']
			detailsDict['sensorDescription'] = jj['sml:SensorML']['sml:member']['sml:System']['gml:description']
			detailsDict['sensorName'] = jj['sml:SensorML']['sml:member']['sml:System']['gml:name']
			# Identification 
			#detailsDict['sensorIdentificationDef'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:identification']['sml:IdentifierList']['sml:identifier']['sml:Term']['@definition']
			detailsDict['sensorIdentification'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:identification']['sml:IdentifierList']['sml:identifier']['sml:Term']['sml:value']
			# list of sensor classification
			sClass = jj['sml:SensorML']['sml:member']['sml:System']['sml:classification']['sml:ClassifierList']['sml:classifier']
			cl = {}
			for c in range(len(sClass)):
				cl[sClass[c]['@name']] = sClass[c]['sml:Term']['sml:value']
			detailsDict['sensorClassificaion'] = cl
			# sensor location  
			loc = {}
			locId = {}
			loc['srs'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:location']['gml:Point']['@srsName']
			loc['gmlId'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:location']['gml:Point']['@gml:id']
			loc['coordinates'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:location']['gml:Point']['gml:coordinates']
			locId[0] = loc 
			detailsDict['sensorLocation'] = locId			
			# sensor output / components
			fieldList = jj['sml:SensorML']['sml:member']['sml:System']['sml:outputs']['sml:OutputList']['sml:output']['swe:DataRecord']['swe:field']
			fieldSet = {}		
			for f in range(len(fieldList)):
				fieldS = {}
				fieldS['name'] = fieldList[f]['@name']
				# time and others are different
				if fieldS['name'] == 'Time':
					fieldS['uom'] = fieldList[f]['swe:Time']['@definition']
					fieldS['definition'] = fieldList[f]['swe:Time']['swe:constraint']['swe:AllowedTimes']['swe:interval']
					# additional time properties
				else:
					fieldS['definition'] = fieldList[f]['swe:Quantity']['@definition']
					fieldS['uom'] = fieldList[f]['swe:Quantity']['swe:uom']['@code'] # unit of measurement
				fieldSet[f] = fieldS
			detailsDict['sensorFields'] = fieldSet
			#print(detailsDict)
			# list all sensors
			new = detailsDict
		except:
			#new = exceptionHandler(res)
			pass
		try:
			jj = xmltodict.parse(res.text)
			detailsDict = {}
			# Description
			detailsDict['sensorId'] = jj['sml:SensorML']['sml:member']['sml:System']['@gml:id']
			detailsDict['sensorDescription'] = jj['sml:SensorML']['sml:member']['sml:System']['gml:description']
			detailsDict['sensorName'] = jj['sml:SensorML']['sml:member']['sml:System']['@gml:id']
			# Identification # some system details are ignored
			detailsDict['sensorIdentification'] = jj['sml:SensorML']['sml:member']['sml:System']['sml:identification']['sml:IdentifierList']['sml:identifier'][0]['sml:Term']['sml:value']
			# list of sensor classification
			sClass = jj['sml:SensorML']['sml:member']['sml:System']['sml:classification']['sml:ClassifierList']['sml:classifier'] 
			cl = {}
			for c in range(len(sClass)):
				cl[sClass[c]['@name']] = sClass[c]['sml:Term']['sml:value']
			detailsDict['sensorClassificaion'] = cl
			# sensor location  
			locId = {}
			sPos = jj['sml:SensorML']['sml:member']['sml:System']['sml:positions']['sml:PositionList']['sml:position']
			for pos in range(len(sPos)):
				loc = {}				
				loc['srs'] = 'None' 
				loc['gmlId'] = sPos[pos]['swe:Position']['swe:location']['swe:Vector']['@gml:id']
				latLonAlt = sPos[pos]['swe:Position']['swe:location']['swe:Vector']['swe:coordinate']
				aa = {}
				for lLa in range(len(latLonAlt)):
					aa[latLonAlt[lLa]['@name']] = latLonAlt[lLa]['swe:Quantity']['swe:value']				
				strLatLonAlt = aa['latitude']+', '+aa['longitude']+', '+aa['altitude']
				loc['coordinates'] = strLatLonAlt
				locId[pos] = loc 
			detailsDict['sensorLocation'] = locId
			# sensor output / components
			fieldList = jj['sml:SensorML']['sml:member']['sml:System']['sml:components']['sml:ComponentList']['sml:component']
			fieldSet = {}		
			for f in range(len(fieldList)):
				fieldS = {}
				fieldS['name'] = fieldList[f]['@name']
				fieldS['uom'] = 'None'
				defNs = fieldList[f]['sml:System']['sml:classification']['sml:ClassifierList']['sml:classifier']
				try:
					tmp = {}
					for dd in range(len(defNs)):
						if defNs[dd]['sml:Term']['sml:value'] != None:
							tmp[defNs[dd]['@name']] = defNs[dd]['sml:Term']['sml:value']
					fieldS['definition'] = tmp
				except:
					fieldS['definition'] = 'None'
					pass
				fieldSet[f] = fieldS
			detailsDict['sensorFields'] = fieldSet			
			# list all sensors
			new = detailsDict	
		except:
			#new = exceptionHandler(res)
			pass			
	elif verify == 'INVALID':
		print(Fore.RED+"URL is Invalid check URL content for 'http:','request','decribeSensor', 'SOS' and 'service'"+Fore.RESET)	
	else:
		print(Fore.RED+"There is unknown problem with URL"+Fore.RESET)
	return new
#-----------------------------------------------------------------------
def verifyDSReq(url):
	"""
	Check and verify Describe Sensor request

	url [str] URL / service DescribeSensor request
	
	output VALID/ INVALID / ERROR

	"""
	verify = "ERROR"
	splitURL = re.split("/|=|&|\\?|\\.", url)
	for i in range(len(splitURL)): splitURL[i] = splitURL[i].lower()
	#print(splitURL)
	findThis = ['http:','request','describesensor', 'sos', 'service', 'procedure', 'version']
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
ndbc1 = "http://sdf.ndbc.noaa.gov/sos/server.php?request=DescribeSensor&service=SOS&procedure=urn:ioos:station:wmo:21346&outputFormat=text/xml;subtype=%22sensorML/1.0.1%22&version=1.0.0"
#ndbc2 = "http://sdf.ndbc.noaa.gov/sos/server.php?request=DescribeSensor&service=SOS&procedure=urn:ioos:station:wmo:21346&outputFormat=text/xml%3Bsubtype=%22sensorML/1.0.1%22&version=1.0.0"
#istsos1 = "http://istsos.org/istsos/demo?request=DescribeSensor&service=SOS&procedure=urn:ogc:def:procedure:x-istsos:1.0:GRABOW&outputFormat=text/xml;subtype=%22sensorML/1.0.1%22&version=1.0.0"
istsos2 = "http://istsos.org/istsos/demo?request=DescribeSensor&service=SOS&procedure=urn:ogc:def:procedure:x-istsos:1.0:GRABOW&outputFormat=text/xml%3Bsubtype=%22sensorML/1.0.1%22&version=1.0.0"
#details = parseSOSDSensor(istsos2)
#print(details)
#details = parseSOSDSensor(ndbc1)
#print(details)
