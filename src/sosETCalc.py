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
# 	re
#	dateutil
#	datetime
#
# Note:
# 	Lines marked with #** are hard coaded
#-----------------------------------------------------------------------
"""
#
import fao_eto as et
import sosParseCap as pc
import sosParseGetObs as go
import sosTsPandas as st
import re, os, dateutil, datetime
#-----------------------------------------------------------------------
#global url, getCapStr
url = 'http://localhost/istsos/service'
# Get capabilities string
getCapStr = '?request=getCapabilities&section=contents&service=SOS'
#-----------------------------------------------------------------------
def checkDate(inDate, trueEndTime, trueStartTime):
	"""
	Function to check the date entered by user is valid
	
	Why?: Date entered should be available within 
		observation dates (start and end)
	
	output/s:
		dateCheck [str] TRUE / FALSE
	"""
	dateCheck = 'FALSE'
	if inDate == 'None': 
		dateCheck = 'FALSE'
	else:	
		tZone = re.split('\+',trueEndTime)
		try:
			inDate = inDate+"T00:00:00+"+tZone[1]
		except:
			pass
		inDate = dateutil.parser.parse(inDate, dayfirst='TRUE')
		#print(inDate.strftime('%Y-%m-%dT%H:%M:%S%z'))
		trueEndTime = dateutil.parser.parse(trueEndTime)
		trueStartTime = dateutil.parser.parse(trueStartTime)
		if inDate > trueEndTime: 
			dateCheck = 'FALSE'
		elif inDate < trueEndTime:
			if inDate > trueStartTime:
				diffDate = inDate - datetime.timedelta(days=7)
				if diffDate < trueStartTime: 
					dateCheck = 'FALSE'
				elif diffDate > trueStartTime: 
					dateCheck = 'TRUE'
			else:
				dateCheck = 'FALSE'
	return(dateCheck)
#
def getRefET(url, getCapStr, inDate='None'):
	"""
	Function to get observations from SOS for one week 

		process sensor observations for reference evapotranspiration estimation

		selected sensors (Temperature, Humidity, Wind Speed, Solar Radiation)

	Input/s:
		url [str] SOS url

		getCapStr [str] Get Capabilities string

		inDate [str] optional  format (dd-mm-YYYY)
			if date is not specified default last observation date is considered 
			  and observations for last 7 days are requested 
			  from SOS and processed for ETo
			
			if date is specified observations for last 7 days are requested 
			  from SOS and processed for ETo 		 

	Output/s:
		ETo Observations [[str, str, str], [str, float, float], ...]

			e.g. [['date', ETo_PM, ETo_Harg], ...]
	"""
	outETo = []
	outETo.append(['date', 'ETo_PM', 'ETo_Harg'])
	nUrl = url+getCapStr
	# send Get Capabilities Request
	out = pc.parseSOScap(nUrl)
	out = out[0]
	#print(out)
	trueEndTime = out['timeEndPosition']
	trueStartTime = out['timeBeginPosition']
	#print(inDate)
	dateCheck = checkDate(inDate, trueEndTime, trueStartTime)
	#print(dateCheck)
	if dateCheck == "FALSE": 
		#
		endTime = out['timeEndPosition']
		startTime = dateutil.parser.parse(endTime)
		# Select start time with 7 days (week) difference
		startTime = startTime-datetime.timedelta(days=7)
		startTime = str(startTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
	else:
		tZone = re.split('\+',trueEndTime)
		try:
			inDate = inDate+"T00:00:00+"+tZone[1]
			
		except:
			pass
		#print(inDate)
		endTime = dateutil.parser.parse(inDate, dayfirst='TRUE')
		startTime = endTime-datetime.timedelta(days=7)
		endTime = str(endTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
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
	try:	
		# process Get Observation response
		minObsT = st.tsOperation(aaT, bbT, operation='min', sampleTime='24H')
		maxObsT = st.tsOperation(aaT, bbT, operation='max', sampleTime='24H')
		meanObsT = st.tsOperation(aaT, bbT, operation='mean', sampleTime='24H')
		medianObsT = st.tsOperation(aaT, bbT, operation='median', sampleTime='24H')
		#print(minObsT, maxObsT, meanObsT)
	except:
		pass
	#
	# 2. For Relative Humidity (%)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][3]# **
	go.ISTSOSrparams['procedure'] = out['procedure'][2]# **
	# send Get Observation request
	aaH, bbH = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	try:
		# process Get Observation response	
		minObsH = st.tsOperation(aaH, bbH, operation='min', sampleTime='24H')
		maxObsH = st.tsOperation(aaH, bbH, operation='max', sampleTime='24H')
		meanObsH = st.tsOperation(aaH, bbH, operation='mean', sampleTime='24H')
		#print(minObsH, maxObsH, meanObsH)
	except:
		pass
	#
	"""	
	# 3. For rainfall (mm)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][4]# **
	go.ISTSOSrparams['procedure'] = out['procedure'][3]# **
	# send Get Observation request
	aaR, bbR = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	try:
		# process Get Observation response	
		sumObsR = st.tsOperation(aaR, bbR, operation='sum', sampleTime='24H')
		countObsR = st.tsOperation(aaR, bbR, operation='count', sampleTime='24H')
		#print(sumObsR,"\n Count is \n",countObsR)
	except:
		pass
	"""
	#
	# 4. For Radiation (in W m-2)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][6] # **
	go.ISTSOSrparams['procedure'] = out['procedure'][5] # **
	# send Get Observation request
	aaRad, bbRad = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	try:
		# process Get Observation response	
		sumObsRad = st.tsOperation(aaRad, bbRad, operation='sum', sampleTime='24H')
		meanObsRad = st.tsOperation(aaRad, bbRad, operation='mean', sampleTime='24H')
		countObsRad = st.tsOperation(aaRad, bbRad, operation='count', sampleTime='24H')
		#print(bbRad)
		#print(sumObsRad,"\n Count is \n", countObsRad)
	except:
		pass
	#
	# 5. For Wind Speed (in kmph)
	go.ISTSOSrparams['observedProperty'] = out['observedProperties'][8] # **
	go.ISTSOSrparams['procedure'] = out['procedure'][8] # **
	# send Get Observation request
	aaWs, bbWs = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	try:
		# process Get Observation response	
		meanObsWs = st.tsOperation(aaWs, bbWs, operation='mean', sampleTime='24H')
		#print(bbRad)
		#print(meanObsWs, len(meanObsWs))
	except:
		pass
	#"""
	# Input parameters
	# Latitude (degree)
	latLon = out['lowerCorner']
	latLon = re.split('\ ', latLon)[0]
	latLon = re.split(',', latLon)
	myLat = float(latLon[0])
	myLon = float(latLon[1])
	etCalc = []
	if minObsT !=[] and maxObsT != []:
		for i in range(len(maxObsT)):
			etCalc = []
			if i != 0:	
				# Date
				myDate = str(maxObsT[i][0])
				if len(meanObsWs) == len(minObsT):
					# Wind Speed (m s-1)
					ws = float(meanObsWs[i][1])
					# kmph to m s-1 conversion
					ws = (((ws+0.0000001)*1000)/3600)
				else:					
					ws = 0.001 # assumption
				# Altitude (m) # TODO: need to send Describe sensor request
				alt = 650 # Assumption
				# mean Temperature (degree Celsius)
				maxT = float(maxObsT[i][1])
				minT = float(minObsT[i][1])
				meanT = float(meanObsT[i][1])
				# Temperature / mean / median
				t = float(medianObsT[i][1])
				# meanT = daily_mean_t(maxT, minT) # not used
				# Relative Humidity (%)
				RHMin = float(minObsH[i][1])
				RHMax = float(maxObsH[i][1])
				# sunshine duration (hours)
				#print(myDate, ws, maxT, minT, meanT, t, RHMin, RHMax)
				#------------------------------------------------------------
				# input altitude
				press = et.atmos_pres(alt)
				# saturated vapour pressure
				satPres = et.delta_sat_vap_pres(meanT)
				# Mean sat vap. press.
				meanEs = et.mean_es(maxT, minT)
				#e_tmin = et.delta_sat_vap_pres(23.22)
				#e_tmax = et.delta_sat_vap_pres(36.47)
				e_tmin = et.sat_vap_press(minT)
				e_tmax = et.sat_vap_press(maxT)
				# actual vapour pressure [kPa] from RHMin and RHMax
				EaCalc = et.ea_from_rhmin_rhmax(e_tmin, e_tmax, RHMin, RHMax)
				# Get doy from date
				doy = et.getDoy(myDate)
				# inverse distance of earth and sun
				invDist = et.inv_rel_dist_earth_sun(doy)
				# Solar declination
				solar_dec = et.sol_dec(doy)
				# sunset hour angle
				sha = et.sunset_hour_angle(myLat, solar_dec)
				# Calculates daily extraterrestrial radiation 'Ra' 
				# i.e. top of the atmosphere radiation [MJ m-2 day-1]
				et_rad = et.et_rad(myLat, solar_dec, sha, invDist)
				# clear sky radiation [MJ m-2 day-1]
				clear_sky_rad = et.clear_sky_rad(alt, et_rad)
				# day length hours
				dl_hours = et.dlHours(sha)
				# =====
				# if sunshine duration data are available use sol_rad_from_sun_hours()
				if len(countObsRad) == len(maxObsT):
					if float(countObsRad[i][1]) > 20.00:
						sun_hours = ((countObsRad[i][1]*15)/60) # observation interval 15 minutes
						solRad = et.sol_rad_from_sun_hours(dl_hours, sun_hours, et_rad)
					else:
						# sunshine duration data is unavailable
						solRad = et.sol_rad_from_t(et_rad, clear_sky_rad, minT, maxT, coastal=-999)
				else:
					# sunshine duration data is unavailable
					solRad = et.sol_rad_from_t(et_rad, clear_sky_rad, minT, maxT, coastal=-999)
				# =====
				# net incoming solar (also known as shortwave) radiation [MJ m-2 day-1]
				NetSolRad = et.net_in_sol_rad(solRad)
				# net outgoing longwave radiation [MJ m-2 day-1]
				nLwOutRad = et.net_out_lw_rad(minT, maxT, solRad, clear_sky_rad, EaCalc)
				# =====
				# if radiation sensor data is available
				if len(countObsRad) == len(maxObsT):
					if float(countObsRad[i][1]) > 20.00:
						# mean observation * number of samples * sampling interval
						# TODO: Get sampling interval from describe sensor request
						NetR = ((float(meanObsRad[i][1])*float(countObsRad[i][1])*15.0)/(1000000.0))# observation interval 15 minutes
					else:		
						# daily net radiation [MJ m-2 day-1] at the crop surface
						NetR = et.net_rad(NetSolRad, nLwOutRad)
				else:
					# daily net radiation [MJ m-2 day-1] at the crop surface
					NetR = et.net_rad(NetSolRad, nLwOutRad)
				# =====
				# psychrometric constant (kPa degC-1)
				psy = et.psy_const(press)
				# PM ETo
				EToPM = et.penman_monteith_ETo(NetR, t, ws, meanEs, EaCalc, satPres, psy, shf=0.0)
				# soil heat fraction (shf) is zero
				Ra = et.rad2equiv_evap(et_rad)
				# Harg. ETo
				EToHarg = et.hargreaves_ETo(minT, maxT, meanT, Ra)
				etCalc.append(myDate)
				etCalc.append(EToPM)
				etCalc.append(EToHarg)
				outETo.append(etCalc)
				#print(myDate, EToPM, EToHarg)
				#"""
	else:
		outETo.append(etCalc)
		#print(('No observations available for dates between %s and %s')%(startTime, endTime))
	return(outETo)
#
def getIrriSchedule():
	"""
	Estimate irrigation schedule using crop water balance

	Input/s:
		
		
	Output/s:
		
				
	"""
#-----------------------------------------------------------------------
# implementation
"""
print(getRefET(url, getCapStr))
print(getRefET(url, getCapStr, '10-12-2015'))
print(getRefET(url, getCapStr, '10-12-2014'))
print(getRefET(url, getCapStr, '10-12-2012'))
print(getRefET(url, getCapStr, '10-12-2013'))
print(getRefET(url, getCapStr, '10-12-2019'))
print(getRefET(url, getCapStr, '10-12-2011'))
"""
