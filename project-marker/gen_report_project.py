import os
import zipfile
import codecs
import glob


import re
import string
import shutil
from subprocess import Popen, PIPE
from decimal import *
import math
rootdirTOP=os.getcwd()
rootdir=os.getcwd()

def genReport(student_no=None):
    rootdir=os.getcwd()
  

    f = open("listings_settings.txt","r")
    listings_settings = f.read()
    f.close()

    print ("Generating report.")
 

    top = os.chdir(rootdir)
    for subdir, dirs, files in os.walk(rootdir):
        dirs.sort()#alphabetical order
        file_list = []
        if student_no!=None and subdir.find(student_no)<=0:
            continue
        print(subdir)
        for file in sorted(files):
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".h" or file_extension == ".cpp":
                file_list.append(file)

            if len(file_list)>0:
                " ".join(file_list)
                os.chdir(subdir)

                #INITIALISE DOC   
                Docname  = str(subdir.split('/')[-2]) + ".tex"
                document = open(Docname,"w+")
                document.write("\\documentclass[9pt]{article}%\n")
                document.write("\\usepackage[margin=2cm]{geometry}%\n")
                document.write(listings_settings)
                filename, file_extension = os.path.splitext(file)
                print (file_list)
                document.write("\n\n\\title{"+subdir.split('/')[-2].replace("_"," ")+"}\n\\author{}\n")
                document.write("\\begin{document}%\n\n\n\n\\maketitle\n\n")

                
                #ADD COMPILE LOG            
                document.write("\\subsection*{compile\\textunderscore log.txt}\n\n")
                f = open("compile_log.txt")
                compile_text = f.read()#re.sub(r'[^a-zA-Z0-9\._\-<>#+*&|/,"\']', '', f.read())
                print(compile_text)
                document.write("\n\n\\noindent\\begin{lstlisting}[style=cmdoutput,numbers=none]\n"+compile_text+"\n\\end{lstlisting}\n")
                f.close()

                #ADD RUN LOG
                if os.path.isfile("run_log.txt"):            
                    f    = open("run_log.txt")
                    text = f.read()#str(re.sub(r'[^a-zA-Z0-9\._\-<>#+*&|/,"\']', '', f.read()))
                    print(text)
                    document.write("\\section*{run\\textunderscore log.txt}\n"+(text)+"\n")
                    f.close()

                #ADD GAME RESULTS    
                if os.path.isfile("game_results_log.txt"):
                    f    = open("game_results_log.txt")
                    text = f.read()
                    print(text)
                    document.write("\\section*{game\\textunderscore results\\textunderscore log.txt}\n\\begin{lstlisting}[style=cmdoutput,numbers=none]\n"+(text)+"\n\\end{lstlisting}\n\n\n")
                    f.close()

                game_images = ["games_0_init1.pdf","games_0_init2.pdf","games_1_init1.pdf","games_1_init2.pdf","games_2_init1.pdf","games_2_init2.pdf","games_3_init1.pdf","games_3_init2.pdf","games_4_init1.pdf","games_4_init2.pdf","games_5_init1.pdf","games_5_init2.pdf","games_6_init1.pdf","games_6_init2.pdf"]

                game_images_1 = []
                game_images_2 = []

                for i in game_images:
                    if i.find("init1")>=0:
                        game_images_1.append(i)
                    else:
                        game_images_2.append(i)

                if len(glob.glob(subdir+"/games*.pdf"))>0:
                    #inint 1

                    document.write("\\begin{figure}[ht!]\n")
                    for i in range(len(game_images_1)):
                        if os.path.isfile(subdir+"/"+game_images_1[i]):
                            if i%2==0:
                                document.write("\\vfill\\eject\n\\begin{subfigure}{0.4\\textwidth}\n   \includegraphics[width=\\textwidth]{"+game_images_1[i]+"}\n   \\caption{"+game_images_1[i].replace("_","-")+"} \n   \\end{subfigure}~\n")
                            else:
                                document.write("   \\begin{subfigure}{0.4\\textwidth}\n   \includegraphics[width=\\textwidth]{"+game_images_1[i]+"}\n   \\caption{"+game_images_1[i].replace("_","-")+"}\n   \\end{subfigure}\n")

                    document.write("\n\\end{figure}\n\n\n")
                    #inint 2
                    document.write("\\begin{figure}[ht!]\n")
                    for i in range(len(game_images_2)):
                        if os.path.isfile(subdir+"/"+game_images_2[i]):
                            if i%2==0:
                                document.write("\\vfill\\eject\n   \\begin{subfigure}{0.4\\textwidth}\n   \includegraphics[width=\\textwidth]{"+game_images_2[i]+"}\n   \\caption{"+game_images_2[i].replace("_","-")+"} \n   \\end{subfigure}~~\n")
                            else:
                                document.write("   \\begin{subfigure}{0.4\\textwidth}\n   \includegraphics[width=\\textwidth]{"+game_images_2[i]+"}\n   \\caption{"+game_images_2[i].replace("_","-")+"}\n   \\end{subfigure}\n")

                    document.write("\n\\end{figure}\n\n\n")
                #ADD ISSUES WHEN RUNNING GAME TESTS    
                if os.path.isfile("output_file_test_log.txt"):
                    f    = open("output_file_test_log.txt")
                    text = f.read()
                    document.write("\\section*{output\\textunderscore file\\textunderscore test\\textunderscore log.txt}\n"+(text)+"\n\n")
                    f.close()     

                #ADD SOURCE CODE     

                document.write("\\section*{source code}\n\n")
                try:
                    for f_name in file_list:
                        print(f_name)

                        f=open(f_name,'rb')
                        
                        text = f.read().decode(encoding='UTF-8')#str(re.sub(r'[^a-zA-Z0-9\._\-<>#+*&|/,"\']', '', f.read()))
                        print(text)
                        document.write("\\begin{lstlisting}[caption=" + f_name.replace("_"," ") + ",style=cmdoutput]\n"+text+"\\end{lstlisting}\n\n")
                        f.close()     
                except:
                        document.write("\\begin{lstlisting}[caption=" + f_name.replace("_"," ") + ",style=cmdoutput]\nError writing code: see actual source code file.\\end{lstlisting}\n\n")


                document.write("\end{document}")
                print(os.system("pdflatex -interaction=nonstopmode " + Docname))

def delete_previous_reports(student_no=None):
    print( "Deleting report files.")
    file_list = [".aux",".fls",".tex",".log",".dvi",".fdb_latexmk",".fuse",".gz"]
    for subdir, dirs, files in os.walk(rootdir):
        if student_no!=None and subdir.find(student_no)<0:
            continue
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension in file_list or filename.find("fuse")>=0 or file_extension.find("fuse")>=0:
               os.remove(os.path.join(subdir,file))
    return

def pdflatex_files(student_no=None):
    
    for subdir, dirs, files in os.walk(rootdir):
        dirs.sort()#alphabetical order
        file_list = []
        if student_no!=None and subdir.find(student_no)<=0:
            continue
        print(subdir)
        for file in sorted(files):
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".tex":
                file_list.append(file)
        if len(file_list)>0:
            os.chdir(subdir)
            print(os.system("pdflatex -interaction=nonstopmode " + file_list[0]))
    os.chdir(rootdir)


if __name__ == '__main__':
 
    # student_no = "2095377"
    # student_no = None
    # delete_previous_reports(student_no)
    # genReport(student_no)