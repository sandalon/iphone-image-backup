import paramiko
import photos
import os
from objc_util import *

host = 'nas.local.agilereaction.io'
port = 22
transport = paramiko.Transport((host, port))

username = 'photobackup'
password = 'photobackup'
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

images = photos.pick_asset(title='Content to backup', multi=True)
for img in images:
	fileName = str(ObjCInstance(img).valueForKey_('filename'))
	print (fileName)	
	b = img.get_image_data().getvalue()
	with open(fileName, mode='wb') as fil:
		fil.write(b)
		sftp.put(fileName, '/Personal/Photos/' + fileName)
		os.remove(fileName) 	
		
sftp.close()
transport.close()

