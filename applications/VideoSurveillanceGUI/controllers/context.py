# -*- coding: utf-8 -*-

"""@package context
  Documentation of the context broker connection controller.

  This file contains the functions that will connect to the orion context broker for creating, updating and receiving entities and subscriptions.

  @author Marlon Garcia

  Project: SmartSDK-Security

  Institution: INAOE
"""

#@auth.requires_login() # Uncomment to enable auth restrictions
def createEntity():
	"""Create entity
	
	Auxiliary function that creates or updates an entity in the context broker.
	"""
	import requests
	import json
	from datetime import datetime
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	# Subtitute of DB info
	latlng = {'1':'19.03353, -98.31621','2':'19.03139, -98.31694','3':'19.03171, -98.31600','4':'19.03077, -98.31637','5':'19.03366, -98.3161'}
	names = {'1':'Hallway','2':'Parking Entrance','3':'Main Entrance','4':'Parking Lot','5':'Hallway 3'}
	# Alert model
	data = {
		#"id": "Camera-"+request.vars['cam'],
		#"type": "Alert",
		"alertSource": {
			"type": "Text",
			"value": "Camera{}: {}".format(request.vars['cam'],names[request.vars['cam']])
		},
		"category": {
			"type": "Text",
			"value": "MyCategory"
		},
		"subCategory": {
			"type": "Text",
			"value": "MySubCategory"
		},
		"dateObserved": {
			"type": "DateTime",
			"value": datetime.now().isoformat('T')[:-7]#"2017-01-01T00:00:00.00Z"
		},
		"validFrom": {
			"type": "DateTime",
			"value": datetime.now().isoformat('T')[:-7]
		},
		"validTo": {
			"type": "DateTime",
			"value": datetime.now().isoformat('T')[:-7]
		},
		"description": {
			"type": "Text",
			"value": "Test alert from WebGUI"
		},
		"location": {
			"type": "geo:point",
			"value": latlng[request.vars['cam']]
		},
		"severity": {
			"type": "Text",
			"value": request. vars['level']
		}
	}
	# Use post to create a new entity and patch to update an existing one
	#r = requests.post("{}/v2/entities/".format(myconf.take('cb.uri')), headers=headers, data=json.dumps(data))
	r = requests.patch("{}/v2/entities/Camera-{}/attrs".format(myconf.take('cb.uri'),request.vars['cam']), headers=headers, data=json.dumps(data))
	#print r.status_code,r.text,r.headers
	return 0

def contextSubscription():
	"""Subscription
	
	Auxiliary function that creates or updates a subscription of an entity in the context broker.
	"""
	import requests
	import json
	from datetime import datetime
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	data = {
		"description":"Web2py Alert",
		"subject":{
			"entities":[
				{
					"idPattern": ".*",
					"type": "Alert"
				}
			],
			"condition": {
				"attrs":[
					"dateObserved"
				]
			}
		},
		"notification": {
			"http":{
				"url": "https://"+request.env.http_host+"/context/subscriptionUpdate"
			}
		},
		#"expires":"2040-01-01T14:00:00.00Z",	
		"throttling": 5
	}
	r = requests.post("{}/v2/subscriptions".format(myconf.take('cb.uri')), headers=headers, data=json.dumps(data))
	#r = requests.patch("{}/v2/subscriptions/59fe91ed002da071f2957259".format(myconf.take('cb.uri')), headers=headers, data=json.dumps(data))
	#r = requests.delete("{}/v2/subscriptions/5a84d5da3fc4dec59e4ef8e7".format(myconf.take('cb.uri')))
	return dict(result=str(r.status_code)+' '+r.text+' '+str(r.headers))#id=5a848f203fc4dec59e4ef8e5
	#return dict(result=data)

def subscriptionUpdate():
	"""Subscription update
	
	This function receives the new information stored in the context broker, i.e. entity updates, and stores this information in the system database (alerts).
	"""
	import json
	data = {}
	for attr in request.post_vars.data[0]:
		if 'value' in request.post_vars.data[0][attr]:
			data[attr]=request.post_vars.data[0][attr]['value']
		#elif attr == 'id':
		#	data['idAlert']=request.post_vars.data[0][attr]
	db.alert.insert(**data)
	
def checkAlerts():
	"""Check alerts
	
	Auxiliary function to retrieve all the alerts stored in the database showing them in a grid.
	"""
	form = SQLFORM.grid(db.alert)
	return dict(form=form)

def resetAlerts():
	"""Reset alerts
	
	Auxiliary function to delete all the alerts in the database to restore the system to an initial test state.
	"""
	db.alert.truncate()
	return dict()

def getNotifications():
	"""Get notifications
	
	This functions retrieves the alerts in the database which dateObserved value is bigger than the first argument in the request.
	"""
	import datetime;
	lastDatetime = 0
	if request.args(0):
		#print request.args(0)
		lastDatetime = datetime.datetime.strptime(request.args(0),'%Y-%m-%d-%H-%M-%S')
	events = ''
	for row in db(db.alert.dateObserved>lastDatetime).select():
		events += ';'+row.description+','+row.alertSource+','+row.severity+','+row.dateObserved.isoformat()
		lastDatetime = row.dateObserved
	events = lastDatetime.strftime('%Y-%m-%d-%H-%M-%S') + events
	return events

def getNotifications2():
	"""Get notifications
	
	This functions retrieves the alerts in the database in a 15 minutes range for an specific set of coordinates.
	"""
	from datetime import datetime, timedelta
	cam = 0
	events = ''
	latlng = {'1':'19.03353, -98.31621','2':'19.03139, -98.31694','3':'19.03171, -98.31600','4':'19.03077, -98.31637','5':'19.03366, -98.3161'}
	if request.args(0):
		for row in db((db.alert.location==latlng[request.args(0)])&(db.alert.dateObserved>(datetime.now()-timedelta(minutes=15)))).select():
			events += ';'+row.description+','+row.severity+','+row.address+','+row.dateObserved.isoformat()
	events = str(cam) + events
	return events
