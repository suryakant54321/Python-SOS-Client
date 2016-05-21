"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 13 May 2016 >> 22 May 2016
# Objective: SOS time series data analysis using Pandas
# 	supported operations mean, median, max, min and sum
#	sampling interval depends on data (24H, week, etc.)
#-----------------------------------------------------------------------
"""
import pandas as pd
import re
from colorama import Fore, Back, Style
#-----------------------------------------------------------------------
def tsOperation(message, data, operation='mean', sampleTime='24H'):
	"""
	function to execute operation on time series data
	
	inputs:
		1. message {dict}

		2. data [[list]] nested list

		3. operation name [str]
			default mean
			supported operations mean, median, max, min and sum

		4. sampleTime / time interval [str]
			default 24H (i.e. 1 day)
			support depends on the sampling frequency of data
	output:
		1. List output of time series operation
			e.g. [['dateTime', 'val'], ['2014-05-03 16:00:00', '19.275'], ...]
	"""
	operationSupport = ['sum', 'mean', 'max', 'median', 'min']
	meanTsList = []
	if operation.lower() in operationSupport: 
		df = pd.DataFrame(data, columns=["dateTime", "val"]) # create dataframe
		df['dateTime'] = pd.to_datetime(df['dateTime']) # convert data type of datetime
		df.index = pd.to_datetime(df.dateTime) # assign index to dataframe
		df['val'] = df.val.convert_objects(convert_numeric=True) # convert data type of temp column to numeric
		#print(df.dtypes)# data type of dataframe varaibles
		#print(df.resample(sampleTime, how = operation))
		#
		meanTs = df.resample(sampleTime, how = operation) # mean of selected time series
		meanTsCsv = meanTs.to_csv()
		meanTsCsv = meanTsCsv.rstrip('\n') 
		meanTsList = re.split(',|\\n',meanTsCsv)
		#
		# using splitLst function to split list
		meanTsList = splitLst(meanTsList, int(len(meanTsList)/2))
		#
	else:
		print(Fore.RED+"invalid operation '"+operation+"' \n Returning empty list \n current support limited to mean, median, max, min and sum."+Fore.RESET)
	return(meanTsList)
#-----------------------------------------------------------------------
def splitLst(splitL, lRank):
	"""
	function to split list into given rank
	splitL [list] input list to split	
	lRank [int] 
	"""	
	length = len(splitL)
	if length >= lRank:
		return [splitL[i*length // lRank: (i+1)*length // lRank] for i in range(lRank) ]
	else:
		print("input list is smaller than expected split \n doing nothing")
		return splitL
#-----------------------------------------------------------------------
"""
# Implementation
import sosParseGetObs as go
# get observation from web URL
message, data = go.parseSOSgetObs(go.istsosGO, go.ISTSOSrparams, responseFormat='plain')
print(message)
print(len(data))
result = tsOperation(message, data, operation='mean', sampleTime='24H')
print(result)
print("--------------------------------------------------------------------------------")
# get observation from web URL
message, data = go.parseSOSgetObs(go.istsosGO, go.ISTSOSrparams, responseFormat='JSON') 
print(message)
print(len(data))
result = tsOperation(message, data, operation='mean', sampleTime='24H')
print(result)
print("--------------------------------------------------------------------------------")
# get observation from web URL
message, data = go.parseSOSgetObs(go.ndbcGO, go.NDBCrparams, responseFormat='csv')
print(message)
print(len(data))
result = tsOperation(message, data, operation='mean', sampleTime='24H')
print(result)
print("--------------------------------------------------------------------------------")
# get observation from web URL
message, data = go.parseSOSgetObs(go.ndbcGO, go.NDBCrparams2, responseFormat='csv')
print(message)
print(len(data))
result = tsOperation(message, data, operation='mean', sampleTime='24H')
print(result)
#
"""
