"""
#-----------------------------------------------------------------------
# Source Details: https://github.com/python-telegram-bot/python-telegram-bot/examples
#
# Modified by: Suryakant Sawant
# Date: 23 May 2016
#
# Objective: Basic example to connect Sensor Observation Service (SOS) to Telegram Messaging Bot
#
# 1. This Bot uses the Updater class to handle the bot.
# 2. Modified Echobot example (https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py).
# 3. Press Ctrl-C on the command line or send a signal to the process to stop the bot.
# 4. User commands are processed for obtaining sensor capabilities, Observations and Measurements.
#
# To Do:
# 1. Add more intearctive user commands 
#	a. Sensor system list
#	b. Sensor selection (temperature, humidity, etc.)
#	c. Sensor observation listing
#	d. Summary statistics of time series observation  
# 2. Process output response using markup tags (HTML, etc.) 
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
	helpMsg = 'For more information enter following commands \n /whoami \n /getSOSUrls \n /ISTSOSCap '
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
def echo(bot, update):
	print(update.message.text)
	# to capture user input without command
	da = ("I don't understand what ' %s ' means :) \n enter /help for more info.")%(update.message.text)
	bot.sendMessage(update.message.chat_id, text=da)
#
def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))
#
def main():
	# Add your bot's token here
	updater = Updater("TOKEN")

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("whoami", whoami))
	dp.add_handler(CommandHandler("getSOSUrls", getSOSUrls))
	dp.add_handler(CommandHandler("ISTSOSCap", ISTSOSCap))
	dp.add_handler(CommandHandler("getObs", getObs))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler([Filters.text], echo))
	
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