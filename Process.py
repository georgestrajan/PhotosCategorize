# This script iterates through all of the files in a folder and prints the EXIF DateTimeOriginal tag
import os
import time
import datetime
import sys
import exifread
import csv

src = "/home/george/Pictures/Test"
src = os.path.abspath(src)

class TripRecord:
    def __init__(self, valueString):
        if valueString:
            self.Country = valueString[4]
            self.Place = valueString[3]
            self.Year = valueString[2]
            self.Month = valueString[1]
            self.Day = valueString[0]

    def __str__(self):
        return "Day:" + self.Day + " Month:" + self.Month + " Year:" + self.Year + " Place:" + self.Place + " Country:" + self.Country

def readLocationsFile(locationsCSV):
    with open(locationsCSV, mode='r') as f:
        reader = csv.reader(f)
        stringList = list(reader)
    
    del stringList[0]
    returnList = []
    for item in stringList:
        record = TripRecord(item)
        print record
        returnList.append(record)
        
    return returnList
    
# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

numberOfPictures = 0
numberOfMovies = 0
picProcessed = False

for root, subdirs, files in os.walk(src):
    path = root.split('/')
    for file in files:
        fullPath = os.path.join(root, file)
               
        if file.lower().find(".jpg") > 0 and picProcessed == False:
            f = open(fullPath, 'rb')        
            tags = exifread.process_file(f)
            picProcessed = True
            for tag in tags.keys():
                if tag in ('EXIF DateTimeOriginal'):
                    # format: 2015:10:08 00:31:47
                    print "File: %s, Date %s" % (fullPath, 
                    time.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S"))
                    numberOfPictures = numberOfPictures + 1
        
        if file.lower().find(".mp4") > 0 or file.lower().find(".avi") > 0:
            print "File: %s, Date %s" % (fullPath, 
            time.gmtime(os.path.getctime(fullPath)))
            numberOfMovies = numberOfMovies + 1
            
print "Number of pictures:", numberOfPictures
print "Number of movies:", numberOfMovies

readLocationsFile('/home/george/Documents/Programming/PhotosCategorize/TripDates.csv')

