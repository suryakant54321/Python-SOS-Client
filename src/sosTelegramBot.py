#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-----------------------------------------------------------------------
# Source Details: https://github.com/python-telegram-bot/python-telegram-bot/examples
#
# Modified by: Suryakant Sawant
# Date: 13 Jan. 2017
#
# Objective: Basic example to connect Sensor Observation Service (SOS) to Telegram Messaging Bot
#
# 1. This Bot uses the Updater class to handle the bot.
# 2. Modified Echobot example (https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py).
# 3. Press Ctrl-C on the command line or send a signal to the process to stop the bot.
# 4. User commands are processed for obtaining sensor capabilities, Observations and Measurements.
# 5. More functions are added in sosTelegramBotIWC.py
#-----------------------------------------------------------------------
"""
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
#-----------------------------------------------------------------------
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
# Command handlers
def start(bot, update):
	welcomeMsg = 'Welcome ... \n Enter /help for more information.'
	bot.sendMessage(update.message.chat_id, text=welcomeMsg)
#
def help(bot, update):
	helpMsg = 'For more information enter following commands \n /whoami \n /getSOSUrls \n /ISTSOSCap \n /picSend '
	bot.sendMessage(update.message.chat_id, text=helpMsg)
#
def whoami(bot, update):
	bot.sendMessage(update.message.chat_id, text='I am Telegram based Sensor Observation Service Bot. \n \n Enter /help for more information.')
#
def getSOSUrls(bot, update):
	bot.sendMessage(update.message.chat_id, text="I have following URL's \n 1. ISTSOS [http://istsos.org/istsos/demo] \n 2. NDBC [http://sdf.ndbc.noaa.gov/sos/server.php] \n")
#
def ISTSOSCap(bot, update):
	import sosParseCap as pc
	out = pc.parseSOScap(pc.url)
	out = str(out[0])
	out = out+"\n to get sample observations send /getObs request"
	bot.sendMessage(update.message.chat_id, text=out)
#
def getObs(bot, update):
	import sosParseGetObs as go
	aa, bb = go.parseSOSgetObs(go.istsosGO, go.ISTSOSrparams, responseFormat='plain')
	out = "Observation details: \n"+str(aa)+" \n Observations: \n "
	import sosTsPandas as st
	result = st.tsOperation(aa, bb, operation='mean', sampleTime='24H')
	out = out+ str(result)
	out = out+"\n "
	bot.sendMessage(update.message.chat_id, text=out)
#
def picSend(bot, update):
	#print(update.message)
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	# Form reply message
	da = ("%s image is received from you.\n We will come back to you soon with results/forward image to expert.")%(f_name)
	#bot.sendMessage(update.message.chat_id, text=da)
	bot.sendPhoto(update.message.chat_id, photo=open('<path to image file>/sample.jpg', 'rb'))
#
def echo(bot, update):
	print(update.message.text)
	# to capture user input without command
	da = ("I don't understand what ' %s ' means :) \n enter /help for more info.")%(update.message.text)
	bot.sendMessage(update.message.chat_id, text=da)
#
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
	da = ("%s you are located at \n Lat: %s , Lon = %s ")%(f_name, str(lat), str(lon))
	bot.sendMessage(update.message.chat_id, text=da)
#
def pic(bot, update):
	#print(update.message)
	dat = update.message
	dat = dat.to_dict()
	print(dat)
	f_name = dat['from']['first_name']
	# Form reply message
	da = ("%s image is received from you.\n We will come back to you soon with results/forward image to expert.")%(f_name)
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
#
def main():
	# Add your bot's token here # KrishiSense: TOKEN
	updater = Updater("TOKEN") # SenseTube: 

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("whoami", whoami))
	dp.add_handler(CommandHandler("getSOSUrls", getSOSUrls))
	dp.add_handler(CommandHandler("ISTSOSCap", ISTSOSCap))
	dp.add_handler(CommandHandler("picSend", picSend))
	dp.add_handler(CommandHandler("getObs", getObs))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler([Filters.text], echo))
	dp.add_handler(MessageHandler([Filters.location], loc))
	dp.add_handler(MessageHandler([Filters.photo], pic))
	
	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()
#
if __name__ == '__main__':
	main()
#
