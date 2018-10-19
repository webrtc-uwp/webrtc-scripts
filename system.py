import os
import platform
import sys
import defaults
from utility import Utility
from settings import Settings
from logger import Logger
import traceback
#exec 'from %s import *'%(defaults.currentTemplateFile)


class System:

    @classmethod
    def PreInit(cls):

      #Determine host OS
      cls.hostOs = platform.system()
      cls.hostOsVersion = platform.release()

      #Set available targets
      cls.setSupportedTargets()

      #cls.addPath(defaults.webrtcDefaultsPath)
      #if cls.checkIfTargetIsSupported('ortc'):
      #   cls.addPath(defaults.ortcDefaultsPath)

      Settings.preInit()
      #Add templates path in the PATH
      cls.addPath(Settings.userWorkingPath)
      cls.addPath(Settings.rootScriptsPath)
      cls.addPath(Settings.templatesPath)

    @classmethod
    def Check(cls):
      #Check if Git and Perl are installed
      Utility.checkIfGitIsInstalled()
      Utility.checkIfPerlIsInstalled()

    @classmethod
    def SetUp(cls):

      Settings.init()
      Logger.SetUp()
      cls.Logger = Logger.getLogger("main logger")

      #Set current working directory to SDK root folder
      os.chdir(Settings.rootSdkPath)
      
      #ACTION: Update clang

    @staticmethod
    def removeDepotToolsFromPath():
      print('Removing depot_tools from path')

    @staticmethod
    def addPath(path):
      #print('Adding ' + path + ' to PATH.')
      sys.path.append(path)

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
    def stopExecution(cls, message = "", error = 0):
      if error:
        cls.Logger.critical('Script execution has failed')
        cls.Logger.error(message)
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
