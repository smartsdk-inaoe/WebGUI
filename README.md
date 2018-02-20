# WebGUI
Web GUI of the Smart Security application.

# Requirements
* Install Python 2.7
* Edit the file ./applications/VideoSurveillanceGUI/private/appconfig.ini.example to set the IP addresses of the database, auth and context broker servers, and save the file as appconfig.ini
* Open a console/terminal inside the root folder of the repository and run the server using the command: python web2py.py -c server.crt -k server.key -a 'admin-pwd' -i 0.0.0.0
