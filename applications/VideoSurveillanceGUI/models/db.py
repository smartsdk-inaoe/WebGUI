# -*- coding: utf-8 -*-

"""@package db
  Documentation for the data model

  This file contains the connection to the database and the definition of its tables.
  Also, it allows to configure the user authentication and email settings
  
  @author Marlon Garcia (Adapted from Web2Py)

  Project: SmartSDK-Security

  Institution: INAOE
"""

## HTTPS redirection
#
#  If SSL/HTTPS is properly configured and you want all HTTP requests to
#  be redirected to HTTPS, uncomment the line below:
request.requires_https()

## App configuration
#
#  Definition of configuration variables in the file private/appconfig.ini
#
#  once in production, remove reload=True to gain full speed
from gluon.contrib.appconfig import AppConfig
myconf = AppConfig(reload=True)

## Database connection
#
# if NOT running on Google App Engine use SQLite or other DB
if not request.env.web2py_runtime_gae:
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=[])#,fake_migrate=True)
else:
    # connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    # store sessions and tickets there
    session.connect(request, response, db=db)
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))

## Generic patterns
#
#  By default give a view/generic.extension to all actions from localhost
#  none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## Form style
#
#  Choose a style for forms
# 'bootstrap3_stacked' or 'bootstrap2' or other
response.formstyle = myconf.take('forms.formstyle')  
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'

from gluon.tools import Auth, Service, PluginManager

## Initial configuration for
#
#  authentication (registration, login, logout, ... )
#
#  authorization (role based authorization)

auth = Auth(db)
auth.settings.table_cas_name = 'authCas'
auth.settings.table_group_name = 'authGroup'
auth.settings.table_membership_name = 'authMembership'
auth.settings.table_permission_name = 'authPermission'
auth.settings.table_event_name = 'authEvent'
auth.settings.table_user_name = 'authUser'

## Initial configuration for
#
#  services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
service = Service()
plugins = PluginManager()

## Authentication tables
#
#  Create all tables needed by auth if not custom tables

auth.settings.extra_fields['authUser']= [
        Field('refAffiliation','integer', writable=False, readable=False),
        Field('refZone','integer'),
        Field('refSubZone','integer'),
        Field('aliasUser','string'),
        Field('address','string'),
        Field('phoneNumber','list:string'),
        Field('dateCreated','datetime', writable=False, default=request.now),
        Field('dateModified','datetime', writable=False, default=request.now),
        Field('refUserContact','list:string', writable=False, readable=False),
        Field('refDevices','list:string', writable=False, readable=False),
        Field('refVehicles','list:string', writable=False, readable=False),
        Field('checkInTime','time'),
        Field('departureTime','time'),
        Field('status','boolean', writable=False, readable=False)]

auth.define_tables(username=False, signature=False)

## Email configuration
#
#  Write to the log when the request is from localhost
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## Auth policy
#
#  Disable registration of new users
#auth.settings.actions_disabled.append('register')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True

## Email verification
#
#  Verify by email if the user is trying to reset his/her password
auth.settings.reset_password_requires_verification = True

## Catalogues

## Table definition
db.define_table('camera',
        Field('name','string',label='Camera name'),
        Field('url','string',label='Connection URL'),
        Field('c_zone','string',label='Zone'))

db.define_table('alerts',
        Field('eventAddress','string'),
        Field('refDevice','string'),
        Field('eventLocation','string'),
        Field('eventObserved','string'),
        Field('eventDateTime','string'))

db.define_table('alert',
	Field('idAlert','id'),
	Field('type','string'),
	Field('category','string'),
	Field('subCategory','string'),
	Field('location','string'),
	Field('address','string'),
	Field('dateObserved','datetime'),
	Field('validFrom','datetime'),
	Field('validTo','datetime'),
	Field('description','string'),
	Field('alertSource','string'),
	Field('data','string'),
	Field('severity','string'))
## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

# User registration
def encryptPassword(form):
	from encryption import crypt
	form.vars.password = crypt('encrypt', request.vars.password)

auth.settings.register_onvalidation = encryptPassword

from gluon.contrib.login_methods.basic_auth import basic_auth
auth.settings.login_methods = [basic_auth(myconf.take('auth.uri')+'/basicauth')]
