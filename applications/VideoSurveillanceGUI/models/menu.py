# -*- coding: utf-8 -*-

"""@package menu
  Documentation of App and menu configuration

  This file contains the definition of logo, title, subtitle of the app as well as the elements of the main menu.
  
  @author Marlon Garcia (Adapted from Web2Py)

  Project: SmartSDK-Security

  Institution: INAOE
"""

## App customization
#
#  HTML code of the logo
response.logo = A('Video Surveillance',
                  _class="navbar-brand",_href="#",
                  _id="web2py-logo")

## App title
#
#  Folder name by default
response.title = 'Smart Video Surveillance'

## App subtitle
#
#  Empty by default
response.subtitle = ''

## Meta definitions
#
#  Read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
## Meta definitions
#
#  Read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.description = 'video surveillance app'
## Meta definitions
#
#  Read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.keywords = 'inaoe, web2py, python, framework'
## Meta definitions
#
#  Read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.generator = 'Web2py Web Framework'

T.force('en')

## Google analytics
#
#  Your http://google.com/analytics id
response.google_analytics_id = None

## App Menu
#
#  This is the main application menu add/remove items as required
response.menu = [
	(T('Main'), False, URL('default', 'main'), []),
	(T('Mutiple cameras'), False, '#', [
			(T('Grid'), False, URL('default', 'multi'), []),
			(T('Map'), False, URL('default', 'onlineMap'), [])
		]),
	(T('Search'), False, '#', [
			(T('Videos'), False, URL('default', 'view'), []),
			(T('On map'), False, URL('default', 'campusZonesMap'), [])
		]),
	(T('Management'), False, '#', [
			(T('Cameras'), False, URL('default', 'cameras'), []),
			(T('Markers'), False, URL('default', 'filters'), []),
			(T('Users'), False, URL('default', 'users'), [])
		])
]

if "auth" in locals(): auth.wikimenu()
