import os
import sys
import exifread

src = "/home/george/Pictures/Test"
src = os.path.abspath(src)

# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

count = 0
for root, subdirs, files in os.walk(src):
    path = root.split('/')
    for file in files:
        fullPath = os.path.join(root, file)
        f = open(fullPath, 'rb')
        
        tags = exifread.process_file(f)
        for tag in tags.keys():
            if tag in ('EXIF DateTimeOriginal'):
                print "File: %s, Date %s" % (fullPath, tags[tag])
        
        count = count + 1

print "Number of files:", count