import os
from importlib import import_module

import config
import defaults
from defaults import *
from helper import convertToPlatformPath


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
    cls.userDefFilePath = os.path.join(cls.userWorkingPath, config.USER_DEFAULTS_FILE + '.py')
    #Scripts root path
    cls.rootScriptsPath = os.path.dirname(defaults.__file__)
    #Predefined templates path
    cls.templatesPath = os.path.join(cls.rootScriptsPath, convertToPlatformPath(config.TEMPLATES_PATH))
    #Sdk root path
    cls.rootSdkPath = os.path.join(cls.rootScriptsPath, '..')
    #Local depot tools path
    cls.localDepotToolsPath = os.path.join(Settings.rootSdkPath, convertToPlatformPath(config.RELATIVE_DEPOT_TOOLS_PATH))
    #Local buildtools path
    #TODO: Make platform dependent - check host os and add proper subfolder name
    cls.localBuildToolsPath = os.path.join(Settings.rootSdkPath, convertToPlatformPath(config.RELATIVE_BUILD_TOOLS_PATH),'win')
    #defaults.py path
    cls.defaultFilePath = os.path.join(os.path.dirname(defaults.__file__),'defaults.py')

  @classmethod
  def init(cls):

    #First import userdef.py created from defaults.py
    if os.path.isfile( cls.userDefFilePath):
      globals().update(import_module(config.USER_DEFAULTS_FILE).__dict__)
    
    #Import custom template if provided
    if cls.inputArgs.template:
      if cls.inputArgs.template and \
         (os.path.isfile(cls.inputArgs.template) or 
          os.path.isfile(cls.inputArgs.template + '.py') or 
          os.path.isfile(os.path.join(cls.templatesPath, cls.inputArgs.template + '.py'))): 
        globals().update(import_module(cls.inputArgs.template).__dict__)

    cls.supportedPlatformsForHostOs = supportedPlatformsForHostOs
    cls.supportedCPUsForPlatform = supportedCPUsForPlatform

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
    cls.showPATHOnError = showPATHOnError

    cls.webRTCGnArgsTemplatePath = webRTCGnArgsTemplatePath
