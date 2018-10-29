import os
import platform
import sys
import subprocess
import traceback

import config
from utility import Utility
from settings import Settings
from logger import Logger
from errors import *


class System:
  """
    Encapsulate determining supported targets, updating python and 
    system PATH, downloading missing tools and script termination.
  """

  #Defined here, so it can be performed logger check if script failes before logger is created
  systemLogger = None

  @classmethod
  def preInit(cls):
    """
      Determines host OS. Sets supported targets based on present folders. 
      Initializes Settings and update PATH environment variable.
    """
    #Determine host OS
    cls.hostOs = platform.system().lower()
    cls.hostOsVersion = platform.release().lower()

    #Create userdef.py file if missing. Create path variables used in preparation process.
    Settings.preInit()

    #Set available targets
    cls.setSupportedTargets()

    #Add templates path in the PATH
    Utility.addModulePath(Settings.userWorkingPath)
    Utility.addModulePath(Settings.rootScriptsPath)
    Utility.addModulePath(Settings.templatesPath)

    cls.updateDepotToolsPath()
    Utility.addPath(Settings.localBuildToolsPath)

  @classmethod
  def setUp(cls):

    Settings.init()
    Logger.SetUp()
    cls.systemLogger = Logger.getLogger('System')

    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_GN):
      cls.downloadBuildTool(config.BUILD_TOOL_GN)

    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_CLANG_FORMAT):
      cls.downloadBuildTool(config.BUILD_TOOL_CLANG_FORMAT)

    #Set current working directory to SDK root folder
    os.chdir(Settings.rootSdkPath)
    
    #TODO: Update clang

  @classmethod
  def checkTools(cls):
    """
      Checks if git and perl are installed on host machine.
      :return: NO_ERROR if all tools are installed, otherwise returns error code
    """
    #Check if Git is installed
    if not Utility.checkIfToolIsInstalled('git'):
      return ERROR_SYSTEM_MISSING_GIT
    
    #Check if Perl is installed
    if not Utility.checkIfToolIsInstalled('perl'):
      return ERROR_SYSTEM_MISSING_PERL

    return NO_ERROR

  @classmethod
  def setSupportedTargets(cls):
    """
      Sets array of supported targets. By default webrtc is supported. 
      Ortc is supported if ortc folder exists in sdk root
    """
    #Webrtc is always supported
    cls.supportedTargets = ['webrtc']
    
    #If ortc folder exists in sdk root folder add ortc in the list of supported targets
    if os.path.exists(os.path.join(Settings.rootSdkPath,'ortc')):
      cls.supportedTargets += ['ortc']

  @classmethod
  def checkIfTargetIsSupported(cls, target):
    """
      Checks if specific target is supported.
      :param target: target to check for
      :return: True if target is supported
    """
    if target.lower() not in [item.lower() for item in cls.supportedTargets]:
      return False
    return True

  @classmethod
  def checkIfTargetsAreSupported(cls, targets):
    """
      Checks if specified targets are supported.
      :param targets: list of targets to check for
      :return: True if targets are supported
    """
    cls.systemLogger.debug('Checking if specified targets are supported.')
    for target in targets:
      if not cls.checkIfTargetIsSupported(target):
        return False
    return True

  @classmethod
  def checkIfPlatformIsSupportedForHostCPU(cls, platform):
    """
      Checks if host Os supports specific platform.
      :param platform: platform to check for
      :return: True if platform is supported
    """
    if platform.lower() not in Settings.supportedPlatformsForHostOs[cls.hostOs]:
      cls.systemLogger.warning(platform + ' is not supported.')
      return False
    return True

  @classmethod
  def checkIfPlatformsAreSupported(cls, platforms):
    """
      Checks if host OS supports specified platforms.
      :param platforms: list of platforms to check for
      :return: True if platforms are supported
    """
    cls.systemLogger.debug('Checking if specified platforms are supported.')
    for platform in platforms:
      if not cls.checkIfPlatformIsSupportedForHostCPU(platform):
        return False
    return True

  @classmethod
  def isWindows(cls):
    """
      Checks if Windows is host OS.
      :return: True if Windows
    """
    if cls.hostOs.lower() == 'windows':
      return True
    return False

  @classmethod
  def updateDepotToolsPath(cls):
    """
      Checks if Google's depot tools is in the PATH, removes it and add local depot tool path in PATH.
    """
    #Search if gclient is one of the folders in the PATH
    depotToolPath = Utility.searchFileInPATH('gclient')
    if depotToolPath != None:
      #Remove depot tools path from the PATH
      Utility.removePath(depotToolPath)
      #Add local depot tools path in the PATH
      Utility.addPath(Settings.localDepotToolsPath)

  @classmethod
  def downloadBuildTool(cls, toolName):
    """
      Download tools from the google storage, Currently used for downloading gn and clang-format
      :param toolName: tool name (gn, clang-format)
    """
    #Temporary change working directory to local depot tools path
    oldCurrent = os.getcwd()
    os.chdir(Settings.localDepotToolsPath)
    #Download tool
    ret = subprocess.call([
      'python',
      'download_from_google_storage.py',
      '--bucket', 'chromium-' + toolName,
      '-s',
      os.path.join(Settings.localBuildToolsPath,toolName + '.exe.sha1')])

    #Switch to previous working directory
    os.chdir(oldCurrent)

    if ret != 0:
      cls.systemLogger.error('Failed downloading ' + toolName)

  @classmethod
  def stopExecution(cls, error = NO_ERROR, message = ''):
    """
      Stops further script execution.
      :param error: error code. Default value is NO_ERROR
      :param message: error message. If message is empty, it will be used error message related to provided error code
    """
    if error:
      #If message is not empty, show it, otherwise get message for provided error code
      if message != '':
        errorMessage = message
      else:
        errorMessage = error_codes[error]
      
      #If logger is not yet initialzed it cannot be use it, so just colorized message is shown
      if cls.systemLogger != None:
        cls.systemLogger.critical('Script execution has failed')
        cls.systemLogger.error(message)
      else:
        Logger.printColorMessage('Script execution has failed')
        Logger.printColorMessage('Error E'+ str(error) + ': ' + errorMessage)

      #If showSettingsValuesOnError is set to True, print current settings values
      if Settings.showSettingsValuesOnError:
        print ('\n\n\n----------------------- CURRENT SETTINGS -----------------------')
        attrs = vars(Settings)
        print ('\n '.join('%s: %s' % item for item in attrs.items()))
        print ('------------------- CURRENT SETTINGS END -----------------------')

      #If showTraceOnError is set to True, print current trace log
      if Settings.showTraceOnError:
        print ('\n\n\n----------------------- TRACE -----------------------')
        traceback.print_stack()
        print ('----------------------- TRACE END -----------------------')

    sys.exit(error)
