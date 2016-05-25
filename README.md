# Python-SOS-Client
Python Sensor Observation Service (SOS) Cilent

- Python based parsers for parsing SOS response.
- Aimed for standalone operation mainly for SOS based Telegram Bot/s.
- Integrates SOS parsers using [Telegram-Bot-Scripts] to [python-telegram-bot]. More information about [Telegram Bot Platform].


### Version
Alpha 1.0.0

### Depends on

Only tested in Ubuntu 14.04 with python 2.7

- xmltodict
- requests
- dateutil.parser
- colorama 
- pandas

### Other References

- [OGC] Open Geospatial Consortium
- OGC [SOS] Specifications
- Python based SOS [ISTSOS]
- National Data Buoy Center SOS [NDBC]
- Get Capability request for [ISTSOS-Demo] SOS
- Get Capability request for [NDBC-SOS] SOS

### Contains

1. Folder: src
	- sosParseCap.py (SOS GetCapability parser)
	- sosReq.py (SOS Get Observation requests and response parser example)
	- sosTsPandas.py (SOS time series analysis using Pandas )
	- sosParseDSensor.py (SOS Describe sensor parser)
	- sosParseGetObs.py (SOS Get Observation parser)
	- sosTelegramBot.py (SOS integration with Telegram Bot, example1: English)
	- sosTelegramBotMarathi.py (SOS integration with Telegram Bot, example2: English and Marathi)
	- overallFlow.py (overall flow of all processes)

### Advantages

	1. Python based SOS client to support Telegram Bot/s.

### Limitations

	1. Some sections are hardcoaded in SOS response parsers.
	
### Installation

A. Download

- Clone from GitHub

```sh
$ git clone https://github.com/suryakant54321/Python-SOS-Client 
```

- Install dependencies 

```sh
$ cd Python-SOS-Client
$ pip install -r requirements.txt 
```

B. Usage of Python-SOS-Client

	Add to environment path
	or
	Just import the required workflow

```sh
$ python
>>> import sosParseCap as spc
>>> help(spc)
>>> import sosReq as sr
>>> help(sr) 
>>> import sosTsPandas stp
>>> help(stp)
```

C. Other SOS Clients

- Refer [PHP-istSOS-client] PHP based client for IST Sensor Observation Service (SOS)
- Refer [sos4R] sos4R is an extension for the R environment for statistical computing and visualization. Designed by [52°North].
- Refer [sos-js] a JavaScript library to browse, visualise, and access, data from an Open Geospatial Consortium (OGC) Sensor Observation Service (SOS). Designed by [52°North].


#### To Do
	
1. Combine overall flow of all processes (i.e. SOS parsing and Telegram user interactions)

2. Test all modules

3. Write detailed documentation using [Sphinix] 


[ISTSOS]: <http://istsos.org/>
[ISTSOS-Demo]: <http://istsos.org/istsos/demo?request=getCapabilities&section=contents&service=SOS>
[NDBC]: <http://sdf.ndbc.noaa.gov/sos/>
[NDBC-SOS]: <http://sdf.ndbc.noaa.gov/sos/server.php?request=GetCapabilities&service=SOS>
[OGC]: <http://www.opengeospatial.org/>
[SOS]: <http://www.opengeospatial.org/standards/sos>
[PHP-istSOS-client]: <https://github.com/suryakant54321/php_istSOS_client>
[sos4R]: <https://github.com/52North/sos4R>
[sos-js]: <https://github.com/52North/sos-js>
[52°North]: <http://52north.org/>
[Sphinix]: <http://www.sphinx-doc.org/en/stable/>
[Telegram Bot Platform]: <https://telegram.org/blog/bot-revolution>
[Telegram-Bot-Scripts]: <https://github.com/suryakant54321/Telegram-Bot-Scripts>
[python-telegram-bot]: <https://github.com/python-telegram-bot/python-telegram-bot>
