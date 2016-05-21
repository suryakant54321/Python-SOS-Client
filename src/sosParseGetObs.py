"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 21 May 2016
# Objective: 	Sensor Observation Service Get Observation parser
# 
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
def parseSOSGetObs(url, rparams):
	"""
	function to parse SOS describe sensor request	
	
	url [str] SOS url
	
	rparams {dict} get observation request parameters

	output {dict} of sensor observations

		For ISTSOS and NDBC Sensors
					
		Following sections of NDBC sensors are not covered in this parser
		
	Note: 	1. output may contain mupltiple nested dictionaries
		2. Not tested with http://localhost/service
	"""
	new = {}
	# import request class
	import requests as requests
	# Check and verify Get Observation request
	verify = verifyGOReq(url, rparams)
	if verify == 'VALID':
		# Send request
		res = requests.get(url, params=rparams)
		#print(res, res.text)
		try:
			jj = xmltodict.parse(res.text)
			detailsDict = {}

			# all observations
			new = detailsDict
		except:
			#new = exceptionHandler(res)
			pass
		try:
			jj = xmltodict.parse(res.text)
			detailsDict = {}

			# all observations
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
def verifyGOReq(url, rparams):
	"""
	Check and verify Get Observation request

	url [str] SOS URL 
	
	rparams {dict} Get observation request parameters
	
	output VALID/ INVALID / ERROR

	"""
	verify = "ERROR"
	# Verify URL
	splitURL = re.split("/|=|&|\\?|\\.", url)
	for i in range(len(splitURL)): splitURL[i] = splitURL[i].lower()
	#print(splitURL)
	findThis = ['http:']
	foundThis = []
	for i in range(len(findThis)):
		me = fnmatch.filter(splitURL, '*'+findThis[i]+'*')
		if me != []:
			foundThis.append(me[0])
	# Verify request parameters
	rKeys = rparams.keys()
	rTest = []
	# To Do: add verification for request keys
	for p in range(len(rKeys)):
		rSpace = rparams[rKeys[p]].replace(" ","")
		if rparams[rKeys[p]] == 'None' or rparams[rKeys[p]] == [] or rparams[rKeys[p]] == '' or rSpace == '':
			rTest.append("FALSE")
		else:
			rTest.append("TRUE") 
	allTrue = fnmatch.filter(rTest, '*TRUE*')
	#
	if len(findThis) == len(foundThis) and len(rTest) == len(allTrue):
		verify = "VALID"
		print(Fore.GREEN+"Valid Request"+Fore.RESET)
	else:
		verify = "INVALID"
		print(Fore.RED+"invalid Request"+Fore.RESET)
	return verify
#-----------------------------------------------------------------------
def parseCSVresponse(resp):
	"""
	Return time series of observations

	Input csv response of Get Observation request

	Output/s	
		1. nested list time series
		   e.g. [[u'2014-05-07T20:10:00+00:00', u'11.000000'], ... ]

		2. sensor details dict
		   e.g. {:}
	"""
	senDet = {}
	sDetails = []
	sTSobs = []
	try:
		resp = re.split('\n',resp)
		for i in range(len(resp)):
			sObs = []
			if i==0:
				sDetails = re.split(",", resp[i])
				for j in range(len(sDetails)): sDetails[j]=sDetails[j].replace('"','')
			elif i < (len(resp)-2):
				rawSobs = re.split(",",resp[i])
				sObs.append(rawSobs[4])
				sObs.append(rawSobs[6])
				#print(sObs)
				sTSobs.append(sObs)
			elif i < (len(resp)-1):
				rawSobs = re.split(",",resp[i])
				sObs.append(rawSobs[4])
				sObs.append(rawSobs[6])
				#print(sObs)
				sTSobs.append(sObs)
				if len(sDetails) == len(rawSobs):
					for d in range(len(rawSobs)): senDet[sDetails[d]] = rawSobs[d]
			else:
				print(resp[i])
	except:
		pass
	return(senDet, sTSobs)
#-----------------------------------------------------------------------
def parsePlainResponse(resp):
	"""
	Return time series of observations

	Input plain text response of Get Observation request of ISTSOS

	Output/s	
		1. nested list time series
		   e.g. [[u'2014-05-07T20:10:00+00:00', u'11.000000'], ... ]

		2. sensor details dict
		   e.g. {:}
	"""
	senDet = {}
	sDetails = []
	sTSobs = []
	try:
		resp = re.split('\n',resp)
		for i in range(len(resp)):
			sObs = []
			if i==0:
				sDetails = re.split(",", resp[i])
				for j in range(len(sDetails)): sDetails[j]=sDetails[j].replace('"','')
				#print(sDetails)
			elif i < (len(resp)-2):
				rawSobs = re.split(",",resp[i])
				sObs.append(rawSobs[0])
				sObs.append(rawSobs[2])
				#print(sObs)
				sTSobs.append(sObs)
			elif i < (len(resp)-1):
				rawSobs = re.split(",",resp[i])
				sObs.append(rawSobs[0])
				sObs.append(rawSobs[2])
				#print(sObs)
				sTSobs.append(sObs)
				if len(sDetails) == len(rawSobs):
					for d in range(len(rawSobs)): senDet[sDetails[d]] = rawSobs[d]
			else:
				print(resp[i])
	except:
		pass
	return(senDet, sTSobs) 
#-----------------------------------------------------------------------
# implementation
# e.g. URL's
ndbcGO = "http://sdf.ndbc.noaa.gov/sos/server.php"
# XML
NDBCxml = "http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:station:wmo:41063&procedure=urn:ioos:station:wmo:41063&eventTime=2014-04-30T07:00:00Z/2014-05-30T07:00:00Z&observedProperty=air_temperature&responseFormat=text/xml;subtype=%22om/1.0.0%22"
# CSV
NDBCcsv = "http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:station:wmo:41063&procedure=urn:ioos:station:wmo:41063&eventTime=2014-04-30T07:00:00Z/2014-05-30T07:00:00Z&observedProperty=air_temperature&responseFormat=text/csv"
#NDBCrparams = {}
#NDBCrparams = {'':'',}
#

# 2. ISTSOS
istsosGO = "http://istsos.org/istsos/demo"
# JSON
istsosJSON = "http://istsos.org/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=BELLINZONA&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&responseFormat=application/json"
# CSV
istsosCSV = "http://istsos.org/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=BELLINZONA&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&responseFormat=text/plain"
#
startDate = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
endDate = datetime.datetime(2014,05,07,20,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
ISTSOSrparams = {}
ISTSOSrparams['eventTime'] = str(startDate) + "/" +str(endDate) # from start date to end date
ISTSOSrparams = {"service": "SOS", "offering": "BELLINZONA", "request": "GetObservation", "version": "1.0.0", "responseFormat": "application/json", "observedProperty": "air:temperature", "procedure": "BELLINZONA"}

#details = (istsos2)
#print(details)
#details = (ndbc1)
#print(details)

rparams

