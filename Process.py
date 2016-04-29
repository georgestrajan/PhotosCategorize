# This script iterates through all of the files in a folder and prints the EXIF DateTimeOriginal tag
import os
import time
import datetime
import sys
import exifread

src = "/home/george/Pictures/Test"
src = os.path.abspath(src)

# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

numberOfPictures = 0
numberOfMovies = 0

for root, subdirs, files in os.walk(src):
    path = root.split('/')
    for file in files:
        fullPath = os.path.join(root, file)
        
        if file.lower().find(".jpg") > 0:
            f = open(fullPath, 'rb')        
            tags = exifread.process_file(f)
            for tag in tags.keys():
                if tag in ('EXIF DateTimeOriginal'):
                    print "File: %s, Date %s" % (fullPath, tags[tag])
                    numberOfPictures = numberOfPictures + 1
        
        if file.lower().find(".mp4") > 0 or file.lower().find(".avi") > 0:
            print "File: %s, Date %s" % (fullPath, 
            datetime.datetime.strptime(time.ctime(os.path.getctime(fullPath)), "%a %b %d %H:%M:%S %Y"))
            numberOfMovies = numberOfMovies + 1
            
print "Number of pictures:", numberOfPictures
print "Number of movies:", numberOfMovies