import os
import subprocess
import time
from shutil import copyfile

import config
from utility import Utility
from settings import Settings
from system import System
from logger import Logger
from helper import convertToPlatformPath
import errors
from errors import NO_ERROR

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
    ret = NO_ERROR

    #Create logger
    cls.logger = Logger.getLogger('Prepare')

    #Set working directory to ./webrtc/xplatform/webrtc
    if not os.path.exists(Settings.webrtcPath):
      System.stopExecution(1, 'Unable to set preparation working directory')

    #Create missing folders and links
    try:
      #Change working directory
      Utility.pushd(Settings.webrtcPath)

      if not Utility.createFolders(config.FOLDERS_TO_GENERATE):
        ret =  errors.ERROR_PREPARE_CREATING_FOLDERS_FAILED

      if not Utility.createFolderLinks(config.FOLDERS_TO_LINK) and ret == NO_ERROR:
        ret =  errors.ERROR_PREPARE_CREATING_LINKS_FAILED

      #In case ortc is one of the targets create specific folders and links
      if (ortc):
        if not Utility.createFolders(config.FOLDERS_TO_GENERATE_ORTC) and ret == NO_ERROR:
          ret = errors.ERROR_PREPARE_CREATING_FOLDERS_FAILED
        if not Utility.createFolderLinks(config.FOLDERS_TO_LINK_ORTC) and ret == NO_ERROR:
          ret = errors.ERROR_PREPARE_CREATING_LINKS_FAILED

      #Copy files whose paths and destinations are in dictionary { file_path : destination_path }
      if not Utility.copyFilesFromDict(config.FILES_TO_COPY) and ret == NO_ERROR:
        ret = errors.ERROR_PREPARE_COPYING_FILES_FAILED

      #If win is one of the selected platforms it is required to have clang-cl.
      #It is called here becuae proper folders structure is required to execute update script
      if 'win' in Settings.targetPlatforms:
        if not System.downloadClangClIfMissing() and ret == NO_ERROR:
         ret = errors.ERROR_PREPARE_INSTALLING_CLANG_FAILED
        
      #Download missing build tools
      if not System.downloadBuildToolsIfNeeded() and ret == NO_ERROR:
        ret = errors.ERROR_PREPARE_INSTALLING_CLANG_FAILED

    except Exception as error:
      ret = errors.ERROR_PREPARE_SET_UP_FAILED
      cls.logger.error(str(error))
    finally:
      Utility.popd()

    return ret
    
  @classmethod
  def run(cls, target, platform, cpu, configuration):
    """
      Start environment preparation for specified target.
      :param target: Name of the target
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration to build for
      :return ret: NO_ERROR if preparation was successfull. Otherwise returns error code.
    """
    start_time = time.time()
    ret = NO_ERROR
    cls.executionTime = 0
    mainBuildGnFilePath = None

    cls.logger.info('Runnning preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #Change working directory
    Utility.pushd(Settings.webrtcPath)

    #Create output folder where webrtc generated projects will be saved 
    gnOutputPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH,target,platform,cpu,configuration)
    ret = cls.__prepareOutputFolder(gnOutputPath, target, platform, cpu, configuration)

    if ret == NO_ERROR:
      mainBuildGnFilePath = os.path.join(Settings.webrtcPath,'BUILD.gn')
      
      #Backup original BUILD.gn from webrtc root folder and add additional dependecies to webrtc target
      if Utility.backUpAndUpdateGnFile(mainBuildGnFilePath,config.WEBRTC_TARGET,config.ADDITIONAL_TARGETS_TO_ADD):
        #Generate ninja files and VS projects
        ret = cls.__generateProjects(gnOutputPath)
      else:
        ret = errors.ERROR_PREPARE_UPDATING_DEPS_FAILED

    #Delete updated BUILD.gn from webrtc root folder and recover original file
    if mainBuildGnFilePath != None:
      Utility.returnOriginalFile(mainBuildGnFilePath)
    Utility.popd()
    
    if ret == NO_ERROR:
      cls.logger.info('Successfully finished preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)
    
    end_time = time.time()
    cls.executionTime = end_time - start_time
    return ret
    
  #---------------------------------- Private methods --------------------------------------------
  @classmethod
  def __prepareOutputFolder(cls, gnOutputPath, target, platform, cpu, configuration):
    """
      Creates gn output folders. Copies args.gn tamplate file into output folders.
      Updates args.gn file with specified platform, cpu and configuration,
      :param outputFolderPath: Gn output folder where generated ninja files and projects will be saved.
      :param target: Name of the target
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration to build for
      :return ret: NO_ERROR if preparation was successfull. Otherwise returns error code.
    """
    ret = NO_ERROR
    
    try:
      #Full path to args.gn template file
      argsTemplatePath = os.path.join(Settings.rootSdkPath, convertToPlatformPath(config.WEBRTC_GN_ARGS_TEMPLATE_PATH))

      if not os.path.exists(gnOutputPath):
        cls.logger.debug('Making ' + gnOutputPath + ' directory.')
        os.makedirs(gnOutputPath)

      #Copy args.gn template file to output folder
      argsPath = os.path.join(gnOutputPath, 'args.gn')
      cls.logger.debug('Copying ' + argsPath + ' file' + ' to ' + argsTemplatePath )
      copyfile(argsTemplatePath, argsPath)

      #Update target platform and cpu in copied args.gn file
      with open(argsPath) as argsFile:
        cls.logger.debug('Updating args.gn file. Target OS: ' + platform + '; Target CPU: ' + cpu)
        newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu).replace('-is_debug-',str(configuration.lower() == 'debug').lower())
      with open(argsPath, 'w') as argsFile:
        argsFile.write(newArgs)
    except Exception as error:
      cls.logger.error(str(error))
      ret = errors.ERROR_PREPARE_OUTPUT_FOLDER_PREPARATION_FAILED

    return ret

  @classmethod
  def __generateProjects(cls, gnOutputPath):
    """
      Generates ninja files and VS projects.
      :param gnOutputPath: Gn output path where will be saved generated ninja files and VS projects.
      :return ret: NO_ERROR if preparation was successfull. Otherwise returns error code.
    """
    ret = NO_ERROR
    try:
      #Duplicate existing environment variables
      my_env = os.environ.copy()
      #Add new environment variable, required by gn for project generation
      my_env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"  

      cls.logger.debug('Output path: ' + gnOutputPath)
      cls.logger.info('Generating webrtc projects ...')

      #Generate Webrtc projects
      cmd = 'gn gen ' + gnOutputPath + ' --ide=' + config.VISUAL_STUDIO_VERSION
      result = Utility.runSubprocess([cmd], Settings.logLevel == 'DEBUG',my_env)
      if result != 0:
        ret = errors.ERROR_PREPARE_GN_GENERATION_FAILED
        cls.logger.error('Projects generation has failed!')
      else:
        #Update ninja path in VS project files to point to ninja.exe in local depot_tools folder
        cls.__updateNinjaPathinProjects(gnOutputPath)
    except Exception as error:
      cls.logger.error(str(error))
      ret = errors.ERROR_PREPARE_GN_GENERATION_FAILED

    return ret

  @classmethod
  def __updateNinjaPathinProjects(cls,folder):
    """
      Updates ninja.exe path in VS projects.
      :param folder: Root folder where starts search for all vcxproj that are calling ninja.exe
    """
    for root, dirs, files in os.walk(folder):
      for file in files:
        if file.endswith('.vcxproj'):
          try:
            #cls.logger.debug('Updating ninja path in VS project file ' + file)
            #Replace 'call ninja.exe' with 'call local_depot_tools_path\ninja.exe'
            with open(os.path.join(root,file)) as projectFile:
              updatedProject=projectFile.read().replace('call ninja.exe', 'call ' + Settings.localNinjaPath)
            with open(os.path.join(root,file), 'w') as projectFile:
              projectFile.write(updatedProject)
          except Exception as error:
            cls.logger.warning(str(error))
