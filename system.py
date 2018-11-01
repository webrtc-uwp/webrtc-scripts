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
from helper import convertToPlatformPath


class System:
  """
    Encapsulate determining supported targets, updating python and 
    system PATH, downloading missing tools and script termination.
  """

  #Defined here, so it can be performed logger check if script failes before logger is created
  logger = None

  @classmethod
  def preInit(cls):
    """
      Determines host OS. Sets supported targets based on present folders.
    """
    #Determine host OS
    cls.hostOs = platform.system().lower()
    cls.hostOsVersion = platform.release().lower()

    #Create path variables used in preparation process.
    Settings.preInit()

    #Set available targets
    cls.__setSupportedTargets()

    #Add three paths, where can be found templates, in the PYTHONPATH
    Utility.addModulePath(Settings.userWorkingPath)       #User working directory - from where script is run
    Utility.addModulePath(Settings.rootScriptsPath)       #Folder where are scripts file
    Utility.addModulePath(Settings.templatesPath)         #Subfolder in scripts folder, that contains only template files

    Utility.addPath(Settings.localBuildToolsPath)

  @classmethod
  def setUp(cls):
    """
      Initializes Settings, creates logger and updates depot tools path
    """
    #Create userdef.py file if missing. 
    cls.__createUserDefFile()
    
    #Load all settings values
    Settings.init()

    #After logger settings are loaded (log level, log format, ...), logger can be prepared for usage
    Logger.setUp()
    cls.logger = Logger.getLogger('System')
    
    #Set utility logger
    Utility.setUp()

    cls.__updateDepotToolsPath()

    if cls.isWindows:
      cls.__determineVisualStudioPath()
    #Set current working directory to SDK root folder
    #os.chdir(Settings.rootSdkPath)
    
    #TODO: Update clang

  @classmethod
  def downloadBuildToolsIfNeeded(cls):
    """
      Downloads gn and clang-format build tools if missing.
    """
    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_GN):
      cls.logger.warning(config.BUILD_TOOL_GN + ' build tool is not found.')
      cls.__downloadBuildTool(config.BUILD_TOOL_GN)

    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_CLANG_FORMAT):
      cls.logger.warning(config.BUILD_TOOL_CLANG_FORMAT + ' build tool is not found.')
      cls.__downloadBuildTool(config.BUILD_TOOL_CLANG_FORMAT)

  @classmethod
  def checkTools(cls):
    """
      Checks if git and perl are installed on host machine.
      :return: NO_ERROR if all tools are installed, otherwise returns error code
    """
    #Check if Git is installed
    if not Utility.checkIfToolIsInstalled('git'):
      cls.logger.warning('git' + ' is not installed.')
      return ERROR_SYSTEM_MISSING_GIT
    
    #Check if Perl is installed
    if not Utility.checkIfToolIsInstalled('perl'):
      cls.logger.warning('perl' + ' is not installed.')
      return ERROR_SYSTEM_MISSING_PERL

    return NO_ERROR

  @classmethod
  def checkIfTargetIsSupported(cls, target):
    """
      Checks if specific target is supported.
      :param target: target to check for
      :return: True if target is supported
    """
    if target.lower() not in [item.lower() for item in cls.supportedTargets]:
      return ERROR_SYSTEM_MISSING_PERL
      return False
    return True

  @classmethod
  def checkIfTargetsAreSupported(cls, targets):
    """
      Checks if specified targets are supported.
      :param targets: list of targets to check for
      :return: True if targets are supported
    """
    cls.logger.debug('Checking if specified targets are supported.')
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
      cls.logger.warning(platform + ' is not supported.')
      return False
    return True

  @classmethod
  def checkIfPlatformsAreSupported(cls, platforms):
    """
      Checks if host OS supports specified platforms.
      :param platforms: list of platforms to check for
      :return: True if platforms are supported
    """
    cls.logger.debug('Checking if specified platforms are supported.')
    for platform in platforms:
      if not cls.checkIfPlatformIsSupportedForHostCPU(platform):
        return False
    return True

  @classmethod
  def checkIfCPUIsSupportedForPlatform(cls, cpu, platform):
    """
      Checks if host Os supports specific platform.
      :param platform: platform to check for
      :return: True if platform is supported
    """
    if cpu.lower() not in Settings.supportedCPUsForPlatform[platform]:
      cls.logger.warning('CPU ' + cpu + ' is not supported for platform ' + platform)
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
      if cls.logger != None:
        cls.logger.critical('Script execution has failed')
        cls.logger.error(message)
      else:
        Logger.printColorMessage('Script execution has failed')
        Logger.printColorMessage('Error E'+ str(error) + ': ' + errorMessage)

      #If showSettingsValuesOnError is set to True, print current settings values
      if Settings.showSettingsValuesOnError:
        print ('\n\n\n----------------------- CURRENT SETTINGS -----------------------')
        attrs = vars(Settings)
        print ('\n '.join('%s: %s' % item for item in attrs.items()))
        print ('------------------- CURRENT SETTINGS END -----------------------')

      if Settings.showPATHOnError:
        print ('\n\n\n----------------------- PATH -----------------------')
        print (os.environ['PATH'])
        print ('------------------- PATH END -----------------------')

      #If showTraceOnError is set to True, print current trace log
      if Settings.showTraceOnError:
        print ('\n\n\n----------------------- TRACE -----------------------')
        traceback.print_stack()
        print ('----------------------- TRACE END -----------------------')

    sys.exit(error)

  #---------------------------------- Private methods --------------------------------------------
  @classmethod
  def __createUserDefFile(cls):
    """
      Created userdef.py file from defaults.py if it is missing.
    """
    #Checks if in user working directory exists files userdefs.py and if not creates it from default.py
    if not os.path.isfile(Settings.userDefFilePath):
      with open(Settings.defaultFilePath, 'r') as defaultsFile:
        tempFileContent = defaultsFile.readlines()
        tempFileContent = tempFileContent[4:]
        tempFileContent.insert(0,'# ' + config.USERDEF_DESCRIPTION_MESSAGE + '\n')
        tempFileContent = "".join(tempFileContent)
        with open(Settings.userDefFilePath, 'w') as userDefFile:
          userDefFile.write(tempFileContent)

  @classmethod
  def __setSupportedTargets(cls):
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
  def __updateDepotToolsPath(cls):
    """
      Checks if Google's depot tools is in the PATH, removes it and add local depot tool path in PATH.
    """
    #Search if gclient is one of the folders in the PATH
    depotToolPath = Utility.searchFileInPATH('gclient')
    if depotToolPath != None:
      cls.logger.debug('Removing depot tools path \'' + depotToolPath +'\' from the PATH.')
      #Remove depot tools path from the PATH
      Utility.removePath(depotToolPath)
    cls.logger.info('Adding depot tools path \'' + Settings.localDepotToolsPath +'\' to the PATH.')
    #Add local depot tools path in the PATH
    Utility.addPath(Settings.localDepotToolsPath)

  @classmethod
  def __downloadBuildTool(cls, toolName):
    """
      Download tools from the google storage, Currently used for downloading gn and clang-format
      :param toolName: tool name (gn, clang-format)
    """
    
    #oldCurrent = os.getcwd()
    #os.chdir(Settings.localDepotToolsPath)
    
    #Temporary change working directory to local depot tools path
    Utility.pushd(Settings.localDepotToolsPath)
    
    cls.logger.info('Downloading build tool ' + toolName + '...')
    #Download tool
    ret = subprocess.call([
      'python',
      'download_from_google_storage.py',
      '--bucket', 'chromium-' + toolName,
      '-s',
      os.path.join(Settings.localBuildToolsPath,toolName + '.exe.sha1')])

    #Switch to previous working directory
    Utility.popd()
    #os.chdir(oldCurrent)

    if ret != 0:
      cls.logger.error('Failed downloading ' + toolName)

  @classmethod
  def __determineVisualStudioPath(cls):
    """
      Determines Visual Studio and MSVC tools paths if they are installed in
      Program Files or Program Files (x86). If VS is installed but it is not found
      in these folders, it is required to set msvsPath variable in userdef.py file
      to point to proper folder. 
      (e.g. msvsPath = E:\\Development\\Microsoft Visual Studio\\2017\\Community)
    """
    if Settings.msvsPath == '' or not os.path.exists(Settings.msvsPath):
      vsPath = ''
      if os.environ['ProgramFiles(x86)'] == '':
        vsPath = os.environ['ProgramFiles']
      else:
        vsPath = os.environ['ProgramFiles(x86)']
       
      vsPath = os.path.join(vsPath,convertToPlatformPath(config.MSVS_FOLDER_NAME))

      if os.path.exists(vsPath):
        for version in config.MSVS_VERSIONS:
          versionPath = os.path.join(vsPath,version)
          if os.path.exists(version):
            Settings.msvsPath = versionPath
            break
      else:
        cls.logger.warning('Visual studio 2017 is not found at ' + vsPath + '. Please install it, or if it is installed, set msvsPath variable in userdef.py to point to correct path.')

      if Settings.msvsPath != '':
        Settings.msvcToolsPath = os.path.join(Settings.msvsPath,convertToPlatformPath(config.MSVC_TOOLS_PATH))
        cls.logger.info('Visual studio path is ' + Settings.msvsPath)
        cls.logger.debug('MSVC tools path is ' + Settings.msvcToolsPath)

    """
    SET progfiles=%ProgramFiles%
IF NOT "%ProgramFiles(x86)%" == "" SET progfiles=%ProgramFiles(x86)%

REM Check if Visual Studio 2017 is installed
SET msVS_Path="%progfiles%\Microsoft Visual Studio\2017"
SET msVS_Version=14

IF EXIST !msVS_Path! (
	SET msVS_Path=!msVS_Path:"=!
	IF EXIST "!msVS_Path!\Community" SET msVS_Path="!msVS_Path!\Community"
	IF EXIST "!msVS_Path!\Professional" SET msVS_Path="!msVS_Path!\Professional"
	IF EXIST "!msVS_Path!\Enterprise" SET msVS_Path="!msVS_Path!\Enterprise"
	IF EXIST "!msVS_Path!\VC\Tools\MSVC" SET tools_MSVC_Path=!msVS_Path!\VC\Tools\MSVC
)

IF NOT EXIST !msVS_Path! CALL:error 1 "Visual Studio 2017 is not installed"

for /f %%i in ('dir /b %tools_MSVC_Path%') do set tools_MSVC_Version=%%i

CALL:print %debug% "Visual Studio path is !msVS_Path!"
CALL:print %debug% "Visual Studio 2017 Tools MSVC Version is !tools_MSVC_Version!"
"""