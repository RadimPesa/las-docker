from __init__ import *


def handle_uploaded_file(f):
    destination = open(path.join(TEMP_URL, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path.join(TEMP_URL, f.name)

# remove files if they are in tmp directory
def remove_uploaded_files(filelist):
    print filelist
    for f in filelist:
    	if os.path.split(f)[0] == os.path.split(TEMP_URL)[0]:
    		print 'Removing file: ' + str(os.path.split(f)[1])
        	os.remove(f)