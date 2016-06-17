#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-----------------------------------------------------------------------
# Source Details: https://github.com/python-telegram-bot/python-telegram-bot/examples
#
# Modified by: Suryakant Sawant
# Date: 8 June 2016
#
# Objective: IWC Sensor Observation Service (SOS) Telegram Messaging Bot
#
# 1. This Bot uses the Updater class to handle the bot.
# 2. Modified Echobot example (https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py).
# 3. Press Ctrl-C on the command line or send a signal to the process to stop the bot.
# 4. User commands are processed for obtaining sensor capabilities, Observations and Measurements.
#
1. Add more intearctive user commands 
#	a. Sensor system list
#	b. Sensor selection (temperature, humidity, etc.)
#	c. Sensor observation listing
#	d. Summary statistics of time series observation  
# 2. Process output response using markup tags (HTML, etc.) 
# 3. Design response format in both English and Marathi Language
#-----------------------------------------------------------------------
"""
#-----------------------------------------------------------------------
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import datetime, re, os
import dateutil
import csv
#-----------------------------------------------------------------------
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
# Command handlers
def start(bot, update):
	msgCont = 'Welcome to Automatic Weather Station (AWS) Telegram bot \n Enter /help for more information. \n नमस्कार ... \n हे  हवामान केंद्राचे Telegram Bot (रोबोट) आहे. \n अधिक माहितीसाठी /help मेसेज पाठवा.'
	bot.sendMessage(update.message.chat_id, text=msgCont)
# 1
def help(bot, update):
	msgCont = 'For more information enter following commands \n अधिक माहितीसाठी खाली दिलॆलॆ मेसेज पाठवा \n /whoami (मी कॊण आहॆ?) \n /whichSensors (हवामान केंद्राची अधिक माहिती.) \n /getTemp (Air Temperature हवेचे तापमान) \n /getHum (Relative Humidity हवेची सापेक्ष आद्रता) \n /getRain (Rainfall पर्जन्य)\n /getRefET (daily grass / reference Evaporation + Transpiration \n    गवतावरील दैनिक बाष्पीभवन + पाणी वापर मोजणी) )'
	bot.sendMessage(update.message.chat_id, text=msgCont)
# 2
def whoami(bot, update):
	msgCont = 'I am Telegram based AWS sensor information bot. \n मी  Telegram मधॆ तयार कॆलॆला रोबोट आहे. \n मी तुम्हाला हवामान केंद्राची माहीति मिळवण्यासाठी मदत करॆन. \n अधिक माहितीसाठी /morewhoami मेसेज पाठवा'
	bot.sendMessage(update.message.chat_id, text=msgCont)
# 3
def morewhoami(bot, update):
	msgCont = u"कृषीसेन्स (KrishiSense) हा Telegram bot प्रायोगिक तत्वावर फक्त ITRA Water प्रोजेक्ट साठी बनवण्यात आलेला आहे. \n KrishiSense Telegram bot is designed specifically for ITRA Water project. \n सुरुवातीच्या काही महिन्यांमध्ये हा bot सतत बदलत आहे. काही कारणास्तव त्रुटी किवा चुकीची माहिती प्रसारित करण्याची शक्यता आहे. \n This bot is under test for few months and there is possibility of wrong results. \n ----- \n आपल्या शंका कींवा प्रश्न /query 'आपली शंका' लिहून पाठवू शकता. \n Users are requested to submit their questions or concerns on chat window using /query 'your query'. \n ----- \n Location of AWS (हवामान केंद्राचे ठीकान)  \n Village (गाव): Bargaon (बारगाव), \n Tahsil (तालुका): Warud (वरुड), \n Dist (जिल्हा): Amravati (अमरावती), \n ----- \n Designed By: Suryakant Sawant (PhD Research Scholar, IIT Bombay). \n email: suryakant54321@gmail.com \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा.)"
	bot.sendMessage(update.message.chat_id, text=msgCont)
# 4
def whichSensors(bot, update):
	msgCont = "I can provide (सध्या मी तूम्हाला खालील माहीती देण्यासाठी सक्षम आहे) \n 1. Temperature (हवेचे तापमान) in degree Celsius,\n 2. Humidity (हवेची सापेक्ष आद्रता) in % \n 3. Rainfall (पर्जन्य) in mm \n"
	bot.sendMessage(update.message.chat_id, text=msgCont)
# 5
def ISTSOSCap(bot, update):
	import sosParseCap as pc
	out = pc.parseSOScap(pc.url)
	out = str(out[0])
	out = out+"\n to get observations send /getObs request"
	bot.sendMessage(update.message.chat_id, text=out)
# 6
def getObs(bot, update):
	import sosParseGetObs as go
	aa, bb = go.parseSOSgetObs(go.istsosGO, go.ISTSOSrparams, responseFormat='plain')
	out = "Observation details: \n"+str(aa)+" \n Observations: \n "
	import sosTsPandas as st
	result = st.tsOperation(aa, bb, operation='mean', sampleTime='24H')
	out = out+ str(result)
	out = out+"\n to get summary of observations send /getObsSummary request"
	bot.sendMessage(update.message.chat_id, text=out)
# 7
def getTemp(bot, update):
	import sosParseCap as pc
	nUrl = url+getCapStr
	out = pc.parseSOScap(nUrl)
	out = out[0]
	obsProp = out['observedProperties'][0]
	offering = out['offering']
	procedure = out['procedure'][6]
	endTime = out['timeEndPosition']
	startTime = dateutil.parser.parse(endTime)
	startTime = startTime-datetime.timedelta(days=7)
	startTime = str(startTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
	# calling get observation function		
	import sosParseGetObs as go
	# assign details for request
	go.ISTSOSrparams['eventTime'] = ("%s/%s")%(startTime, endTime)
	go.ISTSOSrparams['observedProperty'] = obsProp
	go.ISTSOSrparams['procedure'] = procedure
	go.ISTSOSrparams['offering'] = offering
	aa, bb = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	
	msgOut = "Temperature (हवेचे तापमान) in degree Celsius \n \n"
	# process output	
	import sosTsPandas as st
	minObs = st.tsOperation(aa, bb, operation='min', sampleTime='24H')
	maxObs = st.tsOperation(aa, bb, operation='max', sampleTime='24H')
	if minObs !=[] and maxObs != []:
		for i in range(len(maxObs)):
			if i != 0:
				msgOut = msgOut+'Date (तारिख): '+ str(minObs[i][0]) +', Min (किमान) = '+ str(minObs[i][1]) + ', Max (कमाल) = '+  str(maxObs[i][1]) +' \n'
	else:
		msgOut = msgOut + "Some problem (काही अंतर्गत समस्या)\n Retry after some time (काही वेळानंतर पुन्हा प्रयत्न करा)."
	msgOut = msgOut + '\n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा.)'
	bot.sendMessage(update.message.chat_id, text=msgOut)
# 8
def getHum(bot, update):
	import sosParseCap as pc
	nUrl = url+getCapStr
	out = pc.parseSOScap(nUrl)
	out = out[0]
	obsProp = out['observedProperties'][3]
	offering = out['offering']
	procedure = out['procedure'][2]
	endTime = out['timeEndPosition']
	startTime = dateutil.parser.parse(endTime)
	startTime = startTime-datetime.timedelta(days=7)
	startTime = str(startTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
	# calling get observation function		
	import sosParseGetObs as go
	# assign details for request
	go.ISTSOSrparams['eventTime'] = ("%s/%s")%(startTime, endTime)
	go.ISTSOSrparams['observedProperty'] = obsProp
	go.ISTSOSrparams['procedure'] = procedure
	go.ISTSOSrparams['offering'] = offering
	aa, bb = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	
	msgOut = "Humidity (हवेची सापेक्ष आद्रता) in % \n \n"
	# process output	
	import sosTsPandas as st
	minObs = st.tsOperation(aa, bb, operation='min', sampleTime='24H')
	maxObs = st.tsOperation(aa, bb, operation='max', sampleTime='24H')
	if minObs !=[] and maxObs != []:
		for i in range(len(maxObs)):
			if i != 0:
				msgOut = msgOut+'Date (तारिख): '+ str(minObs[i][0]) +', Min (किमान) = '+ str(minObs[i][1]) + ', Max (कमाल) = '+  str(maxObs[i][1]) +' \n'
	else:
		msgOut = msgOut + "Some problem (काही अंतर्गत समस्या)\n Retry after some time (काही वेळानंतर पुन्हा प्रयत्न करा)."
	msgOut = msgOut + '\n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा.)'
	bot.sendMessage(update.message.chat_id, text=msgOut)
# 9
def getRain(bot, update):
	import sosParseCap as pc
	nUrl = url+getCapStr
	out = pc.parseSOScap(nUrl)
	out = out[0]
	obsProp = out['observedProperties'][4]
	offering = out['offering']
	procedure = out['procedure'][3]
	endTime = out['timeEndPosition']
	startTime = dateutil.parser.parse(endTime)
	startTime = startTime-datetime.timedelta(days=7)
	startTime = str(startTime.strftime('%Y-%m-%dT%H:%M:%S%z'))
	# calling get observation function		
	import sosParseGetObs as go
	# assign details for request
	go.ISTSOSrparams['eventTime'] = ("%s/%s")%(startTime, endTime)
	go.ISTSOSrparams['observedProperty'] = obsProp
	go.ISTSOSrparams['procedure'] = procedure
	go.ISTSOSrparams['offering'] = offering
	aa, bb = go.parseSOSgetObs(url, go.ISTSOSrparams, responseFormat='json')
	
	msgOut = "Rainfall (पर्जन्य) in mm \n \n"
	# process output	
	import sosTsPandas as st
	sumObs = st.tsOperation(aa, bb, operation='sum', sampleTime='24H')
	if sumObs !=[]:
		for i in range(len(sumObs)):
			if i != 0:
				msgOut =msgOut+'Date (तारिख): '+str(sumObs[i][0]) +', Total (एकूण) = '+ str(sumObs[i][1]) +'\n'
	else:
		msgOut = msgOut + "Some problem (काही अंतर्गत समस्या)\n Retry after some time (काही वेळानंतर पुन्हा प्रयत्न करा)."
	msgOut = msgOut + '\n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा.)'
	bot.sendMessage(update.message.chat_id, text=msgOut)
# 10
def query(bot, update):
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	l_name = dat['from']['last_name']
	queryText = dat['text']
	print(queryText)
	qDate = datetime.datetime.fromtimestamp(dat['date'])
	qDate = qDate.strftime('%Y-%m-%dT%H:%M:%S')
	queryContent = re.split('/query',queryText)
	spaces = queryContent[1].replace(' ','')
	if queryContent[1] == u'' or spaces == u'':
		da = (u"Dear %s we received query without content. \n नमस्कार %s आपल्या शंका कींवा प्रश्नाचा मुद्दा रीकामा आहे. \n ---- \n Right format /query your text (यॊग्य मुद्दा प्रकार  /query आपला मुद्दा ).")%(f_name, f_name)
	else:
		da = (u"Dear %s we received your query: \n '%s'. \n नमस्कार %s आपली शंका कींवा प्रश्न मिळाला: \n '%s') \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा).")%(f_name, update.message.text, f_name, update.message.text)
		content = {}
		content['det']=[]
		allContent = qDate+', '+f_name+' '+l_name+', '
		content['det'].append(allContent)
		content['text']=[]
		content['text'].append(queryContent[1])
		# write file with user details
		writeContent(fName, content)
	bot.sendMessage(update.message.chat_id, text=da)
# 11
def getRefET(bot, update):
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	l_name = dat['from']['last_name']
	queryText = dat['text']
	print(queryText)
	qDate = datetime.datetime.fromtimestamp(dat['date'])
	qDate = qDate.strftime('%Y-%m-%dT%H:%M:%S')
	queryContent = re.split('/getRefET',queryText)
	spaces = queryContent[1].replace(' ','')
	import sosETCalc as et
	da =u''
	if queryContent[1] == u'' or spaces == u'':
		obsETo = et.getRefET(url, getCapStr)
		da = (u"Dear %s we received getRefET request without date. \n नमस्कार %s आपला  getRefET मुद्दा रीकामा मिळाला. \n ---- \n Calculated daily grass / reference evaporation + transpiration \n (गवतावरील दैनिक बाष्पीभवन + पाणी वापर मोजणी).\n")%(f_name, f_name)
		if len(obsETo)>2:	
			for i in range(len(obsETo)):
				if i == 0:
					da = da + str(obsETo[i][0]) + ', '+str(obsETo[i][1])+', '+str(obsETo[i][2])+'\n--\n'
				else:
					da = da + str(obsETo[i][0]) + ': '+str(obsETo[i][1])+', '+str(obsETo[i][2])+'\n--\n'
			da = da + u"\n ---- \n To calculate for your requested date. (आपण सुचीत कॆलॆल्या दिनांकासाठी.) \n Send /getRefET 'dd-mm-YYYY' (पाठवा /getRefET 'दिवस-महीना-वर्ष').  \n----\n Send /help (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा)."
		else:
			da = da+ u"\n ---- \n Sorry, unable to calculate (माफ करा मोजणी करन्यास असमर्थ.) \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा)."
	elif spaces != u'':
		validDate=""
		try:
			validDate = re.split('-',spaces)
		except:
			pass
		if len(validDate)==3 and len(validDate[0])==2 and len(validDate[1])==2 and len(validDate[2])==4:
			da = (u"Dear %s we received getRefET request with date. \n नमस्कार %s आपला  getRefET मुद्दा दिनांकासहीत मिळाला. \n ---- \n Calculated daily grass / reference evaporation + transpiration \n (गवतावरील दैनिक बाष्पीभवन + पाणी वापर मोजणी).\n")%(f_name, f_name)
			myDate = str(spaces)
			#print(myDate)
			try:
				obsETo = et.getRefET(url, getCapStr, myDate)
				#print(obsETo)
			except:
				pass
			if len(obsETo)>2:	
				for i in range(len(obsETo)):
					if i == 0:
						da = da + str(obsETo[i][0]) + ', '+str(obsETo[i][1])+', '+str(obsETo[i][2])+'\n--\n'
					else:
						da = da + str(obsETo[i][0]) + ': '+str(obsETo[i][1])+', '+str(obsETo[i][2])+'\n--\n'
				da = da + u"\n ---- \n To calculate for your requested date. (आपण सुचीत कॆलॆल्या दिनांकासाठी.) \n Send /getRefET 'dd-mm-YYYY' (पाठवा /getRefET 'दिवस-महीना-वर्ष').  \n----\n Send /help (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा)."
			else:
				da = da+ u"\n ---- \n Sorry, unable to calculate (माफ करा मोजणी करन्यास असमर्थ.) \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा)."
		else:
			da = "Sorry, unable to calculate (माफ करा मोजणी करन्यास असमर्थ.) \n"		
			da = da + "\n ---- \n Right format /getRefET 'dd-mm-YYYY' (यॊग्य मुद्दा प्रकार /getRefET 'दिवस-महीना-वर्ष').\n----\n Send /help (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा)."
	else:
		da = (u"%s I don't understand what ' %s ' means. \n %s मला समजलॆ नाही, ' %s ' आपण काय सांगू इच्छित आहात? \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा).")%(f_name, spaces, f_name, spaces)
	bot.sendMessage(update.message.chat_id, text=da)
# Write utf-8 file content
def writeContent(fName, content):
	with open(fName,'a') as fout:
    		writer = csv.writer(fout)    
    		for row in zip(*content.values()):
			row=[s.encode('utf-8') for s in row]
			writer.writerows([row])
	fout.close()
#---------------------------------------------------------------------------------
# a
def echo(bot, update):
	#print(update.message)
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	# Form reply message
	da = (u"%s I don't understand what ' %s ' means. \n %s मला समजलॆ नाही, ' %s ' आपण काय सांगू इच्छित आहात? )  \n To return send (पाठीमागॆ जाण्यासाठी  /help मेसेज पाठवा).")%(f_name, update.message.text, f_name, update.message.text)
	bot.sendMessage(update.message.chat_id, text=da)
# b
def loc(bot, update):
	#print(update.message)
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	# another quick way to know the location id's
	lat = dat['location']['latitude']
	lon = dat['location']['longitude']
	# Form reply message
	da = (u"%s You are located at (आपण येथे आहात) \n Lat (अक्षांश): %s , Lon (रेखांश) = %s ")%(f_name, str(lat), str(lon))
	bot.sendMessage(update.message.chat_id, text=da)
# c
def pic(bot, update):
	#print(update.message)
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	# Form reply message
	da = ("%s Image is received from you.\n We will come back to you soon with results/forward image to expert.")%(f_name)
	bot.sendMessage(update.message.chat_id, text=da)
	'''
	# Help
	f_id = jj.to_dict()['message']['photo'][0]['file_id']#put photo identifier 0=small, 1=medium, 2=original
	newFile = bot.getFile(f_id)
	newFile.download('File_path\\file4.jpg')
	'''
#
def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))
#---------------------------------------------------------------------------------
# TODO: add function to process Reference Evapotranspiration ETo

#---------------------------------------------------------------------------------
#
def main():
	# Add your bot's token here
	updater = Updater("TOKEN")
	global url, fName, getCapStr
	url = 'http://localhost/istsos/service'
	# File to store user queries 
	fName = 'userQuery.csv'
	#TODO: 	Store user queries to database
	# Get capabilities string
	getCapStr = '?request=getCapabilities&section=contents&service=SOS'
	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help)) # 1
	dp.add_handler(CommandHandler("whoami", whoami)) # 2
	dp.add_handler(CommandHandler("morewhoami", morewhoami)) # 3
	
	dp.add_handler(CommandHandler("whichSensors", whichSensors)) #4

	dp.add_handler(CommandHandler("ISTSOSCap", ISTSOSCap)) # 5 not used here
	dp.add_handler(CommandHandler("getObs", getObs)) # 6 not used here
	# Get temperature sensor data # 7	
	dp.add_handler(CommandHandler("getTemp", getTemp))
	# Get humidity sensor data # 8
	dp.add_handler(CommandHandler("getHum", getHum))
	# Get rainfall sensor data # 9
	dp.add_handler(CommandHandler("getRain", getRain))
	# Sending user query # 10
	dp.add_handler(CommandHandler("query", query))
	# Sending user query # 11
	dp.add_handler(CommandHandler("getRefET", getRefET))

	# to do add getET, irriSchedule,
	
	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler([Filters.text], echo)) # a
	dp.add_handler(MessageHandler([Filters.location], loc)) # b
	dp.add_handler(MessageHandler([Filters.photo], pic)) # c

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()
#---------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
#
