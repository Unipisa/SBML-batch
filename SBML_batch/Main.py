#used to work with biological models
import roadrunner
#used to work with directory 
import os
import shutil
#used to work with matrix and array
import numpy as np
import libsbml

from SBML_batch import Simulation
from SBML_batch import SelectFiles
from SBML_batch import Deficiency_Calculation
from SBML_batch import BaseFunctions
from SBML_batch import PetriNets




def analysisTheorems(rr, dirToExamine, dirNotAnalyze, dirToSimulation, dirTheorems):

    BaseFunctions.createDirectoryExit(dirToSimulation)
    BaseFunctions.createDirectoryExit(dirTheorems)
    BaseFunctions.createDirectoryExit(dirTheorems+"\\not_known")
    BaseFunctions.createDirectoryExit(dirTheorems+"\\SteadyState")

    
    #analyze each file into the directory
    files=os.listdir(dirToExamine)
    
    for file in files:
        if file.endswith('.xml'):
            print(file)
            rr.clearModel()

            try:
                rr.load(dirToExamine+'\\'+file)
            except:
                shutil.move(dirToExamine+'\\'+file, dirNotAnalyze)
                print('Not_Analyze')
                continue
            
            #check of use of mass action
            if Simulation.toSimulate(rr)==1:
                #theorems are not applicable
                shutil.move( dirToExamine+'\\'+file, dirToSimulation)
                continue
            
            #study of model with Feinberg's theorems
            results=Deficiency_Calculation.deficiency_calculation(rr)
            if results[1]==1:
                print("Cannot use Feinberg's theorems")
                shutil.move(dirToExamine+'\\'+file, dirToSimulation)
            elif results[0]==0 or results[0]==1:
                print("Model reaches steady state")
                shutil.move(dirToExamine+'\\'+file, dirTheorems+"\\SteadyState")
            else:
                print("Unknown behavior")
                shutil.move(dirToExamine+'\\'+file, dirTheorems+"\\not_known")



#the main function that defines the flow of program. It permits to choice
#the functionality to execute with the parameter "func" that it's 0 by default:
#func=1: select files with determined feautures;
#func=2: study the models with Feimberg's theorems
#func=3: simulate models studying their behaviour 
#func=4: create Petri nets of models
#func=0: execute all the previous functionality
#in input this method takes 4 parameters:
#interval that correspond to the change in quantities species
#maxInterval that is the maximum range in which quantities change
#dirToExamine that correspond to the directory that contains models to studying
#func, previous described 
def main(interval=-1, maxInterval=20, dirToExamine="models", func=0):
    #for use the library libRoadRunner
    rr=roadrunner.RoadRunner()

    simulationTime=20000
    mintime=0

    nTest=10
    increase=5

    dirNotAnalyze="Not_Analyze"
    dirOtherFiles="Other_Files"
    dirPetriNets=os.getcwd()+'\\PetriNets'
    dirTheorems=os.getcwd()+'\\Theorems_Models'
    dirResultsTheorems=os.getcwd()+'\\Results_Theorems'
    dirToSimulation=os.getcwd()+'\\Simulate_Models'
    dirResultsSimulation=os.getcwd()+'\\Results_Simulations'
    

    if func==1:
        SelectFiles.select(rr, dirToExamine, dirNotAnalyze, dirOtherFiles)
    elif func==2:
        analysisTheorems(rr, dirToExamine, dirNotAnalyze, dirToSimulation, dirTheorems)    
    elif func==4:
        PetriNets.createPetriNets(rr, dirToExamine, dirPetriNets, nTest, increase)
    elif func in [0, 3]:
        
        if interval<=0:
            interval=BaseFunctions.numericalInput('Range of initial perturbation (X %) : ',[])
        
        if interval<=0 or maxInterval<=0 or interval>maxInterval:
            exit("Error: invalid interval parameters")

        #contains the percentages to modify the quantities of species
        percent=[]
        i=interval
        while i<=maxInterval:
            percent.append(i)
            i=i+interval
        
        if func==3:
            Simulation.simulateAllModels(rr, dirToExamine, dirResultsSimulation, dirNotAnalyze, simulationTime, mintime, percent)
        else:

            #select models with certain characteristics
            SelectFiles.select(rr, dirToExamine, dirNotAnalyze, dirOtherFiles)
            
            analysisTheorems(rr, dirToExamine, dirNotAnalyze, dirToSimulation, dirTheorems)
                    
            BaseFunctions.createDirectoryExit(dirResultsTheorems)

            #model's simulations
            files=os.listdir(dirTheorems+"\\SteadyState")
            for file in files:     
                Simulation.simulationWithSteadyState(rr, percent, dirResultsTheorems+"\\SteadyState", dirTheorems+"\\SteadyState", file)
            Simulation.simulateAllModels(rr, dirTheorems+"\\not_known", dirResultsTheorems+"\\not_known", dirNotAnalyze, simulationTime, mintime, percent)
            Simulation.simulateAllModels(rr, dirToSimulation, dirResultsSimulation, dirNotAnalyze, simulationTime, mintime, percent)
            
            #creation of Petri nets
            print("Petri Nets")
            PetriNets.createPetriNets(rr, dirToSimulation, dirPetriNets, nTest, increase)
            PetriNets.createPetriNets(rr, dirTheorems+"\\not_known", dirPetriNets, nTest, increase)
            PetriNets.createPetriNets(rr, dirTheorems+"\\SteadyState", dirPetriNets, nTest, increase)
            
    else:
        print("Invalid parameter")