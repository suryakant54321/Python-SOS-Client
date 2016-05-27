"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 22 May 2016
# Application Name: SOS-Telegram-Client
#
# Flow: 1. Get Capabilities (sosParseCap.py)	
#		Status: Complete
#	2. Describe Sensor (sosParseDSensor.py)
#		Status: Complete
#	3. Get Observation (sosParseGetObs.py)
#		Status: Complete
# 	4. Process Observations (sosParseGetObs.py)
#		Status: Complete
#	To Do:
#	5. Compose and push message on Telegram bot (teleCompose.py)
		bot get SOS URL/s (NDBC, ISTSOS, SenseTube, etc.)
		bot GetCapabilities
		bot DescribeSensor
		bot GetObservation (raw csv)
		bot GetObservation (processed mean, max, min, median, sum, etc.)
		bot GetObservation (graph)
#
# Improvement/s
# 	7. Receive commands from user on Telegram bot
#	8. Execute process from (1 to 5)
#-----------------------------------------------------------------------
"""
# 1. Example of Get Capabilities and Get Observation Request
# GetObservation flow for new service
import sosParseCap.py as pc
import sosParseGetObs as go
#
help(pc)
print(pc.url)
pc.url = 'http://localhost/istsos/service?request=getCapabilities&section=contents&service=SOS'
cap = pc.parseSOScap(pc.url)
print(cap)

# local url
url = "http://localhost/istsos/service"
go.startDate = '2012-11-30T20:30:11+0530'
go.endDate = '2012-11-30T23:45:15+0530'

go.ISTSOSrparams['eventTime']=go.startDate+'/'+go.endDate
go.ISTSOSrparams['observedProperty']='urn:ogc:def:parameter:x-ksos:1.0:aws:station1:air_temperature'
go.ISTSOSrparams['offering']='base_station_1'
go.ISTSOSrparams['procedure']='temp_1'
#
msg, data = go.parseSOSgetObs(uurl, go.ISTSOSrparams, responseFormat='JSON')
#
print(msg)
print(data)

