import sys
import os
import time

from inputHandler import Input
from system import System
from settings import Settings
from logger import Logger,ColoredFormatter
from prepare import Preparation
from builder import Builder
from cleanup import Cleanup
from errors import NO_ERROR, ERROR_TARGET_NOT_SUPPORTED, ERROR_PLATFORM_NOT_SUPPORTED
from summary import Summary

def actionClean():
  """
    Deletes output folders and files generated from idl
  """
  Logger.printStartActionMessage('Cleanup')

  #Init cleanup logger
  Cleanup.init()

  for action in Settings.cleanupOptions['actions']:
    if action == 'cleanOutput':
      for target in Settings.cleanupOptions['targets']:
        for platform in Settings.cleanupOptions['platforms']:
          for cpu in Settings.cleanupOptions['cpus']:
            for configuration in Settings.cleanupOptions['configurations']:
              #Clean up output folders for specific target, platform, cpu and configuration
              Cleanup.run(action, target, platform, cpu, configuration)
    else:
      #Perform other cleanup acrions that are not dependent of target ...
      Cleanup.run(action)

  Logger.printEndActionMessage('Cleanup')

def actionCreateUserdef():
  """
    Creates userdef.py file.
  """
  result = System.recreateUserDef()
  if result != NO_ERROR:
    #Terminate script execution if stopExecutionOnError is set to True in userdef
    shouldEndOnError(result)

def actionPrepare():
  """
    Prepare dev environment for all specified targets and platforms.
  """
  
  #Do preparation that is common for all platforms. Pass true if ortc is one of targets
  Preparation.setUp('ortc' in Settings.targets)
  for target in Settings.targets:
    for platform in Settings.targetPlatforms:
      for cpu in Settings.targetCPUs:
        if System.checkIfCPUIsSupportedForPlatform(cpu,platform):
          for configuration in Settings.targetConfigurations:
            Logger.printStartActionMessage('Prepare ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.YELLOW)
            result = Preparation.run(target, platform, cpu, configuration)
            Summary.addSummary('prepare', target, platform, cpu, configuration, result, Preparation.executionTime)
            if result != NO_ERROR:
              Logger.printEndActionMessage('Failed prepare ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.RED)
              #Terminate script execution if stopExecutionOnError is set to True in userdef
              shouldEndOnError(result)
            else:
              Logger.printEndActionMessage('Prepare '  + target + ' ' + platform + ' ' + cpu + ' ' + configuration)

def actionBuild():
  """
    Build all specified targets for all specified platforms.
  """

  #Init builder logger
  Builder.init()

  for target in Settings.targets:
    targetsToBuild, combineLibs = Builder.getTargetGnPath(target)
    for platform in Settings.targetPlatforms:
      for cpu in Settings.targetCPUs:
        if System.checkIfCPUIsSupportedForPlatform(cpu,platform):
          for configuration in Settings.targetConfigurations:
            if not Summary.isPreparationFailed(target, platform, cpu, configuration):
              Logger.printStartActionMessage('Build ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.YELLOW)
              result = Builder.run(target, targetsToBuild, platform, cpu, configuration, combineLibs)
              Summary.addSummary('build', target, platform, cpu, configuration, result, Builder.executionTime)
              if result != NO_ERROR:
                  Logger.printEndActionMessage('Failed build ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.RED)
                  #Terminate script execution if stopExecutionOnError is set to True in userdef
                  shouldEndOnError(result)
              else:
                Logger.printEndActionMessage('Build ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration)
            else:
              Logger.printColorMessage('Build cannot run because preparation has failed for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.YELLOW)
              Logger.printEndActionMessage('Build not run for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration,ColoredFormatter.YELLOW)

def actionCreateNuget():
    pass

def actionPublishNuget():
  pass

def actionUpdatePublishedSample():
  pass

def shouldEndOnError(error):
  """
    Terminates script execution if stopExecutionOnError is set to True in userdef 
  """
  if Settings.stopExecutionOnError:
    System.stopExecution(error)
    Summary.printSummary()


def main():
  
  #Save time when script is started to calculate total execution tima
  start_time = time.time()

  #Determine host OS, checks supported targets, update python and system paths.
  System.preInit()

  #Parse input parameters if any. This must be call after System.preInit, because it is required to determine host os first. 
  Input.parseInput(sys.argv[1:])
  
  #Start message put here, so it is not shown when script help is being shown.
  Logger.printStartActionMessage('Script execution',ColoredFormatter.YELLOW)

  #Create userdef.py file if missing. Load settings. Create system logger. Download depot tools (gn and clang-format). -----Set working directory to rood sdk folder.
  System.setUp()

  #Create root logger
  mainLogger = Logger.getLogger('Main')
  mainLogger.info('Root logger is created')
  
  #Check if required tools are installed. Currently git (used for downloading iOS binaries) and perl(used in assembly builds)
  errorCode = System.checkTools()
  if errorCode != 0:
    System.stopExecution(errorCode)
   
  #Check if specified targets are supported
  if not System.checkIfTargetsAreSupported(Settings.targets):
    mainLogger.error('Target from the list ' + str(Settings.targets) + ' is not supported')
    System.stopExecution(ERROR_TARGET_NOT_SUPPORTED)
  
  #Check if specified platforms are supported
  if not System.checkIfPlatformsAreSupported(Settings.targetPlatforms):
    mainLogger.error('Platform from the list ' + str(Settings.targetPlatforms) + ' is not supported')
    System.stopExecution(ERROR_PLATFORM_NOT_SUPPORTED)

  #Start performing actions. Actions has to be executed in right order and that is the reason why it is handled this way
  if 'clean' in Settings.actions:
    actionClean()
    
  if 'createuserdef' in Settings.actions:
    actionCreateUserdef()

  if 'prepare' in Settings.actions:
    actionPrepare()

  if 'build' in Settings.actions:
    actionBuild()

  if 'createNuget' in Settings.actions:
    actionCreateNuget()

  if 'publishNuget' in Settings.actions:
    actionPublishNuget()

  if 'updatePublishedSample' in Settings.actions:
    actionUpdatePublishedSample()

  end_time = time.time()
  Summary.printSummary(end_time - start_time)

if  __name__ =='__main__': main()
