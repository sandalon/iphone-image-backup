import paramiko
import photos
import dialogs
import os
import json
from objc_util import *

host = ''
port = 22
username = ''
password = ''

with open('settings.json') as in_file:
	login_creds = json.load(in_file)

if login_creds is not None:
	host = login_creds.get('host')
	username = login_creds.get('username')
	password = login_creds.get('password')

dialog_settings = ([{'key':'host', 'type':'text', 'value': host, 'title': 'Host'},
									{'key':'username', 'type':'text', 'value': username, 'title':'User name: '}, 
									{'key':'password', 'type':'password', 'value': password, 'title':'Password: '}])
	
login_creds = dialogs.form_dialog('SFTP Login', dialog_settings)

if login_creds is None:
	quit()

host = login_creds.get('host')
username = login_creds.get('username')
password = login_creds.get('password')

if not username or not password:
	quit()

# save the credentials for later
with open('settings.json', 'w') as out_file:
	json.dump(login_creds, out_file)

transport = paramiko.Transport((host, port))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

images = photos.pick_asset(title='Content to backup', multi=True)
if images is not None:
	for img in images:
		fileName = str(ObjCInstance(img).valueForKey_('filename'))
		print ('copying ' + fileName)	
		b = img.get_image_data().getvalue()
		with open(fileName, mode='wb') as fil:
			fil.write(b)
			sftp.put(fileName, '/Personal/Photos/' + fileName)
			os.remove(fileName) 
			print ('done')	
	sftp.close()
	transport.close()
	print ('transfer complete')

