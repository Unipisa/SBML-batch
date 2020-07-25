import os
import numpy as np
import shutil
from SBML_batch import BaseFunctions
import libsbml


#parameters used in the simulation
_step=100
_interval=25
_points=_step*5



#to simulate a set of models
#this method need the reference to libRoadRunner, the paths of directory that will be used, the simulation time, the
#minimum time used during model's behaviour analysis, the intervals to change quantities of species, 
#number of point generate during a simulation (optional)
def simulateAllModels(rr, dirToSimulation, toPath, dirReject, simulationTime, time, percent, points=_points):
    files=os.listdir(dirToSimulation)
    for file in files:
        if file.endswith('.xml'):
            print(file)
            simulateModel(rr, dirToSimulation, file, toPath, dirReject, simulationTime, time, percent, points)
    



#To simulate a model studying his behaviour. It returns 1 if an error occur, 0 otherwise
#this method need the reference to libRoadRunner, the file to simulate, the paths of directory that will be used, 
#the simulation time, the minimum time used during model's behaviour analysis, the intervals to change quantities 
#of species, number of point generate during a simulation (optional)
def simulateModel(rr, path, file, toPath, dirReject, simulationTime, time, percent, points=_points):


    #creation of directories used
    if BaseFunctions.createDirectory(dirReject)==1 or BaseFunctions.createDirectory(toPath)==1 or \
        BaseFunctions.createDirectory(toPath+"\\Oscillation")==1 or \
        BaseFunctions.createDirectory(toPath+"\\Steady_State")==1 or \
            BaseFunctions.createDirectory(toPath+"\\Others")==1:
        return 1


    rr.conservedMoietyAnalysis = False
    rr.clearModel()

    step=_step
    max=simulationTime/step
    
    #name of file
    nameDir=file[0:(len(file)-4)]
    rr.clearModel()

    try:
        rr.load(path+'\\'+file)
    except:
        shutil.move(path+'\\'+file, dirReject)
        print('To not analyze')
        return 1

    
    #original quantities of species
    originalQuantities=rr.model.getFloatingSpeciesAmounts()
    
    originalPath=toPath
    #files to memorize the results
    allResults=open(originalPath+"\\Results_Original.txt", "w")
    smallResults=open(originalPath+"\\Small_Results_Original.txt", "w")
        
    oldSimulations=np.array(np.zeros(rr.model.getNumFloatingSpecies()), dtype=int)
    stop=False
    steadyState=False

    start=-(step/points)
    i=0
    while(i<max and not stop):
        try:
            sim=rr.simulate(start+(step/points),start+step,points)
        except:
            #an error has occured during the simulation
            break

        if i==0:
            np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))

            np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',header=str(rr.timeCourseSelections))
            j=_interval
            while j<len(sim):
                np.savetxt(smallResults, [sim[j,:]], fmt='%.5f')
                j=j+_interval
        else:
            np.savetxt(allResults, sim, fmt='%.8f')

            j=0
            while j<len(sim):
                np.savetxt(smallResults, [sim[j,:]], fmt='%.5f')
                j=j+_interval*2
            

        #the behaviour of models is studying
        if start>time:
            first=sim[0,1:].round(decimals=5)
            last=sim[points-1,1:].round(decimals=5)

            j=0
            while j<len(last) and last[j]>=0:
                j=j+1
            if j<len(last):
                break
                
            if not (first==last).all():
                for j in range(np.shape(oldSimulations)[0]):
                    if (not (np.array(first, dtype=int)==np.array(last, dtype=int)).all()) and (np.array(last, dtype=int)==oldSimulations[j]).all():
                        toPath=toPath+"\\Oscillation"
                        stop=True
                        print("Oscillation")
                        break
            else:
                for j in range(points-1):
                    if not (sim[j,1:].round(decimals=5)==last).all():
                        stop=True
                        toPath=toPath+"\\Oscillation"
                        print("Oscillation")
                        break
                if not stop:
                    stop=True
                    steadyState=True
                    toPath=toPath+"\\Steady_State"
                    print("Steady state")

        oldSimulations = np.vstack((oldSimulations, np.array(sim[:,1:], dtype=int)))
        start=start+step
        i=i+1

    #if the behaviour of model is not identified
    if stop==False:
        print("Behaviour not known")
        toPath=toPath+"\\Others"

    allResults.close()
    smallResults.close()

    #creation of directory for store the results
    if BaseFunctions.createDirectory(toPath+'\\'+nameDir)==1 or \
        BaseFunctions.removeFile(toPath+"\\"+nameDir+'\\'+"Results_Original.txt")==1 or\
        BaseFunctions.removeFile(toPath+"\\"+nameDir+'\\'+"Small_Results_Original.txt")==1:
        #if an error has occured
        return 1 
            
    shutil.move(originalPath+"\\Results_Original.txt", toPath+"\\"+nameDir)
    shutil.move(originalPath+"\\Small_Results_Original.txt", toPath+"\\"+nameDir)

    toPath=toPath+"\\"+nameDir+'\\'


    #simulations with different quantities of species
    for i in range(rr.model.getNumFloatingSpecies()):
        for j in range(len(percent)):

            rr.resetAll()   
            #new quantity is setting
            rr.model.setFloatingSpeciesAmounts([i],[originalQuantities[i]+originalQuantities[i]*percent[j]/100])
                
            if not steadyState:
                #files to store the results
                allResults=open(toPath+"Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", "w")
                smallResults=open(toPath+"Small_Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", "w")
                try:
                    sim=rr.simulate(0, simulationTime, simulationTime*int(points/step))
        
                    np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))

                    np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',header=str(rr.timeCourseSelections))
                    k=_interval
                    while k<len(sim):
                        np.savetxt(smallResults, [sim[k,:]], fmt='%.5f')
                        k=k+_interval
                except:
                    print("Error")

                #files are closed
                allResults.close()   
                smallResults.close() 
            else:
                #simulation for models with steady state
                simulationSteps(rr, toPath, "Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", points)

            rr.resetAll()    
            #new quantity is setting
            rr.model.setFloatingSpeciesAmounts([i],[originalQuantities[i]-originalQuantities[i]*percent[j]/100])        

            if not steadyState:
                #files to store the results
                allResults=open(toPath+"Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", "w")
                smallResults=open(toPath+"Small_Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", "w")
                try:
                    sim=rr.simulate(0, simulationTime, simulationTime*int(points/step))
                    np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))
                    
                    np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',header=str(rr.timeCourseSelections))
                    k=_interval
                    while k<len(sim):
                        np.savetxt(smallResults, [sim[k,:]], fmt='%.5f')
                        k=k+_interval
                except:
                    print("Error")

                allResults.close()
                smallResults.close()
            else:
                simulationSteps(rr, toPath, "Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", points)


    


