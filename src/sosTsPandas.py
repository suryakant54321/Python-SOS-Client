"""
#-----------------------------------------------------------------------
# Author: Suryakant Sawant
# Date: 13 May 2016
# Objective: SOS time series analysis using Pandas 
# Requirement: sosReq.py
#
#-----------------------------------------------------------------------
"""
import sosReq
message, data = sosReq.meanTemp() # hard coaded for some site

print(message)

print(data)

import pandas as pd
import re

df = pd.DataFrame(data, columns=["dateTime", "temp"]) # create dataframe

df['dateTime'] = pd.to_datetime(df['dateTime']) # convert data type of datetime

df.index = pd.to_datetime(df.dateTime) # assign index to dataframe

df['temp'] = df.temp.convert_objects(convert_numeric=True) # convert data type of temp column to numeric

print(df.dtypes)# data type of dataframe varaibles

print(df.resample('D', how = 'mean'))

meanTs = df.resample('D', how = 'mean') # mean of selected time series

meanTsCsv = meanTs.to_csv()

meanTsCsv = meanTsCsv.rstrip('\n') 

meanTsList = re.split(',|\\n',meanTsCsv)

#
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

# using above function to split list
meanTsList = splitLst(meanTsList, int(len(meanTsList)/2))

print(message)
print("mean daily values are:")
for i in range(len(meanTsList)):
	if i != 0 and meanTsList != [] and meanTsList != 'None':
		print("Date",meanTsList[i][0],"Mean temperature",meanTsList[i][1])
#

