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
	host = "192.168.56.101"
	port = 1026
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	data = {
			"contextElements":[
				{
					"type": "Alert",
					"isPattern": "false",
					"id": "RecordingState2",
					"attributes": [
						{
							"name":"dateTime",
							"type": "string",
							"value": datetime.now().isoformat('T')[:-7]#"2017-01-01T00:00:00.00Z"
						},
						{
							"name": "refDevice",
							"type": "string",
							"value": "2"
						},
						{
							"name": "eventObserved",
							"type": "string",
							"value": request.args(0)
						}
					]
				}
			],
			"updateAction": "UPDATE"
	}
	r = requests.post("http://{}:{}/v1/updateContext".format(host,port), headers=headers, data=json.dumps(data))
	return dict(result=r.json())
	#return dict(result=data)

def contextSubscription():
	"""Subscription
	
	Auxiliary function that creates or updates a subscription of an entity in the context broker.
	"""
	import requests
	import json
	from datetime import datetime
	host = "192.168.56.101"
	port = 1026
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	data = {
			"description":"Smartphone Alert",
			"subject":{
				"entities":[
					{
						"id": "SmartphoneAlert1",
						"type": "Alert"
					}
				],
				"condition": {
					"attrs":[
					   "dateTime"
					]
				}
			},
			"notification": {
				"http":{
					"url": "https://"+request.env.http_host+"/context/subscriptionUpdate"
				}
			},
			"expires":"2040-01-01T14:00:00.00Z",	
			"throttling": 10
	}
	r = requests.patch("http://{}:{}/v2/subscriptions/59fe91ed002da071f2957259".format(host,port), headers=headers, data=json.dumps(data))
	#r = requests.post("http://{}:{}/v2/subscriptions".format(host,port), headers=headers, data=json.dumps(data))
	#r = requests.delete("http://{}:{}/v2/subscriptions/59fa80a6002da071f2957257".format(host,port))
	return dict(result=r)#id=59d6c99b159e1c0fac94dce9
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
	db.alerts.insert(eventObserved=data['eventObserved']+' - '+data['description'],eventDateTime=data['dateTime'],refDevice=data['refDevice'],eventAddress=data['address']['streetAddress'])
	db.commit()

def checkAlerts():
	"""Check alerts
	
	Auxiliary function to retrieve all the alerts stored in the database showing them in a grid.
	"""
	form = SQLFORM.grid(db.alerts)
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
	for row in db(db.alerts.id>lastId).select():
		events += ';'+row.eventObserved+','+row.refDevice+','+row.eventAddress+','+row.eventDateTime
		lastId = row.id
	events = str(lastId) + events
	return events
