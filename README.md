# SBML-batch



## 1. What is SBML-batch?
SBML-batch is a Python package to analyze and to simulate a set of Chemical Reaction Networks (CRNs). More specifically, this has 4 main functionalities:

1. It recognizes biological models with well-defined proprieties: models with rules or events, qualitative models, and models whose simulation will produce incorrect results;

2. It studies one or more biological models with Feinberg's Theorems: Deficiency Zero Theorem and Deficiency One Theorem. These theorems give us some information about dynamic proprieties of networks with no simulations;

3. It simulates one or more models using better management of simulation time trying to discover the behavior of the systems;

4. It creates Petri nets of one or more models studying their structure.



## 2. How to install SBML-batch
To install SBML-batch you need the following Python's libraries:
- **numpy**
- **pathlib** (not included in Python 3.3 or older)
- **libSBML** with a version 5.18.0 or higher
- **libRoadRunner** with a version 1.5.4 or higher

After installing the previous libraries, install SBML-batch:
`pip install SBML-batch`




## 3. How to use SBML-batch
The package has 6 Python's modules, each one with specific functionality:
- **Main**

  To use one or all the functionalities previously described;

- **BaseFunction**

  To manage files and directories;

- **SelectFiles**

  To select models from others with rules or events, qualitative models, and models whose simulation will produce incorrect results;

- **Deficiency Calculation**

  To calculate the deficiency of a CRN and to study its proprieties of reversibility and weakly reversibility;

- **Simulation** 

  To simulate a set of models and to study kinetic Laws in a model to understand if the model is studied with law of mass action;

- **PetriNets**

  To create Petri nets of one or more models.



### 3.a. Main
This is the main module and allows you to use all the main functionality just calling a method. In this module there are 2 functions:

1. **`main(interval=-1, maxInterval=20, dirToExamine="models", func=0)`**
    It takes 4 optional arguments. `interval` and `maxInterval` are used in case of simulations and determine number of initial configuration that will be simulated. `interval` represents the percentage that will be used to change the initial quantities of species until a maximum percentage represented from `maxInterval`. `dirToExamine` is the path of the directory where the program will search models to analyze. `func` is the functionality that the user wants to execute. It can take an integer value between 0 and 4 (included):
  - 0 - you execute all the main functionalities;
  - 1 - you select models from the others with rules or events, qualitative models, and models whose simulation will produce incorrect results;
  - 2 - you study models with Feinberg's Theorems;
  - 3 - you simulate models;
  - 4 - you create Petri nets that correspond to models.
    By default the arguments take the values in the signature, so calling `main()` is equivalent to call `main(-1, 20, "models", 0)`

2. **`analysisTheorems(rr, dirToExamine, dirNotAnalyze, dirToSimulation, dirTheorems)`**
    This function studies models with Feinberg's theorems. It takes 5 arguments:
  - `rr` is a reference to libRoadRunner;
  -  `dirToExamine` is the directory with models to analyze;
  -  `dirNotAnalyze` is the directory with models to not study;
  -  `dirToSimulation` is the directory with models that can't be analyzed with Feinberg's theorems but need to be simulated;
  -  `dirTheorems` is the directory with models studied with Feinberg's theorems.

An example of use of this module is the use of Feinberg's theorems:

`from SBML_batch import Main`
`Main.main(func=2)`



### 3.b. BaseFunction
This module has 4 functions:

1. **`createDirectoryExit(path)`** 

   To create the directory `path` and to stop the program if a failure occurs;

2. **`createDirectory(path)`** 

   It creates the directory `path` and **returns** 1 if a failure occurs and 0 otherwise. It doesn't stop the program;

3. **`removeFile(path)`** 

   It deletes the file `path` and **returns** 1 if a failure occurs and 0 otherwise;

4. **`numericalInput(outputString, allowValues)`**

   This method asks the user to insert an integer number. This shows the user the string in the variable `outputString`. If the number to insert can take a value in a set of values, you can indicate this set in `allowValues` using a list. If user inserts a not valid number, the program will be stopped, otherwise, this method returns the number inserted.



### 3.c. SelectFiles
This module has 2 functions:
1. **`select(rr, dirToExamine, dirNotAnalyze, others)`**
This is used to select models from the others with rules or events, qualitative models and models whose simulation will produce incorrect results.
It studies all models in the directory `dirToExamine` and it moves models with one of the proprieties previously nominated in the directory `dirNotAnalyze`. If in the directory there are files that are not models because they aren't XML files, these will be moved in the directory `others`. `rr` is a reference to libRoadRunner.

2. **`selectOneModel(rr, path, file)`**
    This method doesn't move models but studies one model and returns a numerical code that says if the model has one of the previous proprieties. It takes 3 arguments:
    
    - `rr` is a reference to libRoadRunner;
    - `path` is the path where the model is;
    - `file` is the name of the file to study.
    
    This method **returns**:
    
    - 0 if the model doesn't have these proprieties;
    - -1 if there is an error during load of the file so this can't be simulated or studied anymore;
    - 1 if the model has one of the proprieties;
    - 2 if `file` it's not an XML file.



### 3.d. Deficiency Calculation
This module is used to study a model with Feinberg's Theorems. To do this, it offers a method: **`deficiency_calculation(rr)`**. This method takes one argument, `rr`, that is a reference to libRoadRunner with loaded the model to analyze. It returns a list with 2 integer numbers. The first it's the deficiency of the Chemical Reaction Network, the second it's a number that can be 0 or 1: 1 if the network is not reversible and not weakly reversible, 0 otherwise.

An example of use of this method is the following, where you import the module, create the reference to libRoadRunner, load the file with the model that you want to study, and, in the end, you call the method.

