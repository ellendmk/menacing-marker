# Author: Ellen de Mello Koch
# Date: 20 June 2020
#
# This script automatically checks student code submissions downloaded from sakai
# Each students code is compiled and run on the inputs specified. 
# Student outputs are then compared to expected outputs.
#
# The following files are generated for each student:
#           * compile.txt - contains compile output from compiling their code using g++
#           * out_gen.txt - contains student and expected outputs and contains results from comparing these outputs
#           * code.txt - stores their source code 
#
# The above files for each student are compiled into a report which makes marking much easier using the script gen_report_text.py

import os
import zipfile
import re
import string
import shutil
from subprocess import Popen, PIPE
import subprocess
from decimal import *
import math
import signal
import time
import glob
import sys


# Set number of tests you would like to run students code on
# Input and output text files should be saved in a folder called test_cases
NUM_INPUT_TESTS = 3
folder_test = "./test_cases/"

inputList  = []
outputList = []

# Pre-load all test inputs and outputs into lists
for i in range(1,NUM_INPUT_TESTS+1):
    inFile = open(folder_test + "input" +str(i) + ".txt")
    inputList.append(inFile.read())
    outFile = open(folder_test + "output" +str(i) + ".txt")
    outputList.append(outFile.read())

rootdir = os.getcwd()
print (rootdir)

######################################################################################################
# Timeout alarm
def handler(signum, frame):
    raise Exception("Timeout")

signal.signal(signal.SIGALRM, handler)

######################################################################################################
def renameFolders():
    print( "Renaming folders")
    for subdir, dirs, files in os.walk("./" ):
        filenew=subdir.replace(' ', '')
        filenew=filenew.replace(',', '_')
        filenew=filenew.replace('-', '')
        filenew=filenew.replace('\'', '')
        filenew=filenew.replace('(', '')
        filenew=filenew.replace(')', '')
        os.rename(subdir,filenew)

######################################################################################################

def removePreviousSubmissions():
    print ("Removing all submissions but last.")
    for subdir, dirs, files in os.walk("./"):
        if ( len(files) > 1 ):
            length = len(files)
            for f in files:
                if f.find("+")>=0:
                    # os.remove(os.path.join(subdir,f))
                    print("Removed: ", subdir," ",f)
                # else:
                    # print("Didn't remove: ", f)



######################################################################################################
def renameCPP():
    print ("Renaming cpp files.")
    for subdir, dirs, files in os.walk("./"):
        for file_name in files:
            # print(os.path.join(subdir, file_name))
            filenew=file_name.replace(' ', '')
            filenew=filenew.replace(',', '_')
            filenew=filenew.replace('-', '')
            filenew=filenew.replace('\'', '')
            filenew=filenew.replace('(', '')
            filenew=filenew.replace(')', '')
            os.rename(os.path.join(subdir,file_name),os.path.join(subdir,filenew))
            filename, file_extension = os.path.splitext(file_name)
            if file_extension == ".cpp":
                folders=subdir.split('/')
                index = 0
                for i in range(0,len(folders)):
                    folders[i] = folders[i].replace(" ","_")
                    folders[i] = folders[i].replace(",","")
                    folders[i] = folders[i].replace("-","")
                    folders[i] = folders[i].replace("\'","")
                    folders[i] = folders[i].replace("(","")
                    folders[i] = folders[i].replace(")","")
                    if folders[i].find("Submission")>=0:
                        index = i
                os.rename(os.path.join(subdir,filenew), os.path.join(subdir,str(folders[index-1]))+'.cpp')

######################################################################################################
#unzip recursively
def unzipFolders():
    
    print ("Unzipping files.")
    for x in range(0,2):
        for subdir, dirs, files in os.walk("./"):

            for file_name in files:
                filename, file_extension = os.path.splitext(file_name)
                if file_extension == ".zip":
                    PATH= os.path.join(subdir, file_name)
                    zip_ref = zipfile.ZipFile(PATH, 'r')
                    zip_ref.extractall(os.path.join(subdir, filename))
                    zip_ref.close()
    return

######################################################################################################
def gen_input_files(test):
    f = open("input.txt","w")
    f.write(inputList[test])
    f.close()

######################################################################################################