#To simulate a model using a fixed time
#It need the reference to libRoadRunner, path where save results, simulation time, 
#intervals to change quantities of species, number of point to generate into simulation
def simulateWithTime(rr, nameDir, simulationTime, toPath, percent, points):

    if BaseFunctions.createDirectory(toPath+"\\"+nameDir)==1:
        #an error has occured
        return
    
    path=toPath+"\\"+nameDir+"\\"

    originalQuantities=rr.model.getFloatingSpeciesAmounts()

    allResults=open(path+"Results_Original.txt", "w")
    smallResults=open(path+"Small_Results_Original.txt", "w")
        
    try:
        sim=rr.simulate(0,simulationTime, points)
        np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))

        np.savetxt(smallResults, [sim[0,:]], fmt='%.5f', header=str(rr.timeCourseSelections))
        i=_interval
        while i<len(sim):
            np.savetxt(smallResults, [sim[i,:]], fmt='%.5f')
            i=i+_interval
    except:
        print("Error")

    allResults.close()
    smallResults.close()

    for i in range(rr.model.getNumFloatingSpecies()):
      
        for j in range(len(percent)):

            rr.resetAll()    
            
            rr.model.setFloatingSpeciesAmounts([i], [originalQuantities[i]+originalQuantities[i]*percent[j]/100])

            allResults=open(path+"Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", "w")
            smallResults=open(path+"Small_Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", "w")

            try:
                sim=rr.simulate(0,simulationTime, points)
                np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))

                np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',header=str(rr.timeCourseSelections))
                k=_interval
                while k<len(sim):
                    np.savetxt(smallResults, [sim[k,:]], fmt='%.5f')
                    k=k+_interval
            except:
                print("Error")

            allResults.close()
            smallResults.close()

            rr.resetAll()    
            
            rr.model.setFloatingSpeciesAmounts([i], [originalQuantities[i]-originalQuantities[i]*percent[j]/100])        

            allResults=open(path+"Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", "w")
            smallResults=open(path+"Small_Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", "w")

            try:
                sim=rr.simulate(0,simulationTime, points)
                np.savetxt(allResults, sim, fmt='%.8f',\
                    header=str(rr.timeCourseSelections))

                np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',\
                    header=str(rr.timeCourseSelections))
                k=_interval
                while k<len(sim):
                    np.savetxt(smallResults, [sim[k,:]], fmt='%.5f')
                    k=k+_interval
            except:
                print("Error")

            allResults.close()
            smallResults.close()





