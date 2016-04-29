# This script iterates through all of the files in a folder and prints the EXIF DateTimeOriginal tag
import os
import time
import datetime
import sys
import exifread
import csv
from operator import itemgetter, attrgetter, methodcaller

src = "/home/george/Documents/Sorted"
dest = "/home/george/Pictures"

csvFile = '/home/george/Documents/Programming/PhotosCategorize/TripDates.csv'

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
            self.Year = int(valueString[2])
            self.Month = int(valueString[1])
            self.Day = int(valueString[0])
        else:
            self.ValueString = None
            
    def __str__(self):
        if self.ValueString:        
            return "Day:" + str(self.Day) + " Month:" + str(self.Month) + " Year:" + str(self.Year) + " Place:" + self.Place + " Country:" + self.Country
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
    def __init__(self, fullPath, fileName, mediaType, createdDateTime):
        if fullPath:
            self.FullPath = fullPath
            self.FileName = fileName
            self.MediaType = mediaType
            self.CreatedDateTime = createdDateTime
            self.TripRecord = TripRecord("")
            
    def __str__(self):
        return "Path:" + self.FullPath + " File name:" + self.FileName + " MediaType:" + self.MediaType + " DateTime:" + time.strftime("%d %b %Y %H:%M:%S", self.CreatedDateTime) + " Trip Record:" + str(self.TripRecord)

    def __repr__(self):
        return str(self)

# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

numberOfPictures = 0
numberOfMovies = 0
filesToProcess = []

# create a list of filesToProcess by recursively walking from the src folder and finding pictures and videos
src = os.path.abspath(src)
for root, subdirs, files in os.walk(src):
    for file in files:
        fullPath = os.path.join(root, file)
               
        if file.lower().find(".jpg") > 0:
            f = open(fullPath, 'rb')        
            tags = exifread.process_file(f)
            for tag in tags.keys():
                if tag in ('EXIF DateTimeOriginal'):
                    # format: 2015:10:08 00:31:47
                                        
                    try:
                        tagDateTime = time.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        tagDateTime = time.strptime(str(tags[tag]), "%d/%m/%Y %H:%M")
                        
                    filesToProcess.append(MediaFile(fullPath, file, "picture", tagDateTime))
                    numberOfPictures = numberOfPictures + 1
        
        if file.lower().find(".mp4") > 0 or file.lower().find(".avi") > 0:
            filesToProcess.append(MediaFile(fullPath, file, "video", time.gmtime(os.path.getmtime(fullPath))))
            numberOfMovies = numberOfMovies + 1

print "Number of files ready for processing: %s" % (numberOfPictures + numberOfMovies)

# read the CSV file and sort it by date           
tripRecords = TripRecord.readLocationsFile(csvFile)
tripRecords = sorted(tripRecords, key = attrgetter('Year', 'Month', 'Day'))

# go through each file, find a valid TripRecord for it, create the target folder for it and move the file
numberOfFilesMoved = 0

for f in filesToProcess:
    for i in range(len(tripRecords)):
        tripRecordTime = time.strptime(str(tripRecords[i].Year) + ":" + str(tripRecords[i].Month) + ":" + str(tripRecords[i].Day), "%Y:%m:%d")
        if (f.CreatedDateTime >= tripRecordTime):
            f.TripRecord = tripRecords[i]
                    
    if hasattr(f, "TripRecord") and hasattr(f.TripRecord, "Year"):
        destPath = os.path.join(dest, str(f.TripRecord.Year), str(f.TripRecord.Country), str(f.TripRecord.Place))
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        fullDestPath = os.path.join(destPath, f.FileName)
        
        print "Move %s to %s" % (f.FullPath, fullDestPath)
        os.rename(f.FullPath, fullDestPath)
        numberOfFilesMoved = numberOfFilesMoved + 1
    else:
        print "WARNING: File %s does not have an associated trip record" % f.FullPath

print "Number of files moved:", numberOfFilesMoved