def compile_run_code():
    print ("Compiling and running code.")
    #Keep track of current directory
    top = os.getcwd()+"/"
    #Iterate through subdirectories
    for subdir, dirs, files in os.walk(top):
        onlyfiles=''
        for file_name in files:
            filename, file_extension = os.path.splitext(file_name)
            #Find all source code files
            # if subdir.find("1876781")>=0:
            if file_extension=="" and filename!="run":
                print(subdir)
                print(filename,file_extension=="")
                input()
            if file_extension == ".h" or file_extension == ".cpp":
                onlyfiles=str(onlyfiles)+" "+str(file_name)
            if file_extension==".txt" and subdir.find("test_cases")<0 and (filename.find("tput")>=0 or filename.find("TPUT")>=0 or filename.find("input")>=0):
                os.remove(os.path.join(subdir,file_name))

        #If we found source code
        if onlyfiles!='':
            #Change directory to subdir
            print (subdir)
            os.chdir(subdir)
            #Compile code
            p=Popen("g++ "+onlyfiles+" -o run",shell=True,stdout=PIPE,stderr=PIPE,encoding="utf-8")
            out, err = p.communicate()
            ########----Compile log----########
            f = open(str(subdir)+"/compile.txt","w+")
            f.write(str(err.strip()))
            f.close()
            ########----Code log----########
            code=open(str(subdir)+"/code.txt","w+")
            source=open(onlyfiles.replace(' ',''))
            try:
                code.write(str(source.read()))
            except Exception as exc:
                code.write("\nException: "+str(exc))
            code.write("\n\nFILES IN DIRECTORY\n\n")
            ########----All files in folder log----########
            subfiles = [subf for subf in os.listdir('.') if os.path.isfile(subf)]
            allfiles=""
            for subf in subfiles:
                allfiles+=(", "+subf)
            code.write(str(allfiles))
            code.close()
            source.close()
            ########----Test code----########
            score=0
            console_score=0
            out=open(str(subdir)+"/out_gen.txt","w+")
            console=""

            #Check output for each tests 
            for test_num in range(0,len(inputList)):
                reachedException=False
                gen_input_files(test_num)

                #Alarm timeout is 5 seconds to prevent infinite loops
                signal.alarm(5)
                f1=None
                lines1=None
                try:
                    # Try execute code
                    print ("Running")
                    p1 = Popen(["./run"], stdout=PIPE,encoding="utf-8")
                    console,errors=p1.communicate()
                    print(console)
                    print ("Done")
                    # console=console.decode('utf-8','ignore')

                except Exception as exc:
                    print( "Exception "+str(exc))

                    out.write("\nERROR: "+str(exc))
                    reachedException=True
                    os.system("killall run")
                # Make sure ram is cleared of infinite loops
                print ("Done")
                if reachedException==0:
                    out.write("Console:\n")
                    for charC in range(0,len(console)):
                        if charC>20:
                            out.write(" ERROR output too long.")
                            break
                        else:
                            out.write(str(console[charC]))
                out.write("\n\n")
                # Reset alarm
                signal.alarm(0)

                #Collect common strange names students name their output files
                listOut1=glob.glob('o*put*')
                listOut2=glob.glob('*TPUT*')
                listOut3=glob.glob('*ou*ut')
                listOut=listOut1+listOut2+listOut3
                if listOut!=None and len(listOut)>0 and reachedException==False:
                # True if file exists
                    for nameF in listOut:
                        lines1=None
                        f2=open(nameF)
                        fileText=""
                        try:
                            text=f2.read()
                            fileText=text
                            f2.close()
                        except Exception as exc:
                            fileText="\nException: "+str(exc)+"\n"
                        f2=open(nameF)
                        lines1=f2.readlines()

                        # Log file contents
                        out.write("*********out_gen.txt**********")
                        out.write("\nTEST "+str(test_num)+" "+str(nameF)+": \n")
                        out.write("\n\nACTUAL:\n")
                        out.write(fileText)

                        #Check output matches memo
                        score+=outputMatches(lines1,test_num)
                        console_score+=outputMatches(console,test_num)

                        out.write("\nCORRECT: \n")
                        out.write(outputList[test_num]+"\n")
                        out.write("-------------------------------------\n")
                        
                else:
                    out.write("\nTEST "+str(test_num)+": ")
                    out.write("  NO OUTPUT PRODUCED")
                    out.write("\nCORRECT: ")
                    out.write("\n---------------------------------------\n")
                    out.write(outputList[test_num]+"\n")
                    out.write("-----------------------------------------\n")
                    
                if f1!=None:
                    f1.close()
            print( "\nSCORE = "+str(float(score)/len(inputList)*100)+"\n\n")
            print( "\nCONSOLE SCORE = "+str(float(console_score)/len(inputList)*100)+"\n\n")
            out.write("\nSCORE = "+str(float(score)/len(inputList)*100)+"\n\n")
            out.write("\nCONSOLE SCORE = "+str(float(console_score)/len(inputList)*100)+"\n\n")
            out.close()
            os.system("killall run")

######################################################################################################

def outputMatches(lines, test):
    #  Tidy up lines  #
    #Remove blank
    lines = [line for line in lines if line.replace(" ","")!="\n"]
    #Remove spaces at end of line
    lines = [line.rstrip() for line in lines]
    memoLines=[]
    #Get memo in correct from
    memoLines =outputList[test].split("\n")

    #Remove blank
    memoLines = [memo for memo in memoLines if memo.replace(" ","")!="\n"]
    #Remove spaces at end of line
    memoLines = [memo.rstrip() for memo in memoLines]
    memoLines = [memo for memo in memoLines if memo!=""]
    if len(lines)<len(memoLines):
        return 0
    for item in range(0,len(memoLines)):
        if lines[item]!=memoLines[item]:
            return 0

    return 1
    
######################################################################################################
if __name__ == '__main__':
    # unzipFolders()
    # renameFolders()
    # removePreviousSubmissions()
    renameCPP()
    compileAndRunCode()
