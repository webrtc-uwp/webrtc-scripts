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
    #Main BUILD.gn path
    cls.mainBuildGnFilePath = os.path.join(cls.webrtcPath,'BUILD.gn')
    #WebRtc solution path
    cls.webrtcSolutionPaths = os.path.join(cls.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_PATH))
    #NuGet executable path
    cls.nugetExecutablePath = os.path.join(cls.rootSdkPath, convertToPlatformPath(config.NUGET_EXECUTABLE_PATH))
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
        os.path.isfile(os.path.join(cls.templatesPath, cls.inputArgs.template)) or 
        os.path.isfile(os.path.join(cls.templatesPath, cls.inputArgs.template + '.py'))):
        templateModuleName = os.path.splitext(os.path.basename(cls.inputArgs.template))[0]
        globals().update(import_module(templateModuleName).__dict__)
      print('======================================= ' + os.path.join(cls.templatesPath, cls.inputArgs.template + '.py'))
    #cls.gnOutputPath = gnOutputPath

    cls.supportedPlatformsForHostOs = supportedPlatformsForHostOs
    cls.supportedCPUsForPlatform = supportedCPUsForPlatform

    if cls.inputArgs.actions:
      cls.actions = cls.inputArgs.actions
    else:
      cls.actions = actions

    #If user target (any target different from ortc and webrtc) is passed like input argument use it.
    if cls.inputArgs.userTarget:
       cls.targets = [cls.inputArgs.userTarget]
    else:
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

    if cls.inputArgs.cpp17:
      cls.buildWithCpp17 = True
    else:
      cls.buildWithCpp17 = buildWithCpp17

    cls.buildWrapper = buildWrapper

    cls.logFormat = logFormat
    cls.logLevel = logLevel
    cls.logNinjaEnvironmentFileVariables = logNinjaEnvironmentFileVariables

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

    #If configurations are passed like input arguments use them, instead of one loaded from template
    if cls.inputArgs.includeTests:
      cls.includeTests = True
    else:
      cls.includeTests = includeTests

    cls.stopExecutionOnError = stopExecutionOnError
    cls.showTraceOnError = showTraceOnError
    cls.showSettingsValuesOnError = showSettingsValuesOnError
    cls.showPATHOnError = showPATHOnError

    cls.nugetFolderPath = nugetFolderPath
    cls.nugetVersionInfo = nugetVersionInfo
    cls.manualNugetVersionNumber = manualNugetVersionNumber
    cls.nugetPackagesToPublish = nugetPackagesToPublish
    cls.releaseNotePath = releaseNotePath
    cls.commitKeywords = commitKeywords
    cls.onedrivePath = onedrivePath
    cls.nugetAPIKey = nugetAPIKey
    cls.nugetServerURL = nugetServerURL
    cls.updateSampleInfo = updateSampleInfo

    # If url is passed like input argument use that url instead of the one from userdef
    if cls.inputArgs.uploadBackupURL:
      cls.uploadBackupURL = cls.inputArgs.uploadBackupURL
    
    # If true API key is set for nuget.org server
    cls.runSetNugetKey = False
    if cls.inputArgs.setnugetkey:
      cls.nugetAPIKey = cls.inputArgs.setnugetkey
      cls.runSetNugetKey = True
    
    if cls.inputArgs.cmdPrerelease:
      cls.nugetVersionInfo['prerelease'] = cls.inputArgs.cmdPrerelease
    
    # If true sets release note version by geting latest published nuget version from nuget.org
    cls.setservernoteversion = False
    if cls.inputArgs.setservernoteversion:
      cls.setservernoteversion = cls.inputArgs.setservernoteversion

    cls.msvsPath = msvsPath

    cls.enabledBackup = enabledBackup
    cls.libsBackupPath = libsBackupPath
    cls.overwriteBackup = overwriteBackup

    #This value will be set during VS path check
    cls.msvcToolsPath = ''
    cls.msvcToolsBinPath = ''
    cls.vcvarsallPath = ''
    cls.msvcToolsVersion = ''
    
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

    cls.availableTargetsForBuilding = availableTargetsForBuilding

    if cls.inputArgs.idlImpl:
      cls.enableIdlImpl = cls.inputArgs.idlImpl
    else:
      cls.enableIdlImpl = enableIdlImpl

    if cls.inputArgs.unitTests:
      cls.unitTestsToRun = cls.inputArgs.unitTests
    else:
      cls.unitTestsToRun = unitTestsToRun

    if '*' in cls.unitTestsToRun:
      cls.unitTestsToRun = list(unitTests)

    cls.unitTests = unitTests
    
    if cls.inputArgs.logToFile:
      cls.logToFile = cls.inputArgs.logToFile
    else:
      cls.logToFile = logToFile

    cls.logFileName = logFileName
    cls.overwriteLogFile = overwriteLogFile

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
