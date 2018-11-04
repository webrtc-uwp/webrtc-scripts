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
    if not os.path.exists(Settings.preparationWorkingPath):
      System.stopExecution(1, 'Unable to set preparation working directory')

    #Create missing folders and links
    try:
      Utility.pushd(Settings.preparationWorkingPath)

      Utility.createFolders(config.FOLDERS_TO_GENERATE)
      Utility.createFolderLinks(config.FOLDERS_TO_LINK)

      #In case ortc is one of the targets create specific folders and links
      if (ortc):
        Utility.createFolders(config.FOLDERS_TO_GENERATE_ORTC)
        Utility.createFolderLinks(config.FOLDERS_TO_LINK_ORTC)

      Utility.copyFilesFromDict(config.FILES_TO_COPY)
    except Exception, errorMessage:
      cls.logger.error(errorMessage)
    finally:
      Utility.popd()
    
  @classmethod
  def run(cls, target, platform, cpu, configuration):

    cls.logger.info('Runnning preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    Utility.pushd(Settings.preparationWorkingPath)

    #Create output folder where will be saved webrtc generated projects
    gnOutputPath = os.path.join('out', target + '_' + platform + '_' + cpu + '_' + configuration)
    if not os.path.exists(gnOutputPath):
      cls.logger.debug('Making ' + gnOutputPath + ' directory.')
      os.makedirs(gnOutputPath)

    #Copy args.gn template file to output folder
    argsPath = os.path.join(gnOutputPath, 'args.gn')
    cls.logger.debug('Copying ' + argsPath + ' file' + ' to ' + Settings.webRTCGnArgsTemplatePath )
    copyfile(Settings.webRTCGnArgsTemplatePath, argsPath)

    #Update target os and cpu in copied args,gn file
    with open(argsPath) as argsFile:
      cls.logger.debug('Updating args.gn file. Target OS: ' + platform + '; Target CPU: ' + cpu)
      newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu).replace('-is_debug-',str(configuration.lower() == 'debug').lower())
    with open(argsPath, 'w') as argsFile:
      argsFile.write(newArgs)
    
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
    except Exception, errorMessage:
      cls.logger.error(str(errorMessage))
      System.stopExecution(ERROR_PREPARE_GN_GENERATION_FAILED)
    finally:
      Utility.popd()
    
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
              #updatedProject=projectFile.read().replace('call ninja.exe', 'call ' + os.path.join(Settings.localDepotToolsPath,'ninja.exe'))
            with open(os.path.join(root,file), 'w') as projectFile:
              projectFile.write(updatedProject)

  
