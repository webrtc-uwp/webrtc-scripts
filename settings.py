import os
from importlib import import_module

import config
from defaults import *
from helper import convertToPlatformPath,iterateDict

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
    cls.rootScriptsPath = os.path.dirname(__file__)
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
    cls.defaultFilePath = os.path.join(os.path.dirname(__file__),'defaults.py')
    #Root path for preparation
    cls.webrtcPath = os.path.join(cls.rootSdkPath, convertToPlatformPath(config.PREPRATARION_WORKING_PATH))
    #WebRtc solution path
    cls.webrtcSolutionPaths = os.path.join(cls.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_PATH))

    #local ninja path
    cls.localNinjaPath = os.path.join(cls.localDepotToolsPath,'ninja')

  @classmethod
  def init(cls):
    """
      Based on userdef.py or specified input tamplate and input arguments sets script variables.
    """
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

    #cls.gnOutputPath = gnOutputPath

    cls.supportedPlatformsForHostOs = supportedPlatformsForHostOs
    cls.supportedCPUsForPlatform = supportedCPUsForPlatform

    if cls.inputArgs.actions:
      cls.actions = cls.inputArgs.actions
    else:
      cls.actions = actions

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

    cls.targetProgrammingLanguage = targetProgrammingLanguage
    #cls.buildWithClang = buildWithClang

    if cls.inputArgs.clang:
      cls.buildWithClang = True
    else:
      cls.buildWithClang = buildWithClang

    cls.buildWrapper = buildWrapper

    cls.logFormat = logFormat
    cls.logLevel = logLevel
    cls.logToFile = logToFile
    cls.overwriteLogFile = overwriteLogFile

    #If configurations are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.noColor:
      cls.noColoredOutput = True
    else:
      cls.noColoredOutput = noColoredOutput

    #If configurations are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.noWrapper:
      cls.buildWrapper = False
    else:
      cls.buildWrapper = buildWrapper

    cls.stopExecutionOnError = stopExecutionOnError
    cls.showTraceOnError = showTraceOnError
    cls.showSettingsValuesOnError = showSettingsValuesOnError
    cls.showPATHOnError = showPATHOnError

    cls.nugetFolderPath = nugetFolderPath
    cls.nugetVersionInfo = nugetVersionInfo
    cls.manualNugetVersionNumber = manualNugetVersionNumber

    cls.msvsPath = msvsPath

    cls.enabledBackup = enabledBackup
    cls.libsBackupPath = libsBackupPath
    cls.overwriteBackup = overwriteBackup

    #This value will be set during VS path check
    cls.msvcToolsPath = ''
    cls.msvcToolsBinPath = ''
    cls.vcvarsallPath = ''

    #Dictionary with additional configuration for each action and default values. Initially dictionary values are already set values (passed from command line, or read from userdef)
    cls.__actionOptions = {
                    'targets' : cls.targets,
                    'cpus' : cls.targetCPUs,
                    'platforms' : cls.targetPlatforms,
                    'configurations' : cls.targetConfigurations
    }
    cls.cleanupOptions = cleanupOptions

    #Set specific clean configuration if specified in userDef.py or use default values from __actionOptions dict
    for key,value in iterateDict(cls.__actionOptions):
      #If cleanup actions are passed from command line, take values only from __actionOptions.
      if cls.inputArgs.cleanOptions or cls.cleanupOptions.get(key,[]) == []:
        cls.cleanupOptions[key] = value

    #If cleanup options are passed like input arguments use them, instead of one loaded from userdef
    if cls.inputArgs.cleanOptions:
      cls.cleanupOptions['actions'] =  cls.inputArgs.cleanOptions

  @classmethod
  def getGnOutputPath(cls, path, target, platform, cpu, configuration):
    """
      Return gn output path for specified args.
      :param path: Root folder where will be saved target specific output
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return outputPath: Return output path relative to to root webrt folder
    """
    outputPath = config.GN_TARGET_OUTPUT_PATH.replace('[GN_OUT]', path).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration)
    return convertToPlatformPath(outputPath)