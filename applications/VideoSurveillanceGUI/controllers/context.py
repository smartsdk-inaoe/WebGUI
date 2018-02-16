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
	host = "130.206.113.226"
	port = 1026
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	data = {
		"id": "DummyAlert16",
		"type": "Alert",
		"alertSource": {
			"type": "Text",
			"value": "Dummy Device 1"
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
			"value": "dummy text"
		},
		"location": {
			"type": "Text",
			"value": "19.03, -98.32"
		},
		"severity": {
			"type": "Text",
			"value": "low"
		}
	}

	r = requests.post("http://{}:{}/v2/entities".format(host,port), headers=headers, data=json.dumps(data))
	return dict(result=str(r.status_code)+' '+r.text+' '+str(r.headers))
	#return dict(result=data)

def contextSubscription():
	"""Subscription
	
	Auxiliary function that creates or updates a subscription of an entity in the context broker.
	"""
	import requests
	import json
	from datetime import datetime
	host = "130.206.113.226"
	port = 1026
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
	#r = requests.patch("http://{}:{}/v2/subscriptions/59fe91ed002da071f2957259".format(host,port), headers=headers, data=json.dumps(data))
	r = requests.post("http://{}:{}/v2/subscriptions".format(host,port), headers=headers, data=json.dumps(data))
	#r = requests.delete("http://{}:{}/v2/subscriptions/5a84d5da3fc4dec59e4ef8e7".format(host,port))
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
	db.alerts.truncate()
	return dict()

def getNotifications():
	"""Get notifications
	
	This functions retrieves the alerts in the database which id is bigger than the first argument in the request.
	"""
	lastId = 0
	if request.args(0):
		lastId = request.args(0)
	events = ''
	for row in db(db.alert.idAlert>lastId).select():
		events += ';'+row.description+','+row.alertSource+','+row.address+','+row.dateObserved.isoformat()
		lastId = row.idAlert
	events = str(lastId) + events
	return events
