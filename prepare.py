import os
import subprocess
import time
from shutil import copyfile

import config
from utility import Utility
from settings import Settings
from system import System
from logger import Logger
from helper import convertToPlatformPath, iterateDict, bool_to_str
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

      #Copy all files from specified folder (key) to destination (value)
      for dict in config.FOLDERS_CONTENT_TO_COPY:
        for key, value in iterateDict(dict):
          result = Utility.copyAllFilesFromFolder(convertToPlatformPath(key), convertToPlatformPath(value))
          if not result:
            ret = errors.ERROR_PREPARE_COPYING_FILES_FAILED
            break
      
      #Copy files whose paths and destinations are in dictionary { file_path : destination_path }
      if not Utility.copyFilesFromDict(config.FILES_TO_COPY) and ret == NO_ERROR:
        ret = errors.ERROR_PREPARE_COPYING_FILES_FAILED

      #If win is one of the selected platforms it is required to have clang-cl.
      #It is called here becuae proper folders structure is required to execute update script
      if not System.downloadClangClIfMissing() and ret == NO_ERROR:
         ret = errors.ERROR_PREPARE_INSTALLING_CLANG_FAILED
        
      #Download missing build tools
      if not System.downloadBuildToolsIfNeeded() and ret == NO_ERROR:
        ret = errors.ERROR_PREPARE_INSTALLING_CLANG_FAILED
      
      if ret == NO_ERROR:
        ret = cls.__updateChangeTimeStamp()
      
    except Exception as error:
      ret = errors.ERROR_PREPARE_SET_UP_FAILED
      cls.logger.error(str(error))
    finally:
      #Remove logger handlers added in third party scripts. (e.g. Google's lastchange.py)
      Logger.cleanThirdPartyLoggers()
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

    cls.logger.info('Runnning preparation for target: ' + target + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    # if we're trying to do a full build, we need some resources
    if target == 'default':
      rcPath = os.path.join(Settings.webrtcPath, 'build/toolchain/win')
      status = System.downloadFromGoogle('chromium-browser-clang/rc', rcPath, True, True)
      if not status:
        ret = errors.ERROR_PREPARE_DOWNLOADING_TOOLS_FAILED
      resourcesPath = os.path.join(Settings.webrtcPath, 'resources')
      status = System.downloadFromGoogle('chromium-webrtc-resources', resourcesPath, True, True)
      if not status:
        ret = errors.ERROR_PREPARE_DOWNLOADING_TOOLS_FAILED

    #Change working directory
    Utility.pushd(Settings.webrtcPath)

    #Create output folder where webrtc generated projects will be saved 
    gnOutputPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH,target,platform,cpu,configuration)
    ret = cls.__prepareOutputFolder(gnOutputPath, target, platform, cpu, configuration)

    if ret == NO_ERROR:
      
      #Backup original BUILD.gn from webrtc root folder and add additional dependecies to webrtc target
      if Utility.backUpAndUpdateGnFile(Settings.mainBuildGnFilePath,config.WEBRTC_TARGET,config.ADDITIONAL_TARGETS_TO_ADD):
        #Generate ninja files and VS projects
        ret = cls.__generateProjects(gnOutputPath)
      else:
        ret = errors.ERROR_PREPARE_UPDATING_DEPS_FAILED

    #Delete updated BUILD.gn from webrtc root folder and recover original file
    Utility.returnOriginalFile(Settings.mainBuildGnFilePath)

    #If unit test projects are generated, copy missing dlls 
    if Settings.includeTests and platform == 'winuwp':
      cls.copyAppRuntimeDlls(cpu,configuration,gnOutputPath)

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
        newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu)
        newArgs=newArgs.replace('-is_debug-',str(configuration.lower() == 'debug').lower())
        newArgs=newArgs.replace('-is_clang-',bool_to_str(Settings.buildWithClang).lower())
        newArgs=newArgs.replace('-std_cpp17-',bool_to_str(Settings.buildWithCpp17).lower())
        newArgs=newArgs.replace('-is_include_tests-', bool_to_str(Settings.includeTests).lower())
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
      cmd = 'gn gen ' + gnOutputPath + ' --ide=' + config.VISUAL_STUDIO_VERSION + ' -v'
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

  @classmethod
  def __updateChangeTimeStamp(cls):
    """
      Creates or uptades LASTCHANGE.committime, required by gn.
      :return ret: NO_ERROR if timestamp is successfully updated. Otherwise error code.
    """
    ret = NO_ERROR

    try:
      lastchangeModulePath = convertToPlatformPath(config.LAST_CHANGE_MODULE_PATH)
      Utility.pushd(lastchangeModulePath)

      Utility.addModulePath(os.getcwd())
      
      import lastchange

      lastchange.main(['','-o','LASTCHANGE'])

    except Exception as error:
      ret = errors.ERROR_PREPARE_UPDATING_TIMESTEMP_FAILED
      cls.logger.error(str(error))
    finally:
      Utility.popd()

    return ret

  @classmethod
  def copyAppRuntimeDlls(cls, cpu, configuration, destinatioPath):
    """

    """
    #runtimeDllsInPlace = True

    #Check if app dlls are already in place
    ##for file in config.RUNTIME_STORE_DLLS[configuration]:
    ##  destinationFile =  os.path.join(destinatioPath, file)
    ##  runtimeDllsInPlace = runtimeDllsInPlace and os.path.isfile(destinationFile)


    #if runtimeDllsInPlace:
    #  return runtimeDllsInPlace

    if Utility.checkIfFolderContainsFiles(destinatioPath, config.RUNTIME_STORE_DLLS[configuration]):
      return True

    listOfFilesToSearch = config.RUNTIME_STORE_DLLS[configuration]
    programFilesPath = os.environ['ProgramFiles']
    windowsAppPath = os.path.join(programFilesPath, 'WindowsApps\\')
    mainVersionNumber = Settings.msvcToolsVersion.split('.')[0]
    buildVersionNumber = Settings.msvcToolsVersion.split('.')[-1]
    counter = 1
    #Copy dlls from VC tools folder from WindowsApp folder
    while counter >= 0 and len(listOfFilesToSearch) > 0: 
      pathToUse = config.VC_LIBS_STORE_PATH.replace('[MAIN_VERSION_NUMBER]',mainVersionNumber).replace('[BUILD_VERSION_NUMBER]',buildVersionNumber).replace('[COUNTER]',str(counter)).replace('[CPU]',cpu)
      windowsAppPath = os.path.join(windowsAppPath,pathToUse)
      if os.path.isdir(windowsAppPath):    
        for root, dirs, files in os.walk(windowsAppPath):
          for file in files:
            if file in config.RUNTIME_STORE_DLLS[configuration]:
              if cpu in root:
                counter=-1
                sourceFile =  os.path.join(root, file)
                destinationFile =  os.path.join(destinatioPath, file)
                if not os.path.isfile(destinationFile) and (Utility.copyFile(sourceFile,destinationFile)):
                  cls.logger.debug('Copied ' + sourceFile + ' to ' + destinationFile)
                  listOfFilesToSearch.remove(file)
      else:
        cls.logger.warning('Folder ' + windowsAppPath + ' doesn\'t exist!')
        counter -= 1

    #If VC tools folder and app dlls are not found, duplicate existing VC dlls and rename it
    if len(listOfFilesToSearch) > 0:
      for file in config.RUNTIME_STORE_DLLS[configuration]:
        sourceFile =  os.path.join(destinatioPath, file.replace('_app',''))
        destinationFile =  os.path.join(destinatioPath, file)
        if not os.path.isfile(destinationFile) and (Utility.copyFile(sourceFile,destinationFile)):
          cls.logger.debug('Copied ' + sourceFile + ' to ' + destinationFile)
          listOfFilesToSearch.remove(file)

    if len(listOfFilesToSearch) > 0:
      cls.logger.warning('Following dlls are not found: ' + ''.join([file for file in listOfFilesToSearch]))
      return False

    return True
    