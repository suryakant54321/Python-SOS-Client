"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 21 May 2016
# Objective: 	Sensor Observation Service Get Observation parser
# 
# Tested on: 
# 1. National Data Buoy Center SOS  (http://sdf.ndbc.noaa.gov/sos/server.php)
# 2. ISTSOS Demo SOS (http://istsos.org/istsos/demo)
# 
# To Do: 
#	1. Add verification for request keys
#	2. Add date time corrections for NDBC request/s
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
def parseJSONresponse(res):
	"""
	Function to parse JSON response SOS GetObservation request	
	
	Input:
		url [str] SOS url
	
		rparams {dict} get observation request parameters

	Output:
		1. nested list time series

		2. sensor details dict
		
	Note: 	1. Not tested with http://localhost/service
	"""
	senDet = {}
	sTSobs = []
	try:
		jj = res.json()
		sTSobs = jj['ObservationCollection']['member'][0]['result']['DataArray']['values']
		senDet['siteName'] = jj['ObservationCollection']['member'][0]['name']
		# sensor site name
		senFields = jj['ObservationCollection']['member'][0]['result']['DataArray']['field']
		# Time series field details
		for i in range(len(senFields)): senDet[senFields[i]['name']] = senFields[i]['definition']
		# Sensor lat, lon, alt
		sGeom = jj['ObservationCollection']['member'][0]['featureOfInterest']['geom']
		sGeom = xmltodict.parse(sGeom) 
		senDet['srsName'] = sGeom['gml:Point']['@srsName']
		senDet['coordinates'] = sGeom['gml:Point']['gml:coordinates']
	except:
		#new = exceptionHandler(res)
		pass
	return(senDet, sTSobs)
#-----------------------------------------------------------------------
def parseCSVresponse(resp):
	"""
	Return time series of observations

	Input CSV response of Get Observation request

	Output/s	
		1. sensor details dict
		   e.g.  {u'latitude (degree)': u'34.798', u'longitude (degree)': u'-75.945',
			  u'sensor_id': u'urn:ioos:sensor:wmo:41063::airtemp1',
 			  u'station_id': u'urn:ioos:station:wmo:41063', ...}

		2. nested list time series
		   e.g. [[u'2014-04-30T10:00:00Z', u'23.90'],
 			 [u'2014-04-30T12:00:00Z', u'23.90'], ...]
	
	Note: 	1. Tested only for NDBC sensors
	"""
	senDet = {}
	sDetails = []
	sTSobs = []
	try:
		resp = re.split('\n',resp.text)
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
		1. Sensor details dict
		   e.g. {u'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature': u'22.800000',
			 u'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601': u'2014-05-04T16:30:00+02:00', ...}

		2. Nested list time series
		   e.g. [[u'2014-05-04T16:20:00+02:00', u'22.700000'],
 			 [u'2014-05-04T16:30:00+02:00', u'22.800000'], ...]

	Note: 1. Tested only for ISTSOS sensors
	"""
	senDet = {}
	sDetails = []
	sTSobs = []
	try:
		resp = re.split('\n',resp.text)
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
def verifyGOReq(url, rparams):
	"""
	Check and verify Get Observation request

	Input:
		url [str] SOS URL 
	
		rparams {dict} get observation request parameters
	
	Output: VALID/ INVALID / ERROR in request
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
	# 
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
# 2.
def parseSOSgetObs(url, rparams, responseFormat='None'):
	"""
	Function for parsing Get Observation response
	
	Input/s:
		url [str] 
			(e.g. "http://istsos.org/istsos/demo")

		rparams {dict} request parameters
			(e.g. ISTSOSrparams = {"service": "SOS",\n
		 		"offering": "BELLINZONA",\n
		 		"request": "GetObservation",\n
		 		"version": "1.0.0",\n
		 		"observedProperty": "air:temperature",\n
		 		"procedure": "BELLINZONA"})
		
		responseFormat [str] response format 
			(e.g. CSV or JSON or plain)
		
		Note:	1. No need to mention response format in request parameters
			2. CSV response format is supported for NDBC sensors 
			3. JSON and plain response formats are supported for ISTSOS
	Output/s:
		1. Sensor details {dict}

		2. Nested [[list]] of sensor observations time series 
	"""
	# import request class
	import requests as requests
	# Check and verify Get Observation request
	verify = verifyGOReq(url, rparams)
	#
	senDetails = {}
	tSeriesObs = []
	if verify == 'VALID':
		if responseFormat.lower() == 'json':
			rparams['responseFormat'] = "application/"+responseFormat.lower()
			res = requests.get(url, params=rparams)
			senDetails, tSeriesObs = parseJSONresponse(res)
		elif responseFormat.lower() == 'csv':
			rparams['responseFormat'] = "text/"+responseFormat.lower()
			res = requests.get(url, params=rparams)
			#print(res.text)
			senDetails, tSeriesObs = parseCSVresponse(res) 
		elif responseFormat.lower() == 'plain':
			rparams['responseFormat'] = "text/"+responseFormat.lower()
			res = requests.get(url, params=rparams)
			#print(res.text)
			senDetails, tSeriesObs = parsePlainResponse(res)
		elif responseFormat.lower() == 'None':
			print(Fore.RED+"Response format is must. \n\
			JSON, CSV and Plain are supported"+Fore.RESET)
	elif verify == 'INVALID':
		print(Fore.RED+"URL or request parameters are invalid"+Fore.RESET)	
	else:
		print(Fore.RED+"There is unknown problem with URL or request parameters"+Fore.RESET)
	#print(rparams)
	return(senDetails, tSeriesObs)
