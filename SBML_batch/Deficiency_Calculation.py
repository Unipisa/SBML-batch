import numpy as np
import libsbml
import collections as cl
    

def recursive_visit(rr, indexRoot, explored, reachables, adjacency_list):
    explored.append(indexRoot)
        
    for i in range(len(adjacency_list[indexRoot])):
        
        #add the successor to list
        reachables[indexRoot]=np.concatenate((reachables[indexRoot], [adjacency_list[indexRoot][i]]))

        #if the nodes was not explored, explore it
        if adjacency_list[indexRoot][i] not in explored:
            recursive_visit(rr, adjacency_list[indexRoot][i], explored, reachables, adjacency_list)
            
        #add the successor of the new node to the list
        reachables[indexRoot]=list(dict.fromkeys(np.concatenate((reachables[indexRoot], reachables[adjacency_list[indexRoot][i]]))))
                        

                        

#for study a model with Feinberg's theorems. It returns a list with deficiency of the network 
#and 0/1 for the properties of reversibility or weakly reversibility.
#0 if one of these properties is verified, 1 if these are not verified
#in input it takes a reference to library libRoadRunner where the model
#is alredy load
def deficiency_calculation(rr):
    #creation of adjacency lists
    adjacency_list=[]
    
    #creation of array to remember node's names
    nodes=[]

    model = libsbml.SBMLReader().readSBMLFromString(rr.getSBML()).getModel()

    #analyze all reaction
    for i in range(model.getNumReactions()):
     
        #create the node with reactants 
        nodeReactant=[]
        for r in model.getListOfReactions().get(i).getListOfReactants():
            nodeReactant.append(str(r.getStoichiometry())+str(r.getSpecies()))
        if len(nodeReactant)==0:
            nodeReactant.append("0")
        else:
            nodeReactant.sort()

        #create the node with products 
        nodeProduct=[]
        for p in model.getListOfReactions().get(i).getListOfProducts():
            nodeProduct.append(str(p.getStoichiometry())+str(p.getSpecies()))
        if len(nodeProduct)==0:
            nodeProduct.append("0")
        else:
            nodeProduct.sort()

    
        #check if the node was already seen
        indexNodeReactant=-1
        j=0
        while indexNodeReactant==-1 and j<len(nodes):
            #if the node is found in the list
            if nodeReactant==nodes[j]:
                indexNodeReactant=j
            else:
                j=j+1


        #if the nodes was not seen before
        if indexNodeReactant==-1:
            #add the node to list 'nodes' and the adjacency list to the set 
            nodes.append(nodeReactant) 
            adjacency_list.append([])
            indexNodeReactant=nodes.index(nodeReactant)
        
            
        indexNodeProduct=-1
        j=0
        while indexNodeProduct==-1 and j<len(nodes):
            if nodeProduct==nodes[j]:
                indexNodeProduct=j
            else:
                j=j+1

        if indexNodeProduct==-1:
            nodes.append(nodeProduct)
            adjacency_list.append([])
            indexNodeProduct=nodes.index(nodeProduct)

        adjacency_list[indexNodeReactant].append(indexNodeProduct)

        #check if the reaction is reversible
        if model.getListOfReactions().get(i).getReversible():
            #add to the list the corrisponding reaction
            adjacency_list[indexNodeProduct].append(indexNodeReactant)


    """
    print(adjacency_list)
    print(nodes)
    """
    
  
    #list that contains the indexes of reactions
    indexes=list(range(np.shape(adjacency_list)[0]))
    #to count number of linkage classes
    numLinkageC=0
    last=-1
    j=0
    while j<len(adjacency_list) and last<len(adjacency_list)-1:
        #if the reaction is not in a linkage class already seen
        if last<j:
            numLinkageC=numLinkageC+1
            last=last+1
        i=0
        while i<len(adjacency_list[indexes[j]]) and last<len(adjacency_list)-1:
            if indexes.index(adjacency_list[indexes[j]][i])>last:
                last=last+1
                pos=indexes.index(adjacency_list[indexes[j]][i])
                tmp=indexes[last]
                indexes[last]= indexes[pos]
                indexes[pos]=tmp
            i=i+1
        i=last+1
        while i<len(adjacency_list) and last<len(adjacency_list)-1:
            if indexes[j] in adjacency_list[indexes[i]]:
                last=last+1
                tmp=indexes[last]
                indexes[last]= indexes[i]
                indexes[i]=tmp
            i=i+1
        j=j+1



    #creation of a matrix of zeros
    stochiometricMatrix=np.zeros((rr.model.getNumReactions(), rr.model.getNumFloatingSpecies()))
    #every reaction is analyzed
    for i in range(model.getNumReactions()):
        #array of node of reactants
        vReactant=np.zeros(rr.model.getNumFloatingSpecies())
        #creation of the array
        for r in model.getListOfReactions().get(i).getListOfReactants():
            vReactant[rr.model.getFloatingSpeciesIds().index(r.getSpecies())]=r.getStoichiometry()
        #array of node of products
        vProduct=np.zeros(rr.model.getNumFloatingSpecies())
        #creation of the array
        for r in model.getListOfReactions().get(i).getListOfProducts():
            vProduct[rr.model.getFloatingSpeciesIds().index(r.getSpecies())]=r.getStoichiometry()
        
        #creation of the stochiometric matrix
        for j in range(rr.model.getNumFloatingSpecies()):
            stochiometricMatrix[i][j]=vProduct[j]-vReactant[j]
      
    """
    print(rr.model.getFloatingSpeciesIds())
    for i in range(np.shape(stochiometricMatrix)[0]):
        for w in range(np.shape(stochiometricMatrix)[1]):
            print(str(stochiometricMatrix[i][w])+'\t', end="")
        print()
    """


    #to calculate the rank of the stochiometric matrix
    rank=np.linalg.matrix_rank(stochiometricMatrix)

    #to calculate the deficiency
    deficiency=len(nodes)-numLinkageC-rank

    print("Number of Nodes : "+ str(len(nodes)))
    print("Number of linkage classes : " + str(numLinkageC))
    print("Rank of the matrix : "+ str(rank))
    print("Deficiency : "+ str(deficiency))


    #reversibility and weakly reversibility

    #check if the network is reversible
    allReversible=True
    for reaction in model.getListOfReactions():
        if reaction.getReversible()==False:
            allReversible=False
            break

    #if the nwtwork is not reversible
    if not allReversible:
    
        #the graph is explored for create lists of reachables nodes

        #is the list of the explored nodes
        explored=[]
        #list of reachables nodes
        reachables=[]
        for i in range(np.shape(adjacency_list)[0]):
            reachables.append([])
        
        i=0
        while len(explored)<np.shape(adjacency_list)[0]:
            #if the node was not explored before 
            if i not in explored:
                recursive_visit(rr, i, explored, reachables, adjacency_list)
            i=i+1
           
        
        #to update the reachables lists
        for i in range(len(explored)):
            j=0
            while j <len(reachables[explored[i]]):
                if reachables[explored[i]][j]!=explored[i]:
                    reachables[explored[i]]=np.concatenate((reachables[explored[i]], reachables[int(reachables[explored[i]][j])]))
                    #to delete the duplicates from the lists
                    reachables[explored[i]] = list(cl.OrderedDict.fromkeys(reachables[explored[i]]))
                j=j+1


        #check if each node is in the lists of successors
        for i in range(np.shape(adjacency_list)[0]):
            for j in range(len(adjacency_list[i])):
                #if is not true, the network is not weakly reversible
                if i not in reachables[adjacency_list[i][j]]:
                    return [deficiency, 1]

    #0 because the network is reversible or weakly reversible
    return [deficiency, 0]
    