#To simulate a model with steady state using a specific configuration
#It need the reference to libRoadRunner, path where save results, file's name with model, 
#intervals to change quantities of species, values at steady state (optional)
def simulationSteps(rr, path, nameFile, points, values=[]):
    
    #check if there are negative values. In this case they cannot be used
    if values!=[]:
        for i in range(len(values)):
            values[i]="{0:.5f}".format(values[i])
        i=0
        while(i<len(values) and values[i]>=0):
            i=i+1
        if i<len(values):
            values=[]
            print('Error: negative values')
            rr.conservedMoietyAnalysis = False

    
    results=np.array(np.ones(len(values))*-1)
       
    allResults=open(path+nameFile, "w")
    smallResults=open(path+"Small_"+nameFile, "w")

    step=_step
    start=-(step/points)

    stop=False
    
    while((not (values==results).all() or values==[])  and not stop):
        try:
            sim=rr.simulate(start+(step/points),start+step,points)
        except:
            #an error has occured
            allResults.close()
            smallResults.close()
            break

        if start==-(step/points):
            np.savetxt(allResults, sim, fmt='%.8f',header=str(rr.timeCourseSelections))

            np.savetxt(smallResults, [sim[0,:]], fmt='%.5f',header=str(rr.timeCourseSelections))
            i=_interval
            while i<len(sim):
                np.savetxt(smallResults, [sim[i,:]], fmt='%.5f')
                i=i+_interval
                
        else:
            np.savetxt(allResults, sim, fmt='%.8f')

            i=0
            while i<len(sim):
                np.savetxt(smallResults, [sim[i,:]], fmt='%.5f')
                i=i+_interval*2
                
        #if we have information about quantities at steady state
        if values!=[]:
            results=sim[points-1,1:]
            for i in range(len(results)):
                results[i]="{0:.5f}".format(results[i])
        #if we have no information about quantities at steady state
        else:

            first=sim[0,1:].round(decimals=5)
            last=sim[points-1,1:].round(decimals=5)
            
            if (first==last).all():
                stop=True
                for i in range(points-1):
                    if not ((sim[i,1:].round(decimals=5)==last).all()):
                        stop=False

            i=0
            while(i<len(values) and last[i]>=0):
                i=i+1
            if i<len(values):
                #found negative values into simulation
                break

        start=start+step
            
    allResults.close()
    smallResults.close()




