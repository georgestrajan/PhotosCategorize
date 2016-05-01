#!/usr/bin/python

# This script iterates through all of the pictures and videos in a folder and processes the moves or copies the files based on the date they were taken
import os
import shutil
import time
import collections
import datetime
import sys
import exifread
import csv
import argparse
from operator import itemgetter, attrgetter, methodcaller

TAG_EXIF_DateTimeOriginal = "EXIF DateTimeOriginal"

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Source directory where all the original files are")
parser.add_argument("dest", help="Destination directory where all of the files will be moved\copied to")
parser.add_argument("csv", help="CSV file which contains the dates and places where the photos were taken. Columns are Day,Month,Year,Location,Country")
parser.add_argument("--v", help="set verbosity. 0 is for errors only. 1 is default. 2 is verbose.")
parser.add_argument("--o", help="the operation to perform on the files. Can be copy, move or display (to just display the output)")
args = parser.parse_args()

src = args.source #"/home/george/Pictures/Original"
dest = args.dest #"/home/george/Pictures/Sorted"
csvFile = args.csv #'/home/george/Documents/Programming/PhotosCategorize/TripDates.csv'

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
            self.DateTime = time.strptime(valueString[2] + ":" + valueString[1] + ":" + valueString[0], "%Y:%m:%d")
        else:
            self.ValueString = None
            
    def __str__(self):
        if self.ValueString:        
            return str(self.DateTime) + " Place:" + self.Place + " Country:" + self.Country
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
    def __init__(self, fullPath, fileName, createdDateTime):
        if fullPath:
            self.FullPath = fullPath
            self.FileName = fileName
            self.CreatedDateTime = createdDateTime
            self.TripRecord = TripRecord("")
            
    def __str__(self):
        return "Path:" + self.FullPath + " File name:" + self.FileName + " DateTime:" + time.strftime("%d %b %Y %H:%M:%S", self.CreatedDateTime) + " Trip Record:" + str(self.TripRecord)

    def __repr__(self):
        return str(self)

#
# Prints a message to the console
# Verbosity is as follows:
#   0 is for errors (which are always displayed)
#   1 is for regular verbosity
#   2 is for extra verbose
def printMessage(strMessage, verbosity = 1):
    if verbosity == 0:
        print(strMessage)
    elif verbosity == 1:
        print(strMessage)
    elif args.v == verbosity:
        print(strMessage)


# Processes a file according to the chosen method (copy, move)
def processFile(fullFilePath, fullDestPath):
    printMessage("Processing file %s. Destination folder is %s" % (f.FullPath, fullDestPath), 2)
    if args.o == "copy":
        printMessage("Copying %s to %s" % (f.FullPath, fullDestPath))
        shutil.copy(f.FullPath, fullDestPath)
    elif args.o == "move":
        printMessage("Moving %s to %s" % (f.FullPath, fullDestPath))
        os.rename(f.FullPath, fullDestPath)

# this command will count the number of pictures and videos in the folder
# find /home/george/Pictures/Test -regex '.*\.\(jpg\|JPG\|mp4\|MP4\)' | tee >(wc -l)

numberOfPictures = 0
numberOfMovies = 0
filesToProcess = []

if not os.path.exists(src):
    printMessage("Source folder '%s' does not exist!" % src, 0)
    sys.exit(1)

if not os.path.exists(csvFile):
    printMessage("CSV file '%s' does not exist!" % csvFile, 0)
    sys.exit(1)

printMessage("Processing files from '%s'. Destination is '%s'. CSV file is '%s'\n" % (src, dest, csvFile))

# create a list of filesToProcess by recursively walking from the src folder and finding pictures and videos
src = os.path.abspath(src)

for root, subdirs, files in os.walk(src):
    printMessage("Processing folder %s" % root)

    for file in files:
        fullPath = os.path.join(root, file)
        if file.lower().find(".jpg") > 0:
            f = open(fullPath, 'rb')        
            tags = exifread.process_file(f, details = False, stop_tag = TAG_EXIF_DateTimeOriginal)
            for tag in tags.keys():
                if tag == TAG_EXIF_DateTimeOriginal:
                    # format: 2015:10:08 00:31:47
                    try:
                        tagDateTime = time.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        tagDateTime = time.strptime(str(tags[tag]), "%d/%m/%Y %H:%M")
                        
                    filesToProcess.append(MediaFile(fullPath, file, tagDateTime))
                    numberOfPictures += 1
        
        if file.lower().find(".mp4") > 0 or file.lower().find(".avi") > 0:
            filesToProcess.append(MediaFile(fullPath, file, time.gmtime(os.path.getmtime(fullPath))))
            numberOfMovies += 1

print "Number of files ready for processing: %s\n" % (numberOfPictures + numberOfMovies)

# read the CSV file and sort it by date           
tripRecords = TripRecord.readLocationsFile(csvFile)
tripRecords = sorted(tripRecords, key = attrgetter('DateTime'))

# go through each file, find a valid TripRecord for it, create the target folder for it and move the file
numberOfFilesMoved = 0
filesNotMoved = []
destinationPathNumberOfFiles = {}

for f in filesToProcess:
    for i in range(len(tripRecords)):
        if (f.CreatedDateTime >= tripRecords[i].DateTime):
            f.TripRecord = tripRecords[i]
                    
    if hasattr(f, "TripRecord") and hasattr(f.TripRecord, "DateTime"):
        destPath = os.path.join(dest, str(f.TripRecord.DateTime.tm_year), str(f.TripRecord.Country), str(f.TripRecord.Place))

        if not os.path.exists(destPath):
            printMessage("Destination folder %s does not exist. Creating it." % destPath)
            os.makedirs(destPath)
        fullDestPath = os.path.join(destPath, f.FileName)

        if destPath in destinationPathNumberOfFiles:
            destinationPathNumberOfFiles[destPath] += 1
        else:
            destinationPathNumberOfFiles[destPath] = 0

        processFile(f.FullPath, fullDestPath)
        numberOfFilesMoved = numberOfFilesMoved + 1

    else:
        filesNotMoved.append(f.FullPath)
        print "WARNING: File %s does not have an associated trip record" % f.FullPath

for k, v in destinationPathNumberOfFiles.iteritems():
    printMessage("\n%d files processed to destination folder %s" % (v, k))
