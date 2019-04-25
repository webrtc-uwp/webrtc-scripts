import os
import platform
import sys
import re
import subprocess
import traceback
from importlib import import_module
try:
  from _winreg import HKEY_LOCAL_MACHINE
except:
  pass

import config
from utility import Utility
from nugetUtility import NugetUtility
from settings import Settings
from logger import Logger, ColoredFormatter
import errors
from errors import error_codes, NO_ERROR
from helper import convertToPlatformPath, getCPUFamily
from consts import MAX_SDK_ROOT_PATH_LENGTH

class System:
  """
    Encapsulate determining supported targets, updating python and 
    system PATH, downloading missing tools and script termination.
  """

  #Defined here, so it can be performed logger check if script failes before logger is created
  logger = None
  recreatedUserDef = False
  @classmethod
  def preInit(cls):
    """
      Determines host OS. Sets supported targets based on present folders.
    """
    #Determine host OS
    cls.hostOs = platform.system().lower()
    cls.hostOsVersion = platform.release().lower()
    cls.hostCPU = getCPUFamily(platform.machine())

    #Create path variables used in preparation process.
    Settings.preInit()

    #Set available targets
    cls.__setSupportedTargets()

    #Add three paths, where can be found templates, in the PYTHONPATH
    Utility.addModulePath(Settings.userWorkingPath)       #User working directory - from where script is run
    Utility.addModulePath(Settings.rootScriptsPath)       #Folder where are scripts file
    Utility.addModulePath(Settings.templatesPath)         #Subfolder in scripts folder, that contains only template files

    Utility.addPath(Settings.localBuildToolsPath)

    #Determine python executable path and add python's Scripts folder in the system PATH
    executablePath = Utility.getExecutablePath('python')
    if executablePath != None:
      pythonPath = os.path.dirname(executablePath)
      pythonScriptsPath = os.path.join(pythonPath,'Scripts')
      #Add python's Scripts folder in the PATH
      Utility.addPath(pythonScriptsPath)

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

    #Set up nuget utility
    NugetUtility.setUp()

    #Remove Google's depot tools from the PATH and add local depot tool path.
    cls.__updateDepotToolsPath()

    if cls.isWindows:
      #Determine Visual Studio and MSVC tools paths
      cls.__determineVisualStudioPath()

    #Install missing python packages
    cls.installPythonModules(config.PYTHON_PACKAGES_TO_INSTALL)

    #Show warning if root sdk path is longer than MAX_SDK_ROOT_PATH_LENGTH = 65
    if len(Settings.rootSdkPath) > MAX_SDK_ROOT_PATH_LENGTH:
      cls.logger.warning(Settings.rootSdkPath + ' is longer than ' + str(MAX_SDK_ROOT_PATH_LENGTH) + '. That may cause build issues for webrtc libraries!')

  @classmethod
  def updatePythonTools(cls):
    """
      Update python's pip tool. In future maybe it would be required to update other tools as well.
      TODO: Check when it is best to call it
    """
    #Update pip tool.
    cmd = 'python.exe -m pip install --upgrade pip'
    result = Utility.runSubprocess([cmd])
    if result != 0:
      cls.logger.error('Failed to update pip!')

  @classmethod
  def installPythonModules(cls, modulesDict):
    """
      Checks if win32file module is installed, and if it is not, install pywin32 python package.
    """

    for module in modulesDict.keys():
      try:
        #Provoke exception if module is not available 
        globals().update(import_module(module).__dict__)
      except:
         #Install python package
        cmd = 'pip install ' + modulesDict[module]
        result = Utility.runSubprocess([cmd], Settings.logLevel == 'DEBUG')
        if result != 0:
          cls.logger.error('Failed to install package ' + modulesDict[module] + ' required for module ' + module)

  @classmethod
  def downloadBuildToolsIfNeeded(cls):
    """
      Downloads gn and clang-format build tools if missing.
      :return ret: True if all tools are present or successfully donloaded.
    """
    ret = True

    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_GN):
      cls.logger.warning(config.BUILD_TOOL_GN + ' build tool is not found.')
      ret = cls.__downloadBuildTool(config.BUILD_TOOL_GN)

    if not Utility.checkIfToolIsInstalled(config.BUILD_TOOL_CLANG_FORMAT) and ret:
      cls.logger.warning(config.BUILD_TOOL_CLANG_FORMAT + ' build tool is not found.')
      ret = cls.__downloadBuildTool(config.BUILD_TOOL_CLANG_FORMAT)

    return ret

  @classmethod
  def checkTools(cls):
    """
      Checks if git, perl and Windows SDK tools are installed on host machine.
      :return: NO_ERROR if all tools are installed, otherwise returns error code
    """
    ret = NO_ERROR
    #Check if Git is installed
    if not Utility.checkIfToolIsInstalled('git'):
      cls.logger.warning('git' + ' is not installed.')
      return errors.ERROR_SYSTEM_MISSING_GIT
    
    #Check if Perl is installed
    if not Utility.checkIfToolIsInstalled('perl'):
      cls.logger.warning('perl' + ' is not installed.')
      #return errors.ERROR_SYSTEM_MISSING_PERL

    ret = cls.checkVSDebugTools()
    
    return ret
  
  @classmethod
  def checkIsPythonVersionSupported(cls):
    """
    Checks if the correct python version is being used.
    :return: True/False based on python version.
    """
    python_version_number = str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro)
    if sys.version_info.major is not int(config.SUPPORTED_PYTHON_VERSION[0]):
      Logger.printColorMessage('Google GN compilation requires Python version ' + 
                                config.SUPPORTED_PYTHON_VERSION + ' but your python version is ' + 
                                python_version_number + ' Please re-run using the proper version of Python.', 
                                ColoredFormatter.RED)
      return False
    else:
      return True

  @classmethod
  def checkVSDebugTools(cls):
    """
      Checks if VS debug tools are installed.
      :return: ERROR_SYSTEM_MISSING_VS_DEBUG_TOOLS if debug tools are not isntalled.
    """
    ret = NO_ERROR
    # Get Windows SDK Debugger path from Windows registry
    winSdkDebugToolPath = Utility.getKeyValueFromRegistry(HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Microsoft\Windows Kits\Installed Roots',"WindowsDebuggersRoot10")

    # If path is not found in registry or path is not valid return error
    if winSdkDebugToolPath == None or not os.path.isdir(winSdkDebugToolPath): 
      ret = errors.ERROR_SYSTEM_MISSING_VS_DEBUG_TOOLS
    else:
      cls.logger.debug('Windows SDK Debug Tools path is ' + winSdkDebugToolPath)
    return ret

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
      
      try:
        Utility.terminateSubprocess()
        Utility.returnOriginalFile(Settings.mainBuildGnFilePath)
      except Exception as error:
        Logger.printColorMessage(str(error))

      if error == errors.TERMINATED_BY_USER:
        Logger.printColorMessage(error_codes[error])
      else:
        #If logger is not yet initialzed it cannot be use it, so just colorized message is shown
        if cls.logger != None:
          cls.logger.critical('Script execution has failed')
          cls.logger.error(errorMessage)
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

  @classmethod
  def recreateUserDef(cls):
    """
      Recreates userdef.py file if it is not just created. If userdef.py file creation has failed, 
      script will be terminated. 
      :return ret: NO_ERROR if userdef is created or it was "just" created. 
                   ERROR_SYSTEM_FAILED_DELETING_USERDEF if deleting userdef.py failed.
    """
    ret = NO_ERROR
    if not cls.recreatedUserDef:
      try:
        #Deletes userdef.py file
        Utility.deleteFiles([Settings.userDefFilePath])
        cls.__createUserDefFile()
      except Exception as error:
        cls.logger.error(str(error))
        ret = errors.ERROR_SYSTEM_FAILED_DELETING_USERDEF
      
    return ret

  @classmethod
  def downloadFromGoogle(cls, bucket, path, isDirectory = False, shouldRecurse = True):
    """
      Download content from the google storage buckets
      :param bucket: the name of the google bucket to download from
      :param path: the path to a sha1 file OR the path to a directory containing sha1 files
      :param isDirectory: must be True is path is a file, and False if path is a directory
      :param shouldRecurse: only used if path is a directory, True to recursively scan for sha1 files, False to not
      :return ret: True if successfully downloaded.
    """
    ret = True

    #TODO(bengreenier): we can and should derive isDirectory

    #Temporary change working directory to local depot tools path
    Utility.pushd(Settings.localDepotToolsPath)
    
    operationDetails = path + ' from bucket \'' + bucket
    cls.logger.info('Downloading ' + operationDetails + '\'...')

    #Run download
    flag = '-d' if isDirectory else '-s'
    modifier = '-r' if shouldRecurse else ''
    cmd = 'python download_from_google_storage.py --bucket ' + bucket + ' ' + flag + ' ' + path + ' ' + modifier

    result = Utility.runSubprocess([cmd], Settings.logLevel == 'DEBUG')

    #Switch to previous working directory
    Utility.popd()

    if result != NO_ERROR:
      ret = False
      cls.logger.error('Failed downloading ' + operationDetails)
    
    return ret
  #---------------------------------- Private methods --------------------------------------------
  @classmethod
  def __createUserDefFile(cls):
    """
      Created userdef.py file from defaults.py if it is missing.
    """
    #Checks if in user working directory exists files userdefs.py and if not creates it from default.py
    if not os.path.isfile(Settings.userDefFilePath):
      try:
        with open(Settings.defaultFilePath, 'r') as defaultsFile:
          tempFileContent = defaultsFile.readlines()
          tempFileContent = tempFileContent[4:]
          tempFileContent.insert(0,'# ' + config.USERDEF_DESCRIPTION_MESSAGE + '\n')
          tempFileContent = "".join(tempFileContent)
          with open(Settings.userDefFilePath, 'w') as userDefFile:
            userDefFile.write(tempFileContent)
            cls.recreatedUserDef = True
      except Exception as error:
        Logger.printColorMessage(str(error))
        cls.stopExecution(errors.ERROR_SYSTEM_FAILED_USERDEF_CREATION)
        


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
      :return ret: True if successfully downloaded.
    """
    ret = True

    result = cls.downloadFromGoogle('chromium-' + toolName, os.path.join(Settings.localBuildToolsPath,toolName + '.exe.sha1'), False, False)

    if not result:
      ret = False
      cls.logger.error('Failed downloading ' + toolName)
    
    return ret

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
      #Get Program File path
      if os.environ['ProgramFiles(x86)'] == '':
        vsPath = os.environ['ProgramFiles']
      else:
        vsPath = os.environ['ProgramFiles(x86)']
       
      #Create exoected VS2017 path
      vsPath = os.path.join(vsPath,convertToPlatformPath(config.MSVS_FOLDER_NAME))

      #Indetify installed VS2017 version 
      if os.path.exists(vsPath):
        for version in config.MSVS_VERSIONS:
          versionPath = os.path.join(vsPath,version)
          if os.path.exists(versionPath):
            Settings.msvsPath = versionPath
            break
      else:
        cls.logger.warning('Visual studio 2017 is not found at ' + vsPath + '. Please install it, or if it is installed, set msvsPath variable in userdef.py to point to correct path.')

    #Determine msvc tools and vcvarsall.bat path
    if Settings.msvsPath != '':
      Settings.msvcToolsPath = os.path.join(Settings.msvsPath,convertToPlatformPath(config.MSVC_TOOLS_PATH))
      Settings.msvcToolsVersion = next(os.walk(Settings.msvcToolsPath))[1][0]
      Settings.msvcToolsBinPath = os.path.join(Settings.msvcToolsPath,Settings.msvcToolsVersion,'bin','Host' + cls.hostCPU)
      #Settings.vcvarsallPath = os.path.join(Settings.msvsPath,convertToPlatformPath(config.VCVARSALL_PATH))

      Settings.vcvarsallPath = os.path.join(Settings.msvsPath,convertToPlatformPath(config.VC_AUXILIARY_BUILD_PATH),'vcvarsall.bat')
      #Read Microsoft.VCToolsVersion.default.txt content to get current vc tools version
      #Settings.vcToolsVersionPath = os.path.join(Settings.msvsPath,convertToPlatformPath(config.VC_AUXILIARY_BUILD_PATH),'Microsoft.VCToolsVersion.default.txt')


      cls.logger.info('Visual studio path is ' + Settings.msvsPath)
      cls.logger.debug('MSVC tools path is ' + Settings.msvcToolsPath)
      cls.logger.debug('MSVC tools bin path is ' + Settings.msvcToolsBinPath)

  @classmethod
  def downloadClangClIfMissing(cls):
    """
      Downloads clang-cl.exe if missing.
      :return ret: True if exists or if it is successfully downloaded.
    """
    ret = True

    #Check if clang-cl is already downloaded
    clangPath = os.path.join(Settings.webrtcPath,convertToPlatformPath(config.CLANG_CL_PATH))
    if not os.path.isfile(clangPath):
      clangUpdateScriptPath =  os.path.join(Settings.webrtcPath,convertToPlatformPath(config.CLANG_UPDATE_SCRIPT_PATH))
      cls.logger.info('Clang-cl.exe is not found in third_party tools. It will be downloaded.')
      #Make copy of environment variable
      my_env = os.environ.copy()
      #Update environment variable with DEPOT_TOOLS_WIN_TOOLCHAIN set to 0, to prevent requiring https://chrome-internal.googlesource.com
      my_env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
      #Run clangg update script
      cmd = 'python ' + clangUpdateScriptPath
      result = Utility.runSubprocess([cmd], Settings.logLevel == 'DEBUG', my_env)
      #result = subprocess.call(['python', clangUpdateScriptPath], env=my_env)
      if result == NO_ERROR:
        cls.logger.info('Clang-cl.exe is downloaded successfully.')
        Utility.createFolderLinks(config.FOLDERS_TO_LINK_LLVM)
      else:
        ret = False
        cls.logger.error('Downloading Clang-cl.exe has failed.')
    else:
      cls.logger.debug('Clang-cl.exe is found.')
    
    return ret

  @classmethod
  def getEnvFromBat(cls):
    """Given a bat command, runs it and returns env vars set by it."""
    cmd = '\"' +  Settings.vcvarsallPath + '\" '
    cpu_arg = "amd64"
    """ if (cpu != 'x64'):
        # x64 is default target CPU thus any other CPU requires a target set
        cpu_arg += '_' + cpu"""
    cmd += cpu_arg
    cmd += ' && set'
    popen = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    variables, _ = popen.communicate()
    if popen.returncode != 0:
      raise Exception('"%s" failed with error %d' % (cmd, popen.returncode))
      #else:
      #parse variables
    return variables

  @classmethod
  def logEnvIncludeAndLibPaths(cls, platform, cpu, path):
    """
      Print include and lib paths for build environment.
      :param platform: Platform of interest ('win' or 'winuwp').
      :param cpu: CPU of interest.
      :param path: Folder path where is save environment file.
    """
    if os.path.exists(path):
      if platform == 'winuwp':
        environmentPath = os.path.join(path, 'environment.store_' + cpu)
      else:
        environmentPath = os.path.join(path, 'environment.' + cpu)
      
      if os.path.isfile(environmentPath):
        textfile = open(environmentPath, "r")
        filetext = textfile.read()
        textfile.close()
        for envVariable in Settings.logNinjaEnvironmentFileVariables:
          regex = r'\x00' + envVariable + '=(.*)\x00'
          includeStr = re.findall(regex,filetext)
          cls.logger.debug('\n\n' + envVariable + ': \n' + str(includeStr))
    else:
      cls.logger.error('environment file is missing!')
