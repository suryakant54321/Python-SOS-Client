#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 12 June 2016 
# Objective: Sensor Observation Service based ETo estimation functions
# 
# Depends on:
# 	fao_eto
#	sosParseCap
#	sosParseGetObs
# 	sosTsPandas
# 
# Note:
# 	Lines marked with #** are hard coaded
#-----------------------------------------------------------------------
"""
#
from fao_eto import *
import sosParseCap as pc
import sosParseGetObs as go
import sosTsPandas as st
#-----------------------------------------------------------------------
global url, getCapStr
url = 'http://localhost/istsos/service'
# Get capabilities string
getCapStr = '?request=getCapabilities&section=contents&service=SOS'
#-----------------------------------------------------------------------
def getAllObs():
	"""
	Steps:	
		Get observations for one week 
		Selected sensors (Temperature, Humidity, Rainfall, Wind Speed, Solar Radiation)

		TODO:
		Process all observations for daily stats (i.e. mean, sum, max, min)
		Unit conversions if any
		
		TODO (low priority): Get Observations for specified date/ week/ season

	Input/s:
		url [str]
		

	Output/s:
		Observations [[str]]
	"""
	nUrl = url+getCapStr
	# send Get Capabilities Request
	out = pc.parseSOScap(nUrl)
	out = out[0]
	#print(out)
	#
	endTime = out['timeEndPosition']
	startTime = dateutil.parser.parse(endTime)
	# Select start time with 7 days (week) difference
	startTime = startTime-datetime.timedelta(days=7)
	startTime = str(startTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
	# assign details for request
	go.ISTSOSrparams['eventTime'] = ("%s/%s")%(startTime, endTime)
	go.ISTSOSrparams['offering'] = out['offering']
	#
	# 1. For Temperature (degree Celsius)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][0]# **
	go.ISTSOSrparams['procedure'] = out['procedure'][6]# **
	# send Get Observation request
	aaT, bbT = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	# process Get Observation response	
	minObsT = st.tsOperation(aaT, bbT, operation='min', sampleTime='24H')
	maxObsT = st.tsOperation(aaT, bbT, operation='max', sampleTime='24H')
	meanObsT = st.tsOperation(aaT, bbT, operation='mean', sampleTime='24H')
	print(minObsT, maxObsT, meanObsT)
	#
	# 2. For Relative Humidity (%)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][3]# **
	go.ISTSOSrparams['procedure'] = out['procedure'][2]# **
	# send Get Observation request
	aaH, bbH = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	# process Get Observation response	
	minObsH = st.tsOperation(aaH, bbH, operation='min', sampleTime='24H')
	maxObsH = st.tsOperation(aaH, bbH, operation='max', sampleTime='24H')
	meanObsH = st.tsOperation(aaH, bbH, operation='mean', sampleTime='24H')
	print(minObsH, maxObsH, meanObsH)
	#
	# 3. For rainfall (mm)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][4]# **
	go.ISTSOSrparams['procedure'] = out['procedure'][3]# **
	# send Get Observation request
	aaR, bbR = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	# process Get Observation response	
	sumObsR = st.tsOperation(aaR, bbR, operation='sum', sampleTime='24H')
	countObsR = st.tsOperation(aaR, bbR, operation='count', sampleTime='24H')
	print(sumObsR,"\n Count is \n",countObsR)
	#
	# 4. For Radiation (in W m-2)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][6] # **
	go.ISTSOSrparams['procedure'] = out['procedure'][5] # **
	# send Get Observation request
	aaRad, bbRad = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	# process Get Observation response	
	sumObsRad = st.tsOperation(aaRad, bbRad, operation='sum', sampleTime='24H')
	countObsRad = st.tsOperation(aaRad, bbRad, operation='count', sampleTime='24H')
	#print(bbRad)
	print(sumObsRad,"\n Count is \n", countObsRad)
	#
	# 5. For Wind Speed (in kmph)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][8] # **
	go.ISTSOSrparams['procedure'] = out['procedure'][8] # **
	# send Get Observation request
	aaWs, bbWs = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	# process Get Observation response	
	meanObsWs = st.tsOperation(aaWs, bbWs, operation='mean', sampleTime='24H')
	#print(bbRad)
	print(meanObsWs)
	# TODO
	# Compile all observations
	# Convert units of observations

	"""
	if minObsH !=[] and maxObsH != []:
		for i in range(len(maxObsH)):
			if i != 0:
				msgOut = msgOut+'Date: '+ str(minObsH[i][0]) +', Min= '+ str(minObsH[i][1]) + ', Max= '+  str(maxObsH[i][1]) +' \n'
	else:
		msgOut = msgOut + "Some problem\n Retry after some time."
	msgOut = msgOut
	print(msgOut)
	"""
#
def refEt():
	"""
	Calculate reference ET using PM or Hargreves method

	Input/s:
		
	Output/s:
		
	"""
#-----------------------------------------------------------------------
getAllObs()
