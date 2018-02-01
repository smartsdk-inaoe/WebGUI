# -*- coding: utf-8 -*-

"""@package default
  Documentation of the default controller.

  This file contains the functions that will be called when the user access a specific page.

  @author Marlon Garcia

  Project: SmartSDK-Security

  Institution: INAOE
"""

@auth.requires_login()
def index():
	"""Default view
	
	This is the default view, but was replaced by main() to maintain a name-oriented convention.
	"""
	redirect(URL(f='main'))
	return dict()

@auth.requires(auth.has_membership(auth.id_group('Administrator')) or auth.has_membership(auth.id_group('Security')))
def main():
	"""Main view
	
	This view contains the feed of the first camera and a carousel with the stream of the rest of cameras.
	For security, it's required that a security gard or an administrator is logged in to view the page.
	"""
	return dict()

@auth.requires(auth.has_membership(auth.id_group('Administrator')) or auth.has_membership(auth.id_group('Security')))
def view():
	"""Video search view
	
	This view allows the search and view of stored videos related to detected events.
	For security, it's required that a security gard or an administrator is logged in to view the page.
	"""
	cameras={}
	cameras['0']=T('Any camera')
	for c in db(db.camera.id>0).select():
		cameras[c.id]=c.name
	form=SQLFORM.factory(Field('type',requires=IS_IN_SET({0:'Any type',1:'Person',2:'Vehicle'},zero=None)),
					Field('camera',requires=IS_IN_SET(cameras,zero=None)),
					Field('start','date'),
					Field('end','date'),
					table_name='filter')
	form2=SQLFORM.factory(Field('face','upload',uploadfolder=request.folder+'uploads'),
					table_name='search')
	form.element(_id='filter_start')['_placeholder']='Start date'
	form.element(_id='filter_end')['_placeholder']='End date'
	form2.element(_type='submit')['_class']='btn'
	files=''
	if form2.process().accepted:
		files=request.vars.face.filename
	return dict(form=form,form2=form2,files=files)

def getVideos():
	"""Get videos
	
	This function allows the retrieval of the stored videos within the parameters established in the request.
	"""
	files=[]
	import os
	import yaml
	with open('/path/to/config.yaml') as f:
		dataMap=yaml.safe_load(f)
	for f in os.listdir(dataMap['video path']):
		s=f.split('_')
		if len(s)>3:
			f_type=False
			if request.vars.type=='0' or request.vars.type==s[0]:
				f_type=True
			f_camera=False
			if request.vars.camera=='0' or request.vars.camera==s[1]:
				f_camera=True
			f_start=False
			if request.vars.start=='' or request.vars.start<=s[2]:
				f_start=True
			f_end=False
			if request.vars.end=='' or request.vars.end>=s[2]:
				f_end=True
			if f_type and f_camera and f_start and f_end:
				#files.append('*file')
				if s[0]=='0':
					fp='Movement'
				elif s[0]=='1':
					fp='Person'
				elif s[0]=='2':
					fp='Vehicle'
				fp=fp+' - '+db.camera[int(s[1])].name+' - '+s[2]+' - '+s[3].replace('-',':')
				files.append(str(XML(LI(A(fp,_onclick="stop();document.getElementById('videourl').value='"+f+"';document.getElementById('videotitle').innerHTML='"+fp+"'",_style="cursor:pointer;")))))
	return files

def searchFace():
	"""Get faces
	
	This function will retrieve the stored videos that contain a face detected in an uploaded image.
	"""
	return XML(P(request.vars))

@auth.requires(auth.has_membership(auth.id_group('Administrator')) or auth.has_membership(auth.id_group('Security')))
def multi():
	"""Multiple cameras/grid view
	
	This view contains a grid of the registered cameras and allows to view all of them at the same time.
	For security, it's required that a Security gard or an administrator is logged in to view the page.
	"""
	return dict()

