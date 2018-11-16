import os
import subprocess
from shutil import copyfile

import config
from utility import Utility
from settings import Settings
from system import System
from logger import Logger
from helper import convertToPlatformPath
from errors import *

class Preparation:
  """
    Encapsulats logic for setting up development environemnt for the WebRtc and generating its projects.
  """
  @classmethod
  def setUp(cls, ortc):
    """
      It is invoked only once, and does common stuff for all targets and platfroms. 
      Creates module logger. Sets working directory. Creates missing folders and links.
    """
    #Create logger
    cls.logger = Logger.getLogger('Prepare')
    
    #Set working directory to ./webrtc/xplatform/webrtc
    if not os.path.exists(Settings.webrtcPath):
      System.stopExecution(1, 'Unable to set preparation working directory')

    #Create missing folders and links
    try:
      #Change working directory
      Utility.pushd(Settings.webrtcPath)

      Utility.createFolders(config.FOLDERS_TO_GENERATE)
      Utility.createFolderLinks(config.FOLDERS_TO_LINK)

      #In case ortc is one of the targets create specific folders and links
      if (ortc):
        Utility.createFolders(config.FOLDERS_TO_GENERATE_ORTC)
        Utility.createFolderLinks(config.FOLDERS_TO_LINK_ORTC)

      Utility.copyFilesFromDict(config.FILES_TO_COPY)

      #If win is one of the selected platforms it is required to have clang-cl.
      #It is called here becuae proper folders structure is required to execute update script
      if 'win' in Settings.targetPlatforms:
        System.installClangClIfMissing()
        
      #Download missing build tools
      System.downloadBuildToolsIfNeeded()

    except Exception, errorMessage:
      cls.logger.error(errorMessage)
    finally:
      Utility.popd()
    
  @classmethod
  def run(cls, target, platform, cpu, configuration):
    isError = False
    cls.logger.info('Runnning preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #Full path to args.gn template file
    argsTemplatePath = os.path.join(Settings.rootSdkPath, convertToPlatformPath(Settings.webRTCGnArgsTemplatePath))

    #Change working directory
    Utility.pushd(Settings.webrtcPath)

    #Create output folder where webrtc generated projects will be saved 
    gnOutputPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH,target,platform,cpu,configuration)

    if not os.path.exists(gnOutputPath):
      cls.logger.debug('Making ' + gnOutputPath + ' directory.')
      os.makedirs(gnOutputPath)

    #Copy args.gn template file to output folder
    argsPath = os.path.join(gnOutputPath, 'args.gn')
    cls.logger.debug('Copying ' + argsPath + ' file' + ' to ' + argsTemplatePath )
    copyfile(argsTemplatePath, argsPath)

    #Update target os and cpu in copied args.gn file
    with open(argsPath) as argsFile:
      cls.logger.debug('Updating args.gn file. Target OS: ' + platform + '; Target CPU: ' + cpu)
      newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu).replace('-is_debug-',str(configuration.lower() == 'debug').lower())
    with open(argsPath, 'w') as argsFile:
      argsFile.write(newArgs)

    mainBuildGnFilePath = os.path.join(Settings.webrtcPath,'BUILD.gn')
    #Backup original BUILD.gn from webrtc root folder and add additional dependecies to webrtc target
    Utility.backUpAndUpdateGnFile(mainBuildGnFilePath,config.WEBRTC_TARGET,config.ADDITIONAL_TARGETS_TO_ADD)

    #Generate Webrtc projects
    try:
      os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
      cls.logger.info('Generating webrtc projects ...')
      cls.logger.debug('Output path: ' + gnOutputPath)
      result = subprocess.call([
        'gn',
        'gen',
        gnOutputPath,
        '--ide=' + config.VISUAL_STUDIO_VERSION,
      ])

      if result != 0:
        cls.logger.error('Projects generation has failed! (' + target + ',' + platform + ',' + cpu + ',' + configuration + ')')
      else:
        #Update ninja path in VS project files to point to ninja.exe in local depot_tools folder
        cls.__updateNinjaPathinProjects(gnOutputPath)
        cls.logger.info('Successfully finished preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)
    except Exception as errorMessage:
      cls.logger.error(str(errorMessage))
      isError = True
    finally:
      #Delete updated BUILD.gn from webrtc root folder and recover original file
      Utility.returnOriginalFile(mainBuildGnFilePath)
      Utility.popd()
    
    if isError:
      return ERROR_PREPARE_GN_GENERATION_FAILED
      
    return NO_ERROR
    
  #---------------------------------- Private methods --------------------------------------------
  @classmethod
  def __updateNinjaPathinProjects(cls,folder):
    for root, dirs, files in os.walk(folder):
      for file in files:
          if file.endswith('.vcxproj'):
            #cls.logger.debug('Updating ninja path in VS project file ' + file)
            #Replace 'call ninja.exe' with 'call local_depot_tools_path\ninja.exe'
            with open(os.path.join(root,file)) as projectFile:
              updatedProject=projectFile.read().replace('call ninja.exe', 'call ' + Settings.localNinjaPath)
            with open(os.path.join(root,file), 'w') as projectFile:
              projectFile.write(updatedProject)
