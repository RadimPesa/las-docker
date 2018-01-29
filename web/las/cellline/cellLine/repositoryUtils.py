from __init__ import *


def handle_uploaded_file(f, folderDest):
    destination = open(path.join(folderDest, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path.join(folderDest, f.name)

