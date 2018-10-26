import os
from importlib import import_module

import defaults
from defaults import *


class Settings:
  """
   Interface to variables set in defaults.py, templates files or using sommand line.
  """

  showSettingsValuesOnError = False
  showTraceOnError = False
  inputArgs = None

  @classmethod
  def preInit(cls):
    """
      Determine verious paths of interest and creates userdef.py file, 
      in current working directory, with defaults value, if it is not 
      already created.
    """

    #User working directory
    cls.userWorkingPath = os.getcwd()
    #User defaults file path
    cls.userDefFilePath = os.path.join(cls.userWorkingPath, defaults.userDefaultsFile + '.py')
    #Scripts root path
    cls.rootScriptsPath = os.path.dirname(defaults.__file__)
    #Predefined templates path
    cls.templatesPath = os.path.join(cls.rootScriptsPath, defaults.templatesPath)
    #Sdk root path
    cls.rootSdkPath = os.path.join(cls.rootScriptsPath, '..')
    #Local depot tools path
    cls.localDepotToolsPath = os.path.join(Settings.rootSdkPath, Utility.convertToPlatformPath(defaults.relativeDepotToolsPath))
    #Local buildtools path
    cls.localBuildToolsPath = os.path.join(Settings.rootSdkPath, Utility.convertToPlatformPath(defaults.relativeBuildToolsPath),'win')

    #Checks if in user working directory exists files userdefs.py and if not creates it from default.py
    if not os.path.isfile(cls.userDefFilePath):
      defaultFilePath = os.path.join(os.path.dirname(defaults.__file__),'defaults.py')
      cls.defaultsFile = open(defaultFilePath, 'r')
      cls.userDefFile = open(cls.userDefFilePath, 'w')
      cls.userDefFile.write(cls.defaultsFile.read())
      cls.defaultsFile.close()
      cls.userDefFile.close()

  @classmethod
  def init(cls):

    #First import userdef.py created from defaults.py
    if os.path.isfile( cls.userDefFilePath):
      globals().update(import_module(defaults.userDefaultsFile).__dict__)
    
    #Import custom template if provided
    if cls.inputArgs.template:
      print(os.path.join(cls.rootScriptsPath,defaults.templatesPath, cls.inputArgs.template + '.py'))
      if cls.inputArgs.template and (os.path.isfile(cls.inputArgs.template) or os.path.isfile(cls.inputArgs.template + '.py') or os.path.isfile(os.path.join(cls.rootScriptsPath,defaults.templatesPath, cls.inputArgs.template + '.py'))): 
        globals().update(import_module(cls.inputArgs.template).__dict__)

    cls.testValue = testValue

    cls.runPrepare = runPrepare
    cls.runBuild = runBuild
    cls.createNuget = createNuget

    cls.supportedPlatformsForHostOs = supportedPlatformsForHostOs

    #If targets are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.targets:
      cls.targets = cls.inputArgs.targets
    else:
      cls.targets = targets

    #If platforms are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.platforms:
      cls.targetPlatforms = cls.inputArgs.platforms
    else:
      cls.targetPlatforms = targetPlatforms

    #If cpus are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.cpus:
      cls.targetCPUs = cls.inputArgs.cpus
    else:
      cls.targetCPUs = targetCPUs

    #If configurations are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.configurations:
      cls.targetConfigurations = cls.inputArgs.configurations
    else:
      cls.targetConfigurations = targetConfigurations

    cls.actions = actions
    cls.logFormat = logFormat
    cls.logLevel = logLevel
    cls.logToFile = logToFile
    cls.overwriteLogFile = overwriteLogFile

    cls.showTraceOnError = showTraceOnError
    cls.showSettingsValuesOnError = showSettingsValuesOnError
