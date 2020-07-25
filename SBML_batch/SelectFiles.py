import os
import shutil
from SBML_batch import BaseFunctions
import libsbml

#to filter files we want to examine from files we don't care and others type of files
#files to examine will be in "dirToExamine", others file in "others" and "don't care" files in "dirNotAnalyze"
def select(rr, dirToExamine, dirNotAnalyze, others):
    
    #to create the directory for models we don't care to study
    BaseFunctions.createDirectoryExit(dirNotAnalyze)
    #to create the directory for others files
    BaseFunctions.createDirectoryExit(others)

    #list of files into directory
    files=os.listdir(dirToExamine)

    #to examine one file at a time
    for file in files:
        if file.endswith('.xml'):
            print(file)
            try:
                #to load the file with roadrunner
                rr.load(dirToExamine+'\\'+file)
            except:
                #if an error occurs we can't examine the file
                shutil.move(dirToExamine+'\\'+file, dirNotAnalyze)
                print('An error occurs during file load: To not analyze')
                continue
            
            #to get the model using libSBML
            model = libsbml.SBMLReader().readSBMLFromString(rr.getSBML()).getModel()
            
            #we don't want to analyze models with rules or events or qualitative models
            #we can't analyze in a correct way models which are bad read from libroadrunner.
            if  model.getNumRules()>0 or model.getNumEvents()>0 or model.getPlugin('qual')!=None or model.getNumSpecies()!=rr.model.getNumFloatingSpecies() or model.getNumReactions()!=rr.model.getNumReactions():
                shutil.move(dirToExamine+'\\'+file, dirNotAnalyze)
                print('To not analyze')            
        else:
            #we don't care other files
            shutil.move(dirToExamine+'\\'+file, others)  
        

#to decide if we want ot analyze a file or not
#it returns 0 if we want to study it, -1 if there is an error during file load, 1 if we don't want to study, 2 if it's not an xml file
#"path" is the path of directory which contains the file, and "file" it's the name of file.
def selectOneModel(rr, path, file):
    if file.endswith('.xml'):
        try:
            #to load the file with roadrunner
            rr.load(path+"\\"+file)
        except:
            #if an error occurs we can't examine the file
            print('An error occurs during file load: To not analyze')
            return -1
        
        #for get the model using libSBML
        model = libsbml.SBMLReader().readSBMLFromString(rr.getSBML()).getModel()
            
        #we don't want to analyze models with rules or events or qualitative models
        #we can't analyze in a correct way models which are bad read from libroadrunner.
        if  model.getNumRules()>0  or model.getNumEvents()>0 or model.getPlugin('qual')!=None or model.getNumSpecies()!=rr.model.getNumFloatingSpecies() or model.getNumReactions()!=rr.model.getNumReactions():
            print('To not analyze') 
            return 1

        return 0       
    else:
        #It's not an xml file
        return 2
    