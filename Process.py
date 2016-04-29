# This script iterates through all of the files in a folder and prints the EXIF DateTimeOriginal tag
import os
import time
import datetime
import sys
import exifread
import csv

src = "/home/george/Pictures/Test"
src = os.path.abspath(src)

#
#   Class that holds a record of the arrival date at a certain place
#   Has the following attributes: Day,Month,Year,Place,Countrys
#
class TripRecord:
    def __init__(self, valueString):
        if valueString:
            self.ValueString = valueString
            self.Country = valueString[4]
            self.Place = valueString[3]
            self.Year = valueString[2]
            self.Month = valueString[1]
            self.Day = valueString[0]
        else:
            self.ValueString = None
            
    def __str__(self):
        if self.ValueString:        
            return "Day:" + self.Day + " Month:" + self.Month + " Year:" + self.Year + " Place:" + self.Place + " Country:" + self.Country
        else:
            return "Empty"
            
    def __repr__(self):
        return str(self)
        
    # reads a CSV file and returns a list of objects of type TripRecord
    @staticmethod
    def readLocationsFile(locationsCSV):
        with open(locationsCSV, mode='r') as f:
            reader = csv.reader(f)
            stringList = list(reader)
        
        del stringList[0]
        returnList = []
        for item in stringList:
            record = TripRecord(item)
            returnList.append(record)
            
        return returnList


#
#   Class which holds information about a media file to be processsed
#
class MediaFile:
    def __init__(self, fullPath, mediaType, createdDateTime):
        if fullPath:
            self.FullPath = fullPath
            self.MediaType = mediaType
            self.CreatedDateTime = createdDateTime
            self.TripRecord = TripRecord("")
            
    def __str__(self):
        return "Path:" + self.FullPath + " MediaType:" + self.MediaType + " DateTime:" + time.strftime("%d %b %Y %H:%M:%S", self.CreatedDateTime) + " Trip Record:" + str(self.TripRecord)

    def __repr__(self):
        return str(self)

# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

numberOfPictures = 0
numberOfMovies = 0
picProcessed = False
filesToProcess = []

# create a list of filesToProcess by recursively walking from the src folder and finding pictures and videos
for root, subdirs, files in os.walk(src):
    for file in files:
        fullPath = os.path.join(root, file)
               
        if file.lower().find(".jpg") > 0 and picProcessed == False:
            f = open(fullPath, 'rb')        
            tags = exifread.process_file(f)
            picProcessed = True
            for tag in tags.keys():
                if tag in ('EXIF DateTimeOriginal'):
                    # format: 2015:10:08 00:31:47
                    filesToProcess.append(MediaFile(fullPath, "picture", time.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S")))
                    numberOfPictures = numberOfPictures + 1
        
        if file.lower().find(".mp4") > 0 or file.lower().find(".avi") > 0:
            filesToProcess.append(MediaFile(fullPath, "video", time.gmtime(os.path.getmtime(fullPath))))
            numberOfMovies = numberOfMovies + 1
           
tripRecords = TripRecord.readLocationsFile('/home/george/Documents/Programming/PhotosCategorize/TripDates.csv')

# go through each file and assign a valid TripRecord
for f in filesToProcess:
    for t in tripRecords:
        if f.CreatedDateTime.tm_year == t.Year and f.CreatedDateTime.tm_mon == t.Month and f.CreatedDateTime.tm_mday == t.Day:
            f.TripRecord = t
            


print "Number of pictures:", numberOfPictures
print "Number of movies:", numberOfMovies
print filesToProcess
