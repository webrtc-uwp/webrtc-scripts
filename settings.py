import os
import defaults
from defaults import *
from importlib import import_module


class Settings:

  inputArgs = None
  @classmethod
  def preInit(cls):
    
    #Determine verious paths of interest

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

    """
    cls.webrtcTemplateFile = webrtcTemplateFile
    #Import webrtcTemplateFile template if provided
    if webrtcTemplateFile != "" and os.path.isfile(webrtcTemplateFile + ".py"):
      globals().update(import_module(webrtcTemplateFile).__dict__)

    cls.ortcTemplateFile = ortcTemplateFile
    #Import ortcTemplateFile template if provided
    if ortcTemplateFile != "" and os.path.isfile(ortcTemplateFile + ".py"):
      globals().update(import_module(ortcTemplateFile).__dict__)

    """
    
    #Import custom template if provided
    if cls.inputArgs.template:
      print('samo sto nije')
      print(cls.inputArgs.template)
      print(os.path.join(cls.rootScriptsPath,defaults.templatesPath, cls.inputArgs.template + '.py'))
      if cls.inputArgs.template and (os.path.isfile(cls.inputArgs.template) or os.path.isfile(cls.inputArgs.template + ".py") or os.path.isfile(os.path.join(cls.rootScriptsPath,defaults.templatesPath, cls.inputArgs.template + '.py'))): 
        print(cls.inputArgs.template)
        globals().update(import_module(cls.inputArgs.template).__dict__)

    #cls.currentTemplateFile = currentTemplateFile
    #cls.templatesPath = templatesPath

    cls.testValue = testValue

    cls.runPrepare = runPrepare
    cls.runBuild = runBuild
    cls.createNuget = createNuget

    cls.supportedPlatformsForHostOs = supportedPlatformsForHostOs

    if cls.inputArgs.targets:
      cls.targets = cls.inputArgs.targets
    else:
      cls.targets = targets
    cls.targetCPUs = targetCPUs
    cls.targetPlatforms = targetPlatforms
    cls.targetConfigurations = targetConfigurations

    cls.actions = actions
    cls.logFormat = logFormat
    cls.logLevel = logLevel
    cls.logToFile = logToFile
    cls.overwriteLogFile = overwriteLogFile

    cls.showTraceOnError = showTraceOnError
    cls.showSettingsValuesOnError = showSettingsValuesOnError
    
    @classmethod
    def owerwriteWithInputArgs(cls):
      if Input.args.targets:
        cls.targets =  Input.args.targets