#-----------------------------------------------------------------------
# Implementation
# 1. NDBC
# e.g. URL's
# NDBC Ex 1
ndbcGO = "http://sdf.ndbc.noaa.gov/sos/server.php"
# XML
NDBCxml = "http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:station:wmo:41063&procedure=urn:ioos:station:wmo:41063&eventTime=2014-04-30T07:00:00Z/2014-05-30T07:00:00Z&observedProperty=air_temperature&responseFormat=text/xml;subtype=%22om/1.0.0%22"
# CSV
NDBCcsv = "http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:station:wmo:41063&procedure=urn:ioos:station:wmo:41063&eventTime=2014-04-30T07:00:00Z/2014-05-30T07:00:00Z&observedProperty=air_temperature&responseFormat=text/csv"
NDBCrparams = {"service": "SOS",\
		 "offering": "urn:ioos:station:wmo:41063",\
		 "request": "GetObservation",\
		 "version": "1.0.0",\
		 "observedProperty": "air_temperature",\
		 "procedure": "urn:ioos:station:wmo:41063"}
# Enter pre formatted time series for NDBC
NDBCstartDate = "2014-04-30T07:00:00Z"
NDBCendDate = "2014-05-30T07:00:00Z"
# e.g. 1 
# tmp = dateutil.parser.parse("2014-04-30T07:00:00Z")
# tmp = tmp.strftime('%Y-%m-%dT%H:%M:%S')
# tmp = tmp+'Z'
# e.g. 2
#NDBCstartDate = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
#NDBCendDate = datetime.datetime(2014,05,07,20,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
#
NDBCrparams['eventTime'] = str(NDBCstartDate) + "/" +str(NDBCendDate) # observations from start date to end date
#---
# NDBC Ex 2
NDBCparams2 = "http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:station:wmo:41012&observedproperty=air_pressure_at_sea_level&responseformat=text/csv&eventtime=2014-02-10T12:50:00Z/2014-02-19T12:50:00Z"
NDBCrparams2 = {"service": "SOS",\
		 "offering": "urn:ioos:station:wmo:41012",\
		 "request": "GetObservation",\
		 "version": "1.0.0",\
		 "observedProperty": "air_pressure_at_sea_level",\
		 "procedure": "urn:ioos:station:wmo:41012"}
NDBCstartDate2 = "2014-02-10T12:50:00Z"
NDBCendDate2 = "2014-02-19T12:50:00Z"
NDBCrparams2['eventTime'] = str(NDBCstartDate2) + "/" +str(NDBCendDate2) # observations from start date to end date
#-----------------------------------------------------------------------
# 2. ISTSOS
# ISTSOS Ex 1
istsosGO = "http://istsos.org/istsos/demo"
# JSON
istsosJSON = "http://istsos.org/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=BELLINZONA&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&responseFormat=application/json"
# CSV
istsosPlain = "http://istsos.org/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=BELLINZONA&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&responseFormat=text/plain"
#
startDate = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
endDate = datetime.datetime(2014,05,07,20,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
ISTSOSrparams = {}
ISTSOSrparams = {"service": "SOS",\
		 "offering": "BELLINZONA",\
		 "request": "GetObservation",\
		 "version": "1.0.0",\
		 "observedProperty": "air:temperature",\
		 "procedure": "BELLINZONA"}
ISTSOSrparams['eventTime'] = str(startDate) + "/" +str(endDate) # observations from start date to end date
# ISTSOS Ex 2

"""
#
print('ISTSOS Request 1')
aa, bb = parseSOSgetObs(istsosGO, ISTSOSrparams, responseFormat='plain')
print(aa)
print(len(bb))
#
print('ISTSOS Request 2')	
aa, bb = parseSOSgetObs(istsosGO, ISTSOSrparams, responseFormat='JSON')
print(aa)
print(len(bb))
#
print('NDBC Request 1')	
print(NDBCrparams)
aa, bb = parseSOSgetObs(ndbcGO, NDBCrparams, responseFormat='csv')
print(aa)
print(len(bb))
#
print('NDBC Request 2')	
print(NDBCrparams2)
aa, bb = parseSOSgetObs(ndbcGO, NDBCrparams2, responseFormat='csv')
print(aa)
print(len(bb))
"""