#simulation for models that have a steady state
#It need the reference to libRoadRunner, path where save results and where find model, file's name with model, 
#intervals to change quantities of species, number of points generate during simulation
def simulationWithSteadyState(rr, percent, dirResults, dirToExamine, file, points=_points):
    
    nameDir=file[0:(len(file)-4)]

    if BaseFunctions.createDirectory(dirResults)==1 or BaseFunctions.createDirectory(dirResults+"\\"+nameDir)==1:
        #an error has occured
        return

    path=dirResults+"\\"+nameDir+"\\"

    try:
        rr.load(dirToExamine+'\\'+file)
    except:
        print('Error')
        return

    originalQuantities=rr.model.getFloatingSpeciesAmounts()
    
    withValues=True
    values=[]

    try:
        rr.conservedMoietyAnalysis = True
    except:
        withValues=False
        print('Error during studying of steady state')

    if withValues:
        try:
            #to calculate values at steady state. It can be return values
            #also for models that show oscillations
            values=rr.getSteadyStateValues()
            rr.resetAll()
        except:
            #an error has occured 
            print('Error during studying of steady state')
            withValues=False
            rr.conservedMoietyAnalysis = False
    
    simulationSteps(rr, path, "Results_Original.txt", points, values)
    
    for i in range(rr.model.getNumFloatingSpecies()):

            for j in range(len(percent)):

                rr.resetAll()   
                values=[]

                if withValues:
                    try:
                        rr.conservedMoietyAnalysis = True
                        rr.model.setFloatingSpeciesAmounts([i],[originalQuantities[i]+originalQuantities[i]*percent[j]/100])
                        values=rr.getSteadyStateValues()
                        rr.resetAll()   
                    except:
                        print('Error during studying of steady state')

                rr.model.setFloatingSpeciesAmounts([i],[originalQuantities[i]+originalQuantities[i]*percent[j]/100])
                simulationSteps(rr, path, "Results_species_"+str(i+1)+"_plus_"+str(percent[j])+"_p.txt", points, values)

                rr.resetAll()    
                values=[]
                    
                if withValues:
                    try:
                        rr.conservedMoietyAnalysis = True
                        rr.model.setFloatingSpeciesAmounts([i], [originalQuantities[i]-originalQuantities[i]*percent[j]/100])        
                        values=rr.getSteadyStateValues()
                        rr.resetAll()   
                    except:
                        print('Error during studying of steady state')
                
                rr.model.setFloatingSpeciesAmounts([i], [originalQuantities[i]-originalQuantities[i]*percent[j]/100])        
                simulationSteps(rr, path, "Results_species_"+str(i+1)+"_minus_"+str(percent[j])+"_p.txt", points, values)
    
    rr.conservedMoietyAnalysis = False




#in this function, kinetic law of reactions are analyzed. The aim is 
#say if the model is described using mass-action law.
#this method needs the reference to libRoadRunner where model is load
def toSimulate(rr):
    
    model = libsbml.SBMLReader().readSBMLFromString(rr.getSBML()).getModel()

    #in every reaction check if number of modifiers is different from 0
    for i in range(model.getNumReactions()):
        #if there is a modifier mass.action law is not used
        if model.getReaction(i).getNumModifiers()>0:
            return 1 
    
    #to create a list with Id of user's functions
    nameFunctions=[f.getId() for f in model.getListOfFunctionDefinitions()]

    #check on kinetic law
    for i in range(model.getNumReactions()):
        l=model.getListOfReactions().get(i).getKineticLaw().getMath().getListOfNodes()
        #we look for operations different from -, *, ^
        for j in range(l.getSize()):
            if l.get(j).isOperator() and l.get(j).getOperatorName()!="minus" and l.get(j).getOperatorName()!="times" and l.get(j).getOperatorName()!="power":
                return 1 
            if l.get(j).isFunction() and l.get(j).getName() not in nameFunctions and l.get(j).getName()!="minus" and l.get(j).getName()!="times" and l.get(j).getName()!="power":
                return 1
    
    #check on user's functions
    for i in range(model.getNumFunctionDefinitions()):
        l=model.getFunctionDefinition(i).getBody().getListOfNodes()
        #we look for operations different from -, *, ^
        for j in range(l.getSize()):
            if l.get(j).isOperator() and l.get(j).getOperatorName()!="minus" and l.get(j).getOperatorName()!="times" and l.get(j).getOperatorName()!="power":
                return 1 
            if l.get(j).isFunction() and l.get(j).getName() not in nameFunctions and l.get(j).getName()!="minus" and l.get(j).getName()!="times" and l.get(j).getName()!="power":
                return 1

    return 0