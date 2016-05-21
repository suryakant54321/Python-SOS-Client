"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 13 May 2016 >> 17 may 2016
# Objective: 	1. standalone interfase for SOS requests and response 
#		2. 
#-----------------------------------------------------------------------
"""
import re, os, fnmatch
from colorama import Fore, Back, Style
#
# Original snippet
# Source URL: http://istsos.org/en/latest/doc/wns.html
#-----------------------------------------------------------------------
# IMP Steps

def meanTemp():
	"""
	
	1. Send get request to SOS service
	2. Capture response in JSON
	3. Parse Response
	4. Calculate the mean of parameter
        5. Returns data and message

	Help:
	1. Sample Get Capabilities request
		http://istsos.org/istsos/demo?request=getCapabilities&section=contents&service=SOS
	
	2. Sample Describe Sensor request
		http://istsos.org/istsos/demo?request=DescribeSensor&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&outputFormat=text%2Fxml%3Bsubtype%3D%22sensorML%2F1.0.1%22&service=SOS&version=1.0.0
		
		http://istsos.org/istsos/demo?request=DescribeSensor&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&outputFormat=text/xml%3Bsubtype=%22sensorML/1.0.1%22&service=SOS&version=1.0.0			 
		
	# Note the difference between outputFormat and responseFormat		
		
	3. A Sample Get Observation request 
		a. JSON request URL format
	http://istsos.org/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=BELLINZONA&procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&responseFormat=application/json

		b. JSON Request split
	http://istsos.org/istsos/demo?
		service=SOS&
		version=1.0.0&
		request=GetObservation&
		offering=BELLINZONA&
		procedure=urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA&
		eventTime=2014-05-03T16:30:00+02:00/2014-05-04T16:30:00+02:00&
		observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature&
		responseFormat=application/json
	"""
	import datetime #
	import time # 
	from pytz import timezone # for timezone conversion
	message = "Some error"
	# time.tzname[0] was unable to find time zone for IST
	#now = datetime.datetime.now().replace(tzinfo=timezone(time.tzname[0]))
	#endDate = now.strftime('%Y-%m-%dT%H:%M:%S%z')
	#eventTime = now - datetime.timedelta(hours=5)

	#startDate = eventTime.strftime('%Y-%m-%dT%H:%M:%S%z')
	#startDate = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone(time.tzname[0])).strftime('%Y-%m-%dT%H:%M:%S%z')
	startDate = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
        startD = datetime.datetime(2014,05,03,16,30,0, tzinfo=timezone('UTC'))
	#endDate = datetime.datetime(2014,05,03,20,30,0, tzinfo=timezone(time.tzname[0])).strftime('%Y-%m-%dT%H:%M:%S%z')
	endDate = datetime.datetime(2014,05,07,20,30,0, tzinfo=timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
        endD = datetime.datetime(2014,05,07,20,30,0, tzinfo=timezone('UTC'))
        diff = endD - startD
        days = diff.days
        hours = (diff.seconds/3600)
        secs = (diff.seconds-(hours*3600))/60
	print (startDate, endDate)
	
	rparams = {"service": "SOS", "offering": "BELLINZONA", "request": "GetObservation", "version": "1.0.0", "responseFormat": "application/json", "observedProperty": "air:temperature", "procedure": "BELLINZONA"}

	rparams['eventTime'] = str(startDate) + "/" +str(endDate)

	import requests as requests
	res = requests.get('http://istsos.org/istsos/demo', params=rparams)

	result = res.json()['ObservationCollection']['member'][0]['result']['DataArray']['values']
	placeName = res.json()['ObservationCollection']['member'][0]['name']
	mean = 0
	count = 0

	for el in result:
		if float(el[1]) != -999.9:
			mean += float(el[1])
			count += 1

	if len(result) == 0:
		message = "Cannot make mean with no data"
	else:
		mean = mean / count
		message = "At "+ str(placeName) +" for last "+str(days)+" day/s, "+str(hours)+" hour/s, "+str(secs)+" seconds average temperature = " + str(mean)
	"""	
	# 
	# this structure is mandatory to send notification
    	notify = {\
		"twitter": {\
		"public": message,\
		"private": message\
		},\
		"mail":{\
		"subject": "mean temp from T_BELLINZONA",\
		"message": message\
		}\
		}

	# these line are mandatory
	import wnslib.notificationScheduler as nS
	nS.notify('meanTemp',notify, True)
	"""
	return(message, result)
#-----------------------------------------------------------------------
# implementation
#someMessage, data = meanTemp()
#print(someMessage)
#print(data)
# To do
# 1. Push data through Telegram Bot
# 2. Check feasibility for localhost

