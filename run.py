import sys
import os
import defaults
from inputHandler import Input
from system import System
from settings import Settings
from logger import Logger
from prepare import Preparation
from errors import *
from prepare import Preparation

def actionPrepare():
  Preparation.setUp()
  for target in Settings.targets:
    for platform in Settings.targetPlatforms:
      for cpu in Settings.targetCPUs:
        for configuration in Settings.targetConfigurations:
          Preparation.run()

def actionBuild():
  for target in Settings.targets:
    for platform in Settings.targetPlatforms:
      for cpu in Settings.targetCPUs:
        for configuration in Settings.targetConfigurations:
          pass

def actionCreateNuget():
  pass

def actionPublishNuget():
  pass

def actionUpdatePublishedSample():
  pass

def main():

  #Check if required tools are installed
  errorCode = System.checkTools()
  if errorCode != 0:
    System.stopExecution(errorCode)

  #Determine host OS, checks supported targets, create userdef.py file if missing
  System.preInit()
  Settings.preInit()

  #Parse input parameters if any
  Input.parseInput(sys.argv[1:])

  #Load settings
  System.setUp()
  
  mainLogger = Logger.getLogger("Main")
  mainLogger.info('Checks are passes')


  


  #Import template file
  #exec 'from %s import *'%(defaults.currentTemplateFile)
  
  #Options
  #1. Import file dynamicaly like above
  #2. DEfault should be class which will be inherited by template, and using same logic like above it should import Template class
  #2. Create CurrentSetting.py file with init function where all gloabla variable has global decoration, and then append to file default settings and template
  #3. Use simple-settings 
  # https://martin-thoma.com/configuration-files-in-python/
  # https://hackernoon.com/4-ways-to-manage-the-configuration-in-python-4623049e841b
  
  print(Settings.testValue)
  mainLogger.warning(str(Settings.targets))
  #attrs = vars(Settings)
  #print ('\n '.join("%s: %s" % item for item in attrs.items()))
  
  #for attr in dir(Settings):
  #  print("Settings.%s = %r" % (attr, getattr(Settings, attr)))
  
  if not System.checkIfTargetsAreSupported(Settings.targets):
    System.stopExecution('Target is not supported')
  
  if not System.checkIfPlatformsAreSupported(Settings.targetPlatforms):
    System.stopExecution('Platform from the list ' + str(Settings.targetPlatforms) + ' is not supported',1)
    #System.stopExecution('Platform is not supported')

  

  #Start performing actions. Actions has to be executed in right order and that is the reason why it is handled this way
  if 'prepare' in Settings.actions:
    actionPrepare()

  if 'build' in Settings.actions:
    actionBuild

  if 'createNuget' in Settings.actions:
    actionCreateNuget()

  if 'publishNuget' in Settings.actions:
    actionPublishNuget()

  if 'updatePublishedSample' in Settings.actions:
    actionUpdatePublishedSample()


if  __name__ =='__main__':main()
