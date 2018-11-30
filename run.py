import sys
import os

from inputHandler import Input
from system import System
from settings import Settings
from logger import Logger,ColoredFormatter
from prepare import Preparation
from builder import Builder
from cleanup import Cleanup
from createNuget import CreateNuget
from errors import *
from summary import Summary

def actionClean():
  
  Logger.printStartActionMessage('Cleanup')
  Cleanup.init()

  for action in Settings.cleanOptions['actions']:
    Cleanup.run(action)

  Logger.printEndActionMessage('Cleanup')

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
            Logger.printStartActionMessage('Prepare')
            result = Preparation.run(target, platform, cpu, configuration)
            Summary.addSummary('prepare', target, platform, cpu, configuration, result)
            if result != NO_ERROR:
              Logger.printEndActionMessage('Prepare',ColoredFormatter.RED)
              System.stopExecution(result)
            else:
              Logger.printEndActionMessage('Prepare')

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
        for configuration in Settings.targetConfigurations:
          Logger.printStartActionMessage('Build')
          result = Builder.run(target, targetsToBuild, platform, cpu, configuration, combineLibs)
          Summary.addSummary('build', target, platform, cpu, configuration, result)
          if result != NO_ERROR:
              Logger.printEndActionMessage('Build',ColoredFormatter.RED)
              shouldEndOnError(result)
              #System.stopExecution(result)
          else:
            Logger.printEndActionMessage('Build')

def actionCreateNuget():
  CreateNuget.init()

  for target in Settings.targets:
    CreateNuget.run(
      target, Settings.targetPlatforms, Settings.targetCPUs, 
      Settings.targetConfigurations, Settings.nugetFolderPath, Settings.nugetVersionInfo
    )

def actionPublishNuget():
  pass

def actionUpdatePublishedSample():
  pass

def shouldEndOnError(error):
  if Settings.stopExecutionOnError:
    Summary.printSummary()
    System.stopExecution(error)


def main():

  #Determine host OS, checks supported targets, update python and system paths.
  System.preInit()

  #Parse input parameters if any. This must be call after System.preInit, because it is required to determine host os first. 
  Input.parseInput(sys.argv[1:])
  
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

  Summary.printSummary()

if  __name__ =='__main__': main()