@auth.requires_membership('Administrator')
def cameras():
	"""Camera management view
	
	This view allows the creation and edition of the cameras that will be used in the system.
	For security, it's required that an administrator is logged in to view the page.

	@param (optional)the first argument in the request will be considered the id of the camera, thus the form will contain the data stored for that camera to update it.

	When the page its accessed without arguments, it displays a form to add a camera to the system.
	"""
	form = SQLFORM.grid(db.camera,searchable=False,details=False,csv=False,onvalidation=validateCam,ondelete=deleteCam)
	if request.args(0):
		form[0][0][1][0] = 'Back'
		form['_class'] = 'col-sm-offset-3 col-sm-6'
	else:
		form[0][0][1][0] = 'Add Camera'
	return dict(form=form)
	if request.args(0):
		c=db.camera[request.args(0)]
		form = SQLFORM.factory(
			Field('name', requires=IS_NOT_EMPTY(), label='Camera name',default=c.name),
			Field('url', label='Connection URL', default=c.url),
			Field('c_zone', requires=IS_NOT_EMPTY(), label='Zone', default=c.c_zone))
		if form.process().accepted:
			db(db.camera.id==c.id).update(**db.camera._filter_fields(form.vars))
	else:
		form = SQLFORM.factory(
			Field('name', requires=IS_NOT_EMPTY(), label='Camera name'),
			Field('url', label='Connection URL'),
			Field('c_zone', requires=IS_NOT_EMPTY(), label='Zone'))
		if form.process().accepted:
			c_id = db.camera.insert(**db.camera._filter_fields(form.vars))
	return dict(form=form)

def validateCam(form):
	session.flash = 'In progress...'
	redirect(URL(f='cameras'))

def deleteCam(table, id):
	session.flash = 'Action not available...'
	redirect(URL(f='cameras'))

@auth.requires_membership('Administrator')
def filters():
	"""Filters view
	
	This view allows the edition of the visual markers that will be used by the object detectors (kurento filters).
	For security, it's required that an administrator is logged in to view the page.
	"""
	import xml.etree.ElementTree as ET
	methods = {'1':'Bounding Box','2':'Enclosing Circle','4':'Filling Object','3':'Text Tag'}
	formNames = ['CarDetection','PersonDetection','BlobDetection']#,'DogDetection']
	fileNames = ['OutdoorPeople','IndoorPeople','Visualizer']
	form = SQLFORM.factory(Field(formNames[0],type="boolean",label="Car Detection"),
						   Field(formNames[0]+"M",requires=IS_IN_SET(methods,zero=None)),
						   Field(formNames[0]+"C"),
						   Field(formNames[0]+"T"),
						   Field(formNames[1],type="boolean",label="Person Detection"),
						   Field(formNames[1]+"M",requires=IS_IN_SET(methods,zero=None)),
						   Field(formNames[1]+"C"),
						   Field(formNames[1]+"T"),
						   Field(formNames[2],type="boolean",label="Blob Detection"),
						   Field(formNames[2]+"M",requires=IS_IN_SET(methods,zero=None)),
						   Field(formNames[2]+"C"),
						   Field(formNames[2]+"T"))#,
						   #Field("DogDetection",type="boolean",label="Dog Detection"),
						   #Field("DogDetectionM",requires=IS_IN_SET(methods,zero=None)),
						   #Field("DogDetectionC"))
	tree = ET.parse('/home/viva22017/SmartSecurityApp/kurento/label_config.xml')
	root = tree.getroot()
	for fiN,foN in zip(fileNames,formNames):
		element = root.find(fiN+'Color')
		form.vars[foN+'C'] = "RGB("+element.text+")"
		element = root.find(fiN+'Method')
		form.vars[foN+'M'] = element.text
		element = root.find(fiN+'Text')
		form.vars[foN+'T'] = element.text
	for name in formNames:
		form.element("input",_name=str(name))["_onclick"]="showMe(this,'"+name+"')"
		form.vars[name] = True
		form.element("select",_name=str(name+'M'))["_onchange"]="enableMe(this,'#no_table_"+name+"T')"
		if form.vars[name+'M']!='3':
			form.element("input",_name=str(name+'T'))["_disabled"]=True
	if form.process().accepted:
		response.flash = 'MyForm accepted'
	if len(request.vars):
		return request.vars['PersonDetectionM']+request.vars['CarDetectionM']+request.vars['BlobDetectionM']
	if False:
		for fiN,foN in zip(fileNames,formNames):
			element = root.find(fiN+'Color')
			element.text = str(form.vars[foN+'C'][4:-1])
			element = root.find(fiN+'Method')
			element.text = str(form.vars[foN+'M'])
			if form.vars[foN+'M']=='3':
				element = root.find(fiN+'Text')
				element.text = str(form.vars[foN+'T'])
		tree.write('/home/viva22017/SmartSecurityApp/kurento/label_config.xml')
		response.flash = 'Filters updated successfully'
	return dict(form=form,names=formNames)

@auth.requires_membership('Administrator')
def users():
	"""Users view
	
	This view shows a list of the users that made a registration request to access the system, a list of the current users is also displayed.
	For security, it's required that an Administrator is logged in to view the page.
	"""
	#form = SQLFORM.grid(db.authUser,searchable=False,create=False,details=False,csv=False,onvalidation=validateUser,ondelete=deleteUser)
	if request.args(0):
		response.flash=request.args(0)
	db.authUser.id.readable=False
	form = SQLFORM.grid((db.authUser.registration_key=='pending'),links=[dict(header='Action',body=lambda row:  DIV(SELECT(OPTION('Administrator',_value='1'),OPTION('Security',_value='2'),OPTION('Mobile',_value='3'),_name='role'+str(row.id)),A('Accept',_onclick='ajax("'+URL('accept/'+str(row.id))+'",["role'+str(row.id)+'"],":eval")',_class='button btn btn-default'),_class='row_buttons'))],searchable=False,editable=False,deletable=False,create=False,details=False,csv=False)
	form2 = SQLFORM.grid(db.authUser.registration_key=='',searchable=False,create=False,details=False,csv=False,onvalidation=validateUser,ondelete=deleteUser)
	return dict(pendingUsers=form, registeredUsers=form2)
	
def accept():
	row = db.authUser[request.args(0)]
	from encription import crypt
	row.password=crypt('decrypt', row.password)

	import requests
	host = "207.249.127.96"
	port = 8001
	url = "http://{}:{}/v3/users".format(host,port)
	payload = '{"user": \
					{'+'\
						"username": "{first_name}",\
						"default_project_id": "idm_project",\
						"domain_id": "default",\
						"enabled": true,\
						"name": "{email}",\
						"password": "{password}"\
						'.format(**row)+'\
					}\
				}'
	#print 'payload:',payload
	headers = {
		'x-auth-token': "ADMIN",
		'content-type': "application/json"
		}

	r = requests.post(url, data=payload, headers=headers)

	#print r.status_code
	if r.status_code>=400:
		response.flash = 'Error: Duplicate Entry' if r.status_code==409 else r.json()['error']['title']
		return ""
	row.update_record(registration_key='')
	db.authMembership.insert(user_id=row.id,group_id=request.vars['role'+str(row.id)])
	response.flash = 'User added successfully'
	return "$('tr#{}').remove();".format(row.id)

def validateUser(form):
	session.flash = 'Action not available...'
	redirect(URL(f='users'))

def deleteUser(table, id):
	session.flash = 'Action not available...'
	redirect(URL(f='users'))

#@auth.requires_login()
def campusZonesMap():
	"""Map view
	
	This view will allow the search and localization of users in the map.
	"""
	form=SQLFORM.factory(Field('device'),
					Field('username'),
					Field('user'),
					table_name='filter')
	form.element(_id='filter_device')['_placeholder']='ID Device'
	form.element(_id='filter_username')['_placeholder']='Username'
	form.element(_id='filter_user')['_placeholder']='ID User'
	return dict(form=form)
	
@auth.requires_login()
def dashboard():
	"""Dashboard view
	
	This view allows to embed a graphana dashboard.
	"""
	return dict()

def user():
	"""User functionality

	Exposes:

	http://..../[app]/default/user/login

	http://..../[app]/default/user/logout

	http://..../[app]/default/user/register

	http://..../[app]/default/user/profile

	http://..../[app]/default/user/retrieve_password

	http://..../[app]/default/user/change_password

	http://..../[app]/default/user/bulk_register

	http://..../[app]/default/user/reset_password?key=xxxxx
	"""
	db.authUser.email.label='E-mail/Username'
	return dict(form=auth())

@cache.action()
def download():
	"""Download functionality

	Allows downloading of uploaded files.
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request, db)

def call():
	"""Services functionality

	Exposes services. for example:
	http://..../[app]/default/call/jsonrpc
	"""
	return service()
