import roadrunner
import libsbml
import os
from SBML_batch import BaseFunctions


#to create Petri nets of a set of models
#in input it takes reference to roadrunner, path of directory that contains the files, path
#of directory that will contain the new files, number of test to classify a modifier, value of increase of quantities
def createPetriNets(rr, path, pathResult, nTest, valueIncrease):
    files=os.listdir(path)
    for file in files:
        if file.endswith('.xml'):
            print(file)
            #to create a Petri net
            createOnePetriNet(rr, path, file, pathResult, nTest, valueIncrease)


#to create the Petri Net of model 
#in input it takes reference to roadrunner, path of directory that contains the file, file's name, path
#of directory that will contain the new file, number of test to classify a modifier, value of increase of quantities
#It returns 1 if an error occurs, 0 otherwise
def createOnePetriNet(rr, path, file, pathResult, nTest, valueIncrease):
    
    if BaseFunctions.createDirectory(pathResult)==1:
        return 1
    
    #it clears the currently loaded model and all associated memory
    rr.clearModel()

    path=path+"\\"

    try:
        #to load the file with roadrunner
        rr.load(path+file)
    except:
        print("An error occurs during file load")
        return 1

    #to get the model using libSBML
    model = libsbml.SBMLReader().readSBMLFromString(rr.getSBML()).getModel()

    nameFile=file[0:(len(file)-4)]
    try:
        f=open(pathResult+"\\"+nameFile+".gv", "w")
    except IOError:
        print("An error occurs during opening file")
        return 1

    #string that will contains petri net of model
    graph='digraph "'+str(file)+'"{\n'

    #to create a node for each specie
    for i in range(model.getNumSpecies()):
        graph=graph+str(model.getSpecies(i).getId())+" [shape=circle];\n"
    
    #to examine one reaction at a time
    for i in range(model.getNumReactions()):

        #to create a box (node) for each reaction
        graph=graph+str(model.getListOfReactions().get(i).getId())+" [shape=box];\n"

        #to get reaction's reactants
        for reactant in model.getReaction(i).getListOfReactants():
            graph=graph+str(reactant.getSpecies())+" -> "+str(model.getReaction(i).getId())+" [arrowhead=vee, label="+str(reactant.getStoichiometry())+"];\n"
        
        #to get reaction's products
        for product in model.getListOfReactions().get(i).getListOfProducts():
            graph=graph+str(model.getReaction(i).getId())+" -> "+str(product.getSpecies())+" [arrowhead=vee, label="+str(product.getStoichiometry())+"];\n"

        #to get reaction's modifiers and establish if they are promoter or inhibitor
        for j in range(model.getReaction(i).getNumModifiers()):
            response=functionality(rr, model, j, i, nTest, valueIncrease)
            #if it's a promoter
            if response==1:
                graph=graph+str(model.getReaction(i).getModifier(j).getSpecies())+" -> "+str(model.getReaction(i).getId())+" [arrowhead=dot];\n"
            #if it's a inhibitor
            elif response==0:
                graph=graph+str(model.getReaction(i).getModifier(j).getSpecies())+" -> "+str(model.getReaction(i).getId())+" [arrowhead=tee];\n"    

        #if there is the inverse reaction
        if model.getReaction(i).getReversible():
            #to create a box (node) for the inverse reaction
            graph=graph+str(model.getReaction(i).getId())+"_Reverse [shape=box];\n"

            #to get inverse reaction's reactants
            for reactant in model.getListOfReactions().get(i).getListOfReactants():
                graph=graph+str(model.getListOfReactions().get(i).getId())+"_Reverse -> "+str(reactant.getSpecies())+" [arrowhead=vee, label="+str(reactant.getStoichiometry())+"];\n"

            #to get inverse reaction's products
            for product in model.getListOfReactions().get(i).getListOfProducts():
                graph=graph+str(product.getSpecies())+" -> "+str(model.getListOfReactions().get(i).getId())+"_Reverse [arrowhead=vee, label="+str(product.getStoichiometry())+"];\n"

    graph=graph+"}"
    
    try:
        f.write(graph)
    finally:
        try:
            f.close()
        except IOError:
            return 1
    

    return 0





