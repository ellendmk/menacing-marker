# Author: Ellen de Mello Koch
# Date: 20 June 2020
# 
# This script compiles a report using files produced by test_marker.py
# Each student has the following information collected:
#           * compile outputs when compiling C++ code with g++
#           * output file contents
#           * console output contents
#           * test result from comparing outputs to expected output
#           * code student submitted

import os
import zipfile
import codecs
import re
import string
import shutil
from subprocess import Popen, PIPE
from decimal import *
import math

rootdirTOP=os.getcwd()
rootdir=os.getcwd()

# Generates a report containing student test results
def genReport():

    # Setup latex file
    f = open("listings_settings.txt","r")
    listings_settings = f.read()
    f.close()    

    Docname="report_test.tex"
    document=open("reports/" + Docname,"w+")
    document.write("\\documentclass[9pt]{article}%\n")
    document.write("\\usepackage[margin=2cm]{geometry}%\n")
    document.write(listings_settings)
    document.write("\n\n\\begin{document}")

    top = os.chdir(rootdir)
    for subdir, dirs, files in os.walk(rootdir):
        dirs.sort()#alphabetical order
        for file in files:

            filename, file_extension = os.path.splitext(file)
            # If code submission is found proceed to gen report
            if file_extension == ".cpp"
                os.chdir(subdir)
                print(subdir)
                # Student name extracted from file structure
                student_name = str(subdir.split('/')[-2])
                document.write("\n\n\\section{" + name + "}\n\n")

                # Add compile log
                f = open("compile.txt")
                text = f.read()
                document.write("\n\n\\noindent\\begin{lstlisting}[style=cmdoutput,numbers=none,caption=compile log]\n" + text + "\n\\end{lstlisting}\n")
                f.close()
                
                # Add test results from marking script
                f = open("out_gen.txt")
                text = f.read()

                document.write("\n\n\\noindent\\begin{lstlisting}[style=cmdoutput,numbers=none]\n" + text + "\n\\end{lstlisting}\n")
                f.close()

                f = open("code.txt")
                text = f.read()
                document.write("\n\n\\noindent\\begin{lstlisting}[style=cmdoutput,numbers=none]\n" + text + "\n\\end{lstlisting}\n")

                f.close()

    document.write("\end{document}")
    document.close()
    os.chdir(os.path.join(rootdirTOP ,"reports"))
    print(os.system("pdflatex -interaction=nonstopmode " + Docname))
    print(total)

if __name__ == '__main__':
    if not os.path.exists("./reports/"):
        os.makedirs("./reports/")
    genReport()
    os.chdir(rootdirTOP)
    
