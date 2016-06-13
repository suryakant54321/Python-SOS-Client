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
	allObs = []
	if minObsT !=[] and maxObsT != []:
		for i in range(len(maxObsT)):
			if i != 0:
				datStr = str(minObsT[i][0]) +',
	"""
	#"""
	from fao_eto import *
	# Input parameters
	myDate = str('20-12-2015')
	# Wind Speed (m s-1)
	ws = 1.157
	# Altitude (m)
	alt = 500
	# mean Temperature (degree Celsius)
	maxT = 36.47
	minT = 23.22
	meanT = daily_mean_t(maxT, minT)
	# Relative Humidity (%)
	RHMin = 39.42
	RHMax = 87.48
	# Latitude (degree)
	myLat = 10.48
	# sunshine duration (hours)
	sun_hours = 9.83

	#------------------------------------------------------------
	# input altitude
	press = atmos_pres(alt)
	# saturated vapour pressure
	satPres = delta_sat_vap_pres(meanT)
	# Mean sat vap. press.
	meanEs = mean_es(maxT, minT)
	#e_tmin = delta_sat_vap_pres(23.22)
	#e_tmax = delta_sat_vap_pres(36.47)
	e_tmin = sat_vap_press(minT)
	e_tmax = sat_vap_press(maxT)
	# actual vapour pressure [kPa] from RHMin and RHMax
	EaCalc = ea_from_rhmin_rhmax(e_tmin, e_tmax, RHMin, RHMax)
	# Get doy from date
	doy = getDoy(myDate)
	# inverse distance of earth and sun
	invDist = inv_rel_dist_earth_sun(doy)
	# Solar declination
	solar_dec = sol_dec(doy)
	# sunset hour angle
	sha = sunset_hour_angle(myLat, solar_dec)
	# Calculates daily extraterrestrial radiation 'Ra' 
	# i.e. top of the atmosphere radiation [MJ m-2 day-1]
	et_rad = et_rad(myLat, solar_dec, sha, invDist)
	# clear sky radiation [MJ m-2 day-1]
	clear_sky_rad = clear_sky_rad(alt, et_rad)
	# day length hours
	dl_hours = dlHours(sha)
	# =====
	# ----
	# if sunshine duration data are available use sol_rad_from_sun_hours()
	solRad = sol_rad_from_sun_hours(dl_hours, sun_hours, et_rad)
	# ---- 
	# use if sunshine duration data is unavailable
	solRad = sol_rad_from_t(et_rad, clear_sky_rad, minT, maxT, coastal=-999)
	# =====
	# net incoming solar (also known as shortwave) radiation [MJ m-2 day-1]
	NetSolRad = net_in_sol_rad(solRad)
	# net outgoing longwave radiation [MJ m-2 day-1]
	nLwOutRad = net_out_lw_rad(minT, maxT, solRad, clear_sky_rad, EaCalc)
	# daily net radiation [MJ m-2 day-1] at the crop surface
	NetR = net_rad(NetSolRad, nLwOutRad)
	# psychrometric constant (kPa degC-1)
	psy = psy_const(press)
	# Temperature / mean / median
	t = meanT
	# PM ETo
	EToPM = penman_monteith_ETo(NetR, t, ws, meanEs, EaCalc, satPres, psy, shf=0.0)
	# soil heat fraction (shf) is zero
	Ra = rad2equiv_evap(et_rad)
	# Harg. ETo
	EToHarg = hargreaves_ETo(minT, maxT, meanT, Ra)
	print(EToPM, EToHarg)
	#"""
#
def refEt():
	"""
	Calculate reference ET using PM or Hargreves method

	Input/s:
		
	Output/s:
		
	"""
#-----------------------------------------------------------------------
getAllObs()
