import os
import subprocess
from shutil import copyfile

import config
import defaults
from utility import Utility
from settings import Settings
from system import System
from logger import Logger


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
    if not Utility.changeWorkingDir(os.path.join(Settings.rootSdkPath, Utility.convertToPlatformPath(config.PREPRATARION_WORKING_PATH))):
      System.stopExecution(1, 'Unable to set preparation working directory')
    
    #Create missing folders and links
    try:
      Utility.createFolders(config.FOLDERS_TO_GENERATE)
      Utility.createFolderLinks(config.FOLDERS_TO_LINK)

      #In case ortc is one of the targets create specific folders and links
      if (ortc):
        Utility.createFolders(config.FOLDERS_TO_GENERATE_ORTC)
        Utility.createFolderLinks(config.FOLDERS_TO_LINK_ORTC)

      Utility.copyFiles(config.FILES_TO_COPY)
    except Exception, errorMessage:
      cls.logger.error(errorMessage)
    
  @classmethod
  def run(cls, target, platform, cpu, configuration):

    cls.logger.info('Runnning preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #Create output folder where will be saved webrtc generated projects
    gnOutputPath = os.path.join('out', target + '_' + platform + '_' + cpu + '_' + configuration)
    if not os.path.exists(gnOutputPath):
      os.makedirs(gnOutputPath)

    #Copy args.gn template file to output folder
    argsPath = os.path.join(gnOutputPath, 'args.gn')
    copyfile(defaults.webRTCGnArgsTemplatePath, argsPath)

    #Update target os and cpu in copied args,gn file
    with open(argsPath) as argsFile:
      newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu).replace('-is_debug-',str(configuration.lower() == 'debug').lower())
    with open(argsPath, 'w') as argsFile:
      argsFile.write(newArgs)
    
    #Generate Webrtc projects
    try:
      os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
      result = subprocess.call([
        'gn',
        'gen',
        gnOutputPath,
        '--ide=' + config.VISUAL_STUDIO_VERSION,
      ])

      if result != 0:
        cls.logger.error('Projects generation has failed! ($target, $platform, $cpu, $configuration)')
      else:
        #Update ninja path in VS project files to point to ninja.exe in local depot_tools folder
        cls.updateNinjaPathinProjects(gnOutputPath)
        cls.logger.info('Successfully finished preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)
    except Exception, errorMessage:
      cls.logger.error(errorMessage)
    
  @classmethod
  def updateNinjaPathinProjects(cls,folder):
    for root, dirs, files in os.walk(folder):
      for file in files:
          if file.endswith('.vcxproj'):
            cls.logger.debug('Updating ninja path in VS project file ' + file)
            #Replace 'call ninja.exe' with 'call local_depot_tools_path\ninja.exe'
            with open(os.path.join(root,file)) as projectFile:
              updatedProject=projectFile.read().replace('call ninja.exe', 'call ' + os.path.join(Settings.localDepotToolsPath,'ninja.exe'))
            with open(os.path.join(root,file), 'w') as projectFile:
              projectFile.write(updatedProject)

  
