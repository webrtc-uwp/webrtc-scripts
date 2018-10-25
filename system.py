import os
import platform
import sys
import subprocess
import defaults
from utility import Utility
from settings import Settings
from logger import Logger
import traceback
from errors import *
#exec 'from %s import *'%(defaults.currentTemplateFile)


class System:

  systemLogger = None

  @classmethod
  def preInit(cls):
    """
      Determines host OS. Sets supported targets based on present folders. 
      Initializes Settings and update PATH environment variable.
    """
    #Determine host OS
    cls.hostOs = platform.system()
    cls.hostOsVersion = platform.release()

    #Set available targets
    cls.setSupportedTargets()

    Settings.preInit()

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
    cls.systemLogger = Logger.getLogger("System")

    if not Utility.checkIfToolIsInstalled(defaults.BUILD_TOOL_GN):
      cls.downloadBuildTool(defaults.BUILD_TOOL_GN)

    if not Utility.checkIfToolIsInstalled(defaults.BUILD_TOOL_CLANG_FORMAT):
      cls.downloadBuildTool(defaults.BUILD_TOOL_CLANG_FORMAT)

    #Set current working directory to SDK root folder
    os.chdir(Settings.rootSdkPath)
    
    #ACTION: Update clang

  @classmethod
  def checkTools(cls):
    #Check if Git is installed
    if not Utility.checkIfToolIsInstalled('git'):
      return ERROR_SYSTEM_MISSING_GIT
    
    #Check if Perl is installed
    #if not Utility.checkIfToolIsInstalled('perl'):
    #  return ERROR_SYSTEM_MISSING_PERL

    return NO_ERROR

  @staticmethod
  def removeDepotToolsFromPath():
    print('Removing depot_tools from path')


  @classmethod
  def setSupportedTargets(cls):
      #ACTION: Performs check if ortc folder is present. If it is add it in the list of supported targets
      cls.supportedTargets = ['ortc', 'webrtc']

  @classmethod
  def checkIfTargetIsSupported(cls, target):
    if target in [item.lower() for item in cls.supportedTargets]:
      #print('Target ' + target + 'is supported')
      return True
    return False

  @classmethod
  def checkIfTargetsAreSupported(cls, targets):
    for target in targets:
      if target not in cls.supportedTargets:
        return False
    return True

  @classmethod
  def checkIfPlatformIsSupportedForHostCPU(cls, platform):
    if platform in Settings.supportedPlatformsForHostOs[cls.hostOs]:
      #print('host supports platform ' + cls.hostOs)
      return True
    return False

  @classmethod
  def checkIfPlatformsAreSupported(cls, platforms):
    for platform in platforms:
      if platform not in Settings.supportedPlatformsForHostOs[cls.hostOs]:
        #print('Platform ' + platform + ' is not supported')
        return False
    return True

  @classmethod
  def isWindows(cls):
    if cls.hostOs.lower() == 'windows':
      return True
    return False

  @staticmethod
  def setWorkingDirectory(path):
    #cwd = os.getcwd()
    if os.path.isdir(path):
      print('setWorkingDirectory 1')
      os.chdir(path)
    elif os.path.isdir('../' + path):
      print('setWorkingDirectory 2')
      os.chdir('../' + path)
    else:
      print('setWorkingDirectory 3')
      return False
    return  True

  @classmethod
  def updateDepotToolsPath(cls):
    depotToolPath = Utility.searchFileInPATH('gclient')
    if depotToolPath != None:
      Utility.removePath(depotToolPath)
      Utility.addPath(Settings.localDepotToolsPath)

  @classmethod
  def downloadBuildTool(cls, toolName):

    oldCurrent = os.getcwd()
    os.chdir(Settings.localDepotToolsPath)
    ret = subprocess.call([
      'python',
      'download_from_google_storage.py',
      '--bucket', 'chromium-' + toolName,
      '-s',
      os.path.join(Settings.localBuildToolsPath,toolName + '.exe.sha1')])

    if ret != 0:
      cls.systemLogger.warning('Failed downloading gn.exe')

    os.chdir(oldCurrent)

      #os.path.join('src', 'buildtools', 'android', 'doclava.tar.gz.sha1')])
  @classmethod
  def stopExecution(cls, error, message=""):
    if error:
      if message != "":
        errorMessage = message
      else:
        errorMessage = error_codes[error]
      if cls.systemLogger != None:
        cls.systemLogger.critical('Script execution has failed')
        cls.systemLogger.error(message)
      else:
        Logger.printColorMessage('Script execution has failed')
        Logger.printColorMessage('Error E'+ str(error) + ': ' + errorMessage)
      if Settings.showSettingsValuesOnError:
        print ('\n\n\n----------------------- CURRENT SETTINGS -----------------------')
        attrs = vars(Settings)
        print ('\n '.join("%s: %s" % item for item in attrs.items()))
        print ('------------------- CURRENT SETTINGS END -----------------------')
      if Settings.showTraceOnError:
        print ('\n\n\n----------------------- TRACE -----------------------')
        traceback.print_stack()
        print ('----------------------- TRACE END -----------------------')

    sys.exit(error)
