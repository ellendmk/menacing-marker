# Author: Ellen de Mello Koch
# Date: 20 June 2020
#
# This script allows the marking of c++ project submissions
# It makes use of the decode_output.py and gen_report_project_scripts.py

import os
import zipfile
import re
import string
import shutil
from subprocess import Popen, PIPE, STDOUT, check_output

import subprocess
from decimal import *
import math
import signal
import time
import glob
from eventlet.timeout import Timeout

from threading import Timer

from decode_output import *
from gen_report_project import *

test_input = "6\n8\n10\n12"

rootdir    = os.getcwd()
rootdirTop = os.getcwd()


def handler(signum, frame):
    raise Exception("Timeout")

def rename_files_and_folders(directory=rootdir):
    for subdir in os.listdir(directory):
        if  subdir.find(".h")>0:
            continue
        filenew = subdir.replace(' ', '')
        filenew = filenew.replace(',', '_')
        filenew = filenew.replace('-', '')
        filenew = filenew.replace('\'', '')
        filenew = filenew.replace('(', '')
        filenew = filenew.replace(')', '')
        os.rename(subdir,filenew)
        if os.path.isdir(filenew):
            os.chdir(filenew)
            rename_files_and_folders(".")
            os.chdir("..")


def unzip_folders():
    print( "Unzipping files.")
    for x in range(0,3):
        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                filename, file_extension = os.path.splitext(file)
                if file_extension == ".zip":
                    PATH = os.path.join(subdir, file)
                    zip_ref = zipfile.ZipFile(PATH, 'r')
                    zip_ref.extractall(os.path.join(subdir, filename))
                    zip_ref.close()
    return

def compile_code(onlyfiles, otherfiles):
    p=Popen("g++ "+onlyfiles+" -o run",shell=True,stdout=PIPE,stderr=PIPE,encoding="utf-8")
    out, err = p.communicate()
    p.wait()
    compile_text = "Output:\n" + str(out) + "Errors:\n" + str(err.strip())
    compile_text += "\nOther files: " + otherfiles 
    log("compile_log.txt",compile_text.replace("b''",""))
    if len(str(err).replace("b''",""))<3:
        return True
    return False


def run_code(subdir):
    #Create input file
    create_input(test_input)
    #Set timeout to end code if takes to long to run
    reached_exception=False

    run_text     = ""
    temp_console = None
    timeout = Timeout(1, handler)

    if not os.path.isfile(subdir+"/run"):
        return
    os.chdir(subdir)
    print ("\nDirectory: "+str(subdir)+"\n")
    p1 = Popen('./run', stdout=PIPE,encoding="utf-8")
    timer = Timer(120, p1.kill)
        
    try:
        timer.start()
        temp_console, errors = p1.communicate()    
        timer.cancel()
    except Exception as exc:
        print ("Reached exception: ",exc)

        run_text += ("\nRUNTIME ERROR: " + str(exc))
        reached_exception=True
        os.system("killall run")
    signal.alarm(0)

    os.system("killall run")
    temp_console = str(temp_console)
    
    if reached_exception == 0:
        for charC in range(0,len(temp_console)):
            if charC>10000:
                run_text += (" ERROR output too long.")
                break
            else:
                run_text += (temp_console[charC])

    log("run_log.txt",run_text.replace("b''",""))


def log(file_name, text):
    f = open(file_name, 'a+')
    f.write(text)
    f.close()

def create_input(input_text):
    f = open("input.txt",'w')
    f.write(input_text)
    f.close()

def delete_student_output_files(student_num):
    print( "Deleting student output files.")
    possible_output_names = ['*sult*.txt', '*tput*.txt', '*SULT*.txt', '*PUT*.txt']
    FOUND_STUD = False
    for subdir, dirs, files in os.walk(rootdir):
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        for item in possible_output_names:
            new_files = glob.glob(subdir+"/"+item)
            for file_name in new_files:
                print(file_name, " removed")
                os.remove(os.path.join(subdir,file_name))
    return

def compile_and_run_code(student_num=None):
    print( "Compiling and running code.")
    FOUND_STUD = False

    top = os.getcwd()
    os.chdir(top)
    for subdir, dirs, files in os.walk(top):

        #Sort dirs in alphabetical order
        dirs.sort()
        file_list = ''
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        print ("\nDirectory: "+str(subdir)+"\n")

        for file in sorted(files):
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".h" or file_extension == ".cpp":
                
                file_list = str(file_list) + " " + str(file)
       
        if file_list!='':
            os.chdir(subdir)
           
            subfiles  = [subf for subf in os.listdir('.') if os.path.isfile(subf)]
            all_files = ""

            #Check other txt files etc in folder 

            for subf in subfiles:
                if subf[0]!=".":
                    all_files += (" " + subf)

            # Compile source code files found
            compile_success = compile_code(file_list, all_files)
            
            # Run code
            if compile_success == True:
                run_code(subdir)
            

def run_tests_on_output(student_num=None):
    print( "Testing code.")
    top = os.getcwd()
    FOUND_STUD = False
    os.chdir(top)
    for subdir, dirs, files in os.walk(top):
        #Sort dirs in alphabetical order
        dirs.sort()

        file_list = ''
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        print ("\nDirectory: "+str(subdir)+"\n")

        for file in sorted(files):
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".h" or file_extension == ".cpp":
                
                file_list = str(file_list) + " " + str(file)
       
        if file_list!='':
            os.chdir(subdir)

            possible_output_names = ['*sult*.txt', '*tput*.txt', '*istor*.txt']
            output_results_list = ["game_results_log.txt","output_file_test_log.txt"]

            output_list = []
            for item in possible_output_names:
                new_files = glob.glob(item)
                for new_item in new_files:
                    if new_item not in output_results_list:
                        output_list.append(new_item)


            #Check output exists and isn't too long
            if output_list!=None and len(output_list) > 0:
                for output_file in output_list:
                    # Try run tests on output file
                    # try:
                    test_output_file(os.getcwd(), output_file)
                    # except Exception as error:
                    # log("output_file_test_log.txt", "Failed to test code due to exception\n" + str(error))
                    
            
def delete_log_files(student_num=None):
    print( "Deleting log files.")
    FOUND_STUD = False

    file_list = ["compile_log","run_log"]
    for subdir, dirs, files in os.walk(rootdir):
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".txt" and filename in file_list:
               os.remove(os.path.join(subdir,file))
    return

def delete_test_output_file(student_num=None):
    print( "Deleting test results log files.")
    FOUND_STUD = False

    file_list = ["game_results_log","output_file_test_log"]
    for subdir, dirs, files in os.walk(rootdir):
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".txt" and filename in file_list:
               os.remove(os.path.join(subdir,file))
    return


                   
def delete_images(student_num=None):
    print( "Deleting log files.")
    FOUND_STUD = False
    
    for subdir, dirs, files in os.walk(rootdir):
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        games_pdf = glob.glob(subdir+"/games*.pdf")
        for file in games_pdf:
            os.remove(os.path.join(subdir,file))


def find_extra_submits(student_num=None):
    FOUND_STUD = False

    for subdir, dirs, files in os.walk(rootdir):
        if (student_num!=None and subdir.find(student_num)<0 and FOUND_STUD==False):
            continue

        for file in sorted(files):
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".h" or file_extension == ".cpp":
                if filename.find("+")>=0:
                    print(subdir)

if __name__ == '__main__':
    stud_no = None
    delete_log_files(stud_no)
    compile_and_run_code(stud_no)
    delete_images(stud_no)
    delete_test_output_file(stud_no)
    run_tests_on_output(stud_no)
    os.chdir(rootdir)
    genReport(stud_no)