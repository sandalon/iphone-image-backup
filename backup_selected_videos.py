import paramiko
import photos
import dialogs
import os
import json
from objc_util import *

# sftp client config
host = ''
port = 22
username = ''
password = ''

if os.path.isfile('settings.json'):
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

# video handling setup
# https://gist.github.com/jsbain/de01d929d3477a4c8e7ae9517d5b3d70

options=ObjCClass('PHVideoRequestOptions').new()
options.version=1	#PHVideoRequestOptionsVersionOriginal, use 0 for edited versions.
image_manager=ObjCClass('PHImageManager').defaultManager()

handled_assets=[]

def handleAsset(_obj,asset, audioMix, info):
	A=ObjCInstance(asset)
	'''I am just appending to handled_assets to process later'''
	handled_assets.append(A)
	'''
	# alternatively, handle inside handleAsset.  maybe need a threading.Lock here to ensure you are not sending storbinaries in parallel
	with open(str(A.resolvedURL().resourceSpecifier()),'rb') as fp:
		fro.storbinary(......)
	'''
handlerblock=ObjCBlock(handleAsset, argtypes=[c_void_p,]*4)
	
# do the actual work
	
transport = paramiko.Transport((host, port))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

images = photos.pick_asset(title='Content to backup', multi=True)
for A in assets:
	#these are PHAssets
	image_manager.requestAVAssetForVideo(A, 
						options=options, 
						resultHandler=handlerblock)
while len(handled_assets) < len(images):
	'''wait for the asynchronous process to complete'''
	time.sleep(1)

for A in handled_assets:
	with open(str(A.resolvedURL().resourceSpecifier()),'rb') as fp:
		filename=str(A.URL()).split('/')[-1]
		print ('copying ' + filename)	
		sftp.putfo(remotepath='/Personal/Photos/' + filename, fl=fp)
		print ('done')

sftp.close()
transport.close()
print ('transfer complete')