#in input it takes reference to roadrunner, reference to model ceate using libsbml, number of specie modifiers,
#number of reaction, number of test to do, value of increase of quantities.
#output: if it's an inhibitor it returns 0, if promoter 1, if it fails to establish the role -1, if the species it's not
#in law -2
def functionality(rr, model, specie, reaction, nTest, valueIncrease):

    i=0
    while i<model.getReaction(reaction).getKineticLaw().getMath().getListOfNodes().getSize() and \
        model.getReaction(reaction).getModifier(specie).getSpecies()!=model.getReaction(reaction).getKineticLaw().getMath().getListOfNodes().get(i).getName():
        i=i+1

    #check if the species it's not in law
    if i==model.getReaction(reaction).getKineticLaw().getMath().getListOfNodes().getSize():
        return -2


    #original quantities of species
    originalQuantities=rr.model.getFloatingSpeciesAmounts()
    
    
    
    #use a time which is not 0
    rr.model.setTime(0.1)
    
    #analyze the role of modifier
    role=analysis(rr, model, specie, reaction, nTest, originalQuantities, valueIncrease)

    #reset the original quantities of species
    rr.model.setFloatingSpeciesAmounts(originalQuantities)

    # if the role of modifier is known, it returns the corresponding code
    if role==0 or role==1:
        return role
        
    
    
    #to try the role changing the quantities of molecules
    #before there is a less change then a major change 
    for j in range(nTest):
        quantities=originalQuantities.copy()
        
        for i in range(0,len(quantities)):
            quantities[i]=quantities[i]+0.1+j
            rr.model.setFloatingSpeciesAmounts([i],[quantities[i]])
            
            #quantities are not changed if the change produce a negative rate
            if rr.model.getReactionRates()[reaction]<0:
                quantities[i]=quantities[i]-0.1-j
                rr.model.setFloatingSpeciesAmounts([i],[quantities[i]])
            

        if rr.model.getReactionRates()[reaction]<0:
            rr.model.setFloatingSpeciesAmounts(originalQuantities)
            continue

        #analyze the role of modifier and reset the original quantities of species
        role=analysis(rr, model, specie, reaction, nTest, quantities, valueIncrease)
        rr.model.setFloatingSpeciesAmounts(originalQuantities)

        #if the role of modifier is known, it returns the corresponding code
        if role==0 or role==1:
            return role

    #if the role of modifier is not known
    return -1
    


#to establish the role of a modifier having a fixed configuration 
#in input it takes reference to roadrunner, reference to model ceate using libsbml, number of specie modifiers,
#number of reaction, number of test to do, vector with quantities of species, value of increase of quantities.
#it returns 1 if it's a promoter, 0 if it's an inhibitor, -1 if don't known
def analysis(rr, model, specie, reaction, nTest, quantities, valueIncrease):
    
    #index of specie to examine
    index=rr.model.getFloatingSpeciesIds().index(model.getReaction(reaction).getModifier(specie).getSpecies())

    #original rates of sistem
    originalRate=rr.model.getReactionRates()[reaction]

    countProm=0
    countInhib=0

    #execute the specified number of tests 
    for i in range(1, nTest+1):
        #increase the quantity of specie to examine
        rr.model.setFloatingSpeciesAmounts([index],[quantities[index]+quantities[index]*(i*valueIncrease)/100])
        
        #if rates increase
        if rr.model.getReactionRates()[reaction]>originalRate:
            countProm=countProm+1
        #if rates decrease
        elif rr.model.getReactionRates()[reaction]<originalRate:
            countInhib=countInhib+1

        originalRate=rr.model.getReactionRates()[reaction]

    #if rates decrease in every test it's a inhibitor
    if countInhib==nTest:
        return 0
    #if rates increase in every test it's a promoter
    elif countProm==nTest:
        return 1


    #using a major increase of quantity
    rr.model.setFloatingSpeciesAmounts(quantities)

    originalRate=rr.model.getReactionRates()[reaction]
    countProm=0
    countInhib=0

    for i in range(1, nTest+1):
        rr.model.setFloatingSpeciesAmounts([index],[quantities[index]*i*valueIncrease])

        if rr.model.getReactionRates()[reaction]>originalRate:
            countProm=countProm+1
        elif rr.model.getReactionRates()[reaction]<originalRate:
            countInhib=countInhib+1

        originalRate=rr.model.getReactionRates()[reaction]

    if countInhib==nTest:
        return 0
    elif countProm==nTest:
        return 1
    
    #if the role is not known return -1
    return -1