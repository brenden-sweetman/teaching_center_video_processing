# Title: Auto Script for Teaching Center Video Encoding
# Author: Brenden Sweetman
#   brenden.sweetman@wustl.edu
#Created: 10/3/17
#Purpose:
# This script automates the video encoding procedure for the Teaching Center.
# NOTE: this script is very specific for this process it WILL NOT work to encode
# anything but the bio and chem videos supplied by the Teaching Center
#Usage:
# This script is activated by the "run" shell executable found in the same directory
#   as autoScript.py
# It can also be run from the command line using "python3 autoScript.py"
# The script relies on a particular file structure and file name format
#   File Structure:
#   All referenced files are stored in the parent directory "Teaching_Center_Video_Processing"
#   "Teaching_Center_Video_Processing" must contain 3 further subdirectories:
#       Copied, Final, and Resources
#   The "run" bash script and "autoScript.py" must also be stored at the base of "Teaching_Center_Video_Processing"
#   The "Copied" directory must contain all videos to be processed before the script is run
#   The "Copied" directory also must contain a "Done" directory to store the original files after processing
#   The "Final" directory stores the completed videos ready for upload
#   The "Resources" directory must contain a copy of the current copyright statement video clip:
#        "copyright.mp4" and a copy of the ffmpeg executable.
#   The complete file structure is given below:
#
#
#           |Teaching_Center_Video_Processing
#           |-->autoScript.py
#           |-->run
#           |-->|Copied
#           |   |--><Files to be processed>
#           |   |-->|Done
#           |       |--><Finished originals>
#           |
#           |-->|Final
#           |   |--><completed videos ready for upload>
#           |
#           |-->|Resources
#           |   |-->ffmpeg
#           |   |-->copyright.mp4
#
#
#   File Naming:
#   The files MUST all be named using the same structure.
#   All movie video files have 5 mandatory parts delimited with "-":
#       1)Class
#       2)Professor
#       3)Year
#       4)Month
#       5)Day
#   Classes with 2 or more video files will have a 6th part denoting the order of the videos
#   The files must be named in this way or the script will not run or will mess up the final video
#   This is the only way the script knows what video goes where!
#
#       The File naming convention is given below:
#       Class-Professor-Year-Month-Day-<part#>.mp4
#       Example file name for 1 part video:
#           chem451-mabbs-2017-10-01.mp4
#       Example file name for multi-part video:
#           chem451-mabbs-2017-10-01-part1.mp4
#           chem451-mabbs-2017-10-01-part2.mp4
# For more info on the script see coments below


import subprocess
from os import listdir
from os.path import isfile
import os
import sys
#get current working directory
cwd = os.getcwd()
# Escape codes to signal color to system terminal
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
#Set bitrate
bitRate="700k"

# This is the main function of the script
# It loops through each file in Copied marking if there is a 2 part video
# It calls errorHandler() and if successfull then cmdHandler() for each video
def main():
    #make list of files
    files = listdir(cwd+"/Copied/")
    #remove ".DS_Store" and "Done" from list
    if ".DS_Store" in files:
        files.remove(".DS_Store")
    files.remove("Done")
    # Sort file names (this is important to maintain the order of multi-part videos)
    files.sort()
    # Initiate input files list
    inputFiles=[]
    #loop through file list
    for i in range(0,len(files)):
        inputFiles.append(files[i])
        #a is the index of the next file to check for duplicates
        a=i+1
        #this while loop only works if files are named correctly and in order
        while(a<len(files) and files[i][:files[i].replace("-"," ",4).find("-")]==files[a][:files[a].replace("-"," ",4).find("-")]):
            print(str(i)+str(a))
            inputFiles.append(files[a])
            files.remove(files[a])
        # send the file name to errorHandler()
        if(errorHandler(inputFiles)):
            #if file name is error free send to cmdHandler()
            cmdHandler(inputFiles)
        inputFiles=[]
    #End program
    sys.stdout.write(BLUE)
    print("I have finished prossesing the all files provided in the Copied foler.")
    print("NOTE: if any files remian in the Copied folder I did not prosses them. Check the red text above for errors")
    sys.stdout.write(RESET)

# the cmdHandler() compiles a list of commands and class ffmpeg for file passed from errorHandler()
def cmdHandler(files):
    finalFileName=""
    # start compiling a list of comands see Documnetation for the ffmpeg command structure
    command=["Resources/ffmpeg","-loglevel","error","-i",cwd+"/Resources/copyright.mp4"]
    # add input file/files
    for f in files:
        command.append("-i")
        command.append(cwd+"/Copied/"+f)
    # add concatenate command
    complexString=""
    # creates command for
    for i in range(0,len(files)+1):
        complexString=complexString+"["+str(i)+":v:0] ["+str(i)+":a:0] "
    complexString=complexString+"concat=n="+str(len(files)+1)+":v=1:a=1 [v] [a]"
    command.extend(["-filter_complex", complexString , "-map" , "[v]" , "-map" , "[a]"])
    # add fps and bitrate to command
    command.extend(["-r", "29.97", "-b:v", str(bitRate), "-bufsize",str(bitRate)])
    # add final file name to output loaction
    if(len(files)>1):
        finalFileName="Final/"+files[0][:files[0].replace("-"," ",4).find("-")]+".mp4"
        command.append(finalFileName)
    else:
        finalFileName="Final/"+files[0]
        command.append(finalFileName)
    sys.stdout.write(BLUE)
    print("Processing...")
    sys.stdout.write(RESET)
    # run ffmpeg with compiled command
    subprocess.run(command)
    # Anounce the finished encode
    sys.stdout.write(BLUE)
    print(finalFileName[6:]+ " is done and ready for upload.")
    sys.stdout.write(RESET)
    # move original to done folder
    for f in files:
        subprocess.run(["mv",cwd+"/Copied/"+f,cwd+"/Copied/Done"])

#errorHandler checks the naming convention for file passed from main()
def errorHandler(files):
    sys.stdout.write(GREEN)
    print("\n\n\n\n")
    print("______________________________________Starting Next Video______________________________________")
    print("I think this is a "+ str(len(files))+ " part video:")
    sys.stdout.write(RESET)
    for i in range(0,len(files)):
        sys.stdout.write(BLUE)
        print ("Part "+str(i)+": "+files[i])
        sys.stdout.write(RESET)
        if (len(files[i].split("-"))!=5 and len(files)==1):
            sys.stdout.write(RED)
            print("Something is up with the file name")
            print("For 1 part videos the file name should look like this:")
            print("<Class>-<Prof>-<Year>-<Month>-<Day>.mp4")
            sys.stdout.write(RESET)
            return False
        #check naming convention for multi-part file
        if(len(files[i].split("-"))!=6 and len(files)>1):
            sys.stdout.write(RED)
            print("Something is up with the file name:")
            print("For multi-part videos the file name should look like this:")
            print("<Class>-<Prof>-<Year>-<Month>-<Day>-<Part#>.mp4")
            sys.stdout.write(RESET)
            return False
    #return true if files match naming convention
    return True


if __name__ == '__main__':
    main()
