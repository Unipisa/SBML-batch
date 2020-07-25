from setuptools import setup, find_packages
 
setup(name='SBML_batch',
      version='0.1',
      url='http://groups.di.unipi.it/msvbio/software/SBML_batch_simulator.html',
      license='LICENSE.txt', #Apache License 2.0
      author='Mariagiovanna Rotundo',
      author_email='mariagiovannarotundo@gmail.com',
      description='A python package for batch simulation of models ',
      packages=find_packages(), 
      long_description=open('README.md').read(),
      install_requires=['libroadrunner>=1.5.4', 'libsbml>=5.18.0', 'numpy', 'pathlib']
      )
      
      
      #is a list of all Python import packages that should be included in the distribution package. 
      #Instead of listing each package manually, we can use find_packages() to automatically discover 
      #all packages and subpackages
      #pathlib is built in from python's version 3.4 but it can be used on python 2.7 (also libroadrunner)