`from SBML_batch import Deficiency_Calculation`
`import roadrunner`
`rr=roadrunner.RoadRunner()`
`rr.load("models\\BIOMD0000000006.xml")`
`results=Deficiency_Calculation.deficiency_calculation(rr)`



### 3.e. Simulation

This module has 6 methods:
1. **`toSimulate(rr)`** 
    It takes one only argument, `rr`, a reference to library libRoadRunner with loaded a model. This method tries to discover if the model is studied with law of mass action analyzing the kinetic law of the reactions of the biological system. This method **returns**:
    - 0 if the model is studied with law of mass action;
    
    - 1 if the model is not studied with law of mass action.
    
2. **`simulationWithSteadyState(rr, percent, dirResults, dirToExamine, file, points=_points)`** 
   To simulate a Chemical Reaction Network that we know it reaches steady state. It takes 5 arguments plus an optional one:
   - `rr` is a reference to libRoadRunner;
   - `percent` is an array with the percentages that will be used to change the initial quantities of species;
   - `dirResults` is the directory where the results will be saved;
   - `dirToExamine` is the directory with models to study;
   - `file` is the name of the file where the model is saved;
   - `points` is the number of points to generate during a simulation.
3. **`simulationSteps(rr, path, nameFile, points, values=[])`**
   It simulates a model with steady state using a specific configuration. It takes 4 arguments plus one optional argument: 
   - `rr`  is a reference to libRoadRunner;
   - `path` is the path where results of simulations will be saved;
   - `nameFile` is the name of the file where the model is saved;
   - `points` is the number of points to generate during a simulation;
   - `values` is an array with values of species at steady state.
4. **`simulateWithTime(rr, nameDir, simulationTime, toPath, percent, points)`**
   To study a Chemical Reaction Network using a fixed time for simulations. It takes 6 arguments:
   - `rr` is a reference to libRoadRunner with a file already loaded;
   - `nameDir` is the name of directory where results will be saved;
   - `simulationTime` is the time that will be used for simulations;
   - `toPath` is the path where create the directory `nameDir`;
   - `percent` is an array with the percentages that will be used to change the initial quantities of species;
   - `points` is the number of points to generate during a simulation. 
5. **`simulateAllModels(rr, dirToSimulation, toPath, dirReject, simulationTime, time, percent, points=_points)`**
   This method simulates all models in a specific directory and, during simulations, tries to recognize the behaviors of models. It takes 7 argument plus one optional argument: 
   - `rr` is a reference to libRoadRunner with a file already loaded;
   - `dirToSimulation` is the directory where models we want to study are;
   - `toPath` is the path of the directory where results of simulations will be saved;
   - `dirReject` is the directory where models to not analyze will be moved;
   - `simulationTime` is the maximum time of simulation to study behaviors of models;
   - `time` is the minimum time of simulation to study behaviors of models;
   - `percent` is an array with the percentages that will be used to change the initial quantities of species;
   - `points` is the number of points to generate during a simulation. 
6. **`simulateModel(rr, path, file, toPath, dirReject, simulationTime, time, percent, points=_points)`**
     This method takes one argument more than the previous one: `file`. Here, `path` is like `dirToSimulation` of the previous method and `file` is the name of file to study and to simulate.

An example of use of the method `toSimulate` is the following:

`from SBML_batch import Simulation`
`import roadrunner`
`rr=roadrunner.RoadRunner()`
`rr.load("models\\BIOMD0000000006.xml")`
`if Simulation.toSimulate(rr)==1:`
		`print("Model is not studied with law of mass action")`


An example of use of the method `simulateAllModels` is the following:

`from SBML_batch import Simulation`
`import roadrunner`
`rr=roadrunner.RoadRunner()`
`Simulation.simulateAllModels(rr, "models", "results", "notAnalyze", 3000, 0, [5, 10])`



### 3.f. PetriNets
Using this module you can study the role of a modifier in a reaction and create the Petri nets of one or more models.

1. **`functionality(rr, model, specie, reaction, nTest, valueIncrease)`**
   This method takes 6 arguments:

   - `rr` is a reference to libRoadRunner with a model loaded;
   - `model` is an object of type Model of the library libSBML;
   - `specie` is the number of modifiers in the reaction that you want to study;
   - `reaction` is the number of reactions in the model;
   - `nTest` is the number of tests that you want to execute to study the role of the modifiers;
   - `valueIncrease` is the value that will be used to increment quantities of species to study the role of modifier.

   This method **returns**:

   - 0 if the specie acts like an inhibitor;
   - 1 if it acts like a promoter;
   - -1 if it fails to establish the role;
   - -2 if the species it's not in the law of the studied reaction.

2. **`createPetriNets(rr, path, pathResult, nTest, valueIncrease)`**
    This method creates Petri nets of a set of models. It takes 5 arguments:
    
    - `rr` is a reference to libRoadRunner;
    - `path` is the directory with the set of models;
    - `pathResult` is the directory where Petri nets will be saved;
- `nTest` and `valueIncrease`, because this method calls the method `functionality`.
    
3. **`createOnePetriNet(rr, path, file, pathResult, nTest, valueIncrease)`**
    This method creates Petri net of one model. It takes one more argument than the previous one: `file`, that represents file of which will be created the Petri net.

An example of use of the method `createPetriNets` is the following:

`from SBML_batch import PetriNets`
`import roadrunner`
`rr=roadrunner.RoadRunner()`
`PetriNets.createPetriNets(rr, 'Simulate_Models', 'PetriNets', 10, 5)`



## 4. License

This package is licensed under Apache License 2.0. Please see file LICENSE.txt for more information about it.