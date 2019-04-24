import os
import shutil 
import glob

import config
from logger import Logger
from settings import Settings
from utility import Utility
from system import System
import errors
from errors import error_codes, NO_ERROR
from helper import convertToPlatformPath

class Cleanup:
  @classmethod
  def init(cls):
    """
      Inits logger
    """
    cls.logger = Logger.getLogger('Cleanup')

  @classmethod
  def cleanOutput(cls, target='*', platform='*', cpu='*', configuration='*'):
    """
      Deletes output folders.
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return ret: NO_ERROR if output folders deletion was successful. Otherwise returns error code.
    """
    ret = NO_ERROR

    if target == '': target = '*'
    if platform == '': platform = '*'
    if cpu == '': cpu = '*'
    if configuration == '': configuration = '*'

    #Switch working directory to root webrtc folder
    Utility.pushd(Settings.webrtcPath)
    foldersToDelete = list()

    #Generate path name for deletion from gn output folder, based on template from config. 
    #Path can contain * chars i.e. to delete output folder for all CPUs for specific target ./out/webrtc_winuwp_*_Debug
    gnFolderToClean = config.GN_TARGET_OUTPUT_PATH.replace('[GN_OUT]', config.GN_OUTPUT_PATH).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration)
    #Generate folder name for deletion from output folder, based on template from config
    outputFolderToClean = convertToPlatformPath(config.BUILT_LIBS_DESTINATION_PATH.replace('[BUILD_OUTPUT]',config.BUILD_OUTPUT_PATH).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration))
    
    #Convert path to host os style, and add all folders that satisfy condition for deletion to the foldersToDelete list
    for folderPath in glob.iglob(convertToPlatformPath(gnFolderToClean)):
      foldersToDelete.append(folderPath)
    
    #Convert path to host os style, and add all folders that satisfy condition for deletion to the foldersToDelete list
    for folderPath in glob.iglob(convertToPlatformPath(outputFolderToClean)):
      foldersToDelete.append(folderPath)

    #Delete all folders marked for deletion
    if not Utility.deleteFolders(foldersToDelete):
      ret = errors.ERROR_CLEANUP_DELETING_OUTPUT_FAILED

    Utility.popd()

    if ret == NO_ERROR and Settings.buildWrapper:
      ret = cls.cleanWrapperProjects(target, platform, cpu, configuration)

    return ret

  @classmethod
  def cleanWrapperProjects(cls, cleanupTarget='*', cleanupPlatform='*', cleanupCpu='*', configuration='*'):
    """
      Cleans wrapper projects.
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return ret: NO_ERROR if output folders deletion was successful. Otherwise returns error code.
    """
    ret = NO_ERROR

    if cleanupTarget == '*':
      targets = Settings.targets
    else:
      targets = [cleanupTarget]

    if cleanupPlatform == '*':
      platforms = Settings.targetPlatforms
    else:
      platforms = [cleanupPlatform]

    if cleanupCpu == '*':
      cpus = Settings.targetCPUs
    else:
      cpus = [cleanupCpu]

    for target in targets:
      for platform in platforms:
        #Get solution to clean, for specified target and platform. Solution is obtained from config.TARGET_WRAPPER_SOLUTIONS
        solutionName = convertToPlatformPath(Utility.getValueForTargetAndPlatformDict(config.TARGET_WRAPPER_SOLUTIONS, target, platform))

        #If solution is not provided, return True like it was succefull
        if solutionName == '':
          cls.logger.warning('Solution with wrapper projects is not specified in config!')
          continue

        for cpu in cpus:
          #Set the PATH and environment variables for command-line builds (e.g. vcvarsall.bat x64_x86)
          cls.cmdVcVarsAll = '\"' +  Settings.vcvarsallPath + '\" ' + config.WINDOWS_COMPILER_OPTIONS[System.hostCPU][cpu]
          cls.cmdVcVarsAllClean = '\"' +  Settings.vcvarsallPath + '\" ' + '/clean_env'

          try:
            #Solution template path
            solutionSourcePath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_TEMPLATES_PATH),solutionName)
            #Path where solution template will be copied
            solutionDestinationPath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_PATH),solutionName)
            
            #Copy template solution to solution folder
            if not Utility.copyFile(solutionSourcePath,solutionDestinationPath):
              return errors.ERROR_CLEANUP_DELETING_OUTPUT_WRAPPER_FAILED

            if (configuration != '*'):
              configurationPart = ' /p:Configuration=\"' + configuration + '\"'
            else:
              configurationPart = ''

            if (cpu != '*'):
              cpuPart =  ' /p:Platform=\"' + cpu + '\"'
            else:
              cpuPart = ''
              
            #MSBuild command for building wrapper projects
            cmdBuild = 'msbuild ' + solutionDestinationPath + ' /t:Clean' + configurationPart + cpuPart
            #Execute MSBuild command
            result = Utility.runSubprocess([cls.cmdVcVarsAll, cmdBuild, cls.cmdVcVarsAllClean], Settings.logLevel == 'DEBUG')
            if result != NO_ERROR:
              ret = errors.ERROR_CLEANUP_DELETING_OUTPUT_WRAPPER_FAILED
              cls.logger.error('Failed cleaning ' + target + ' wrapper projects for ' + cpu + ' for configuration  '+ configuration)
          except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error('Failed cleaning ' + target + ' wrapper projects for ' + cpu + ' for configuration  '+ configuration)
            ret = errors.ERROR_CLEANUP_DELETING_OUTPUT_WRAPPER_FAILED
          finally:
            #Delete solution used for building wrapper projects.
            Utility.deleteFiles([solutionDestinationPath])

    return ret

  @classmethod
  def cleanUserDef(cls):
    """
      Recreates userdef.py file.
      :return ret: NO_ERROR if useddef.py is recreated successfully. Otherwise returns error code.
    """
    ret = System.recreateUserDef()

    return ret

  @classmethod
  def cleanIdls(cls):
    """
      Deletes .flg and files generated by idl compiler.
      :return ret: NO_ERROR if .flg and generated files are deleted successfully. Otherwise returns error code.
    """
    ret = NO_ERROR

    #Switch working directory to root webrtc folder
    Utility.pushd(Settings.webrtcPath)

    #Remove .flg files that are used like flags for successfully generated files by idl compiler.
    if os.path.exists(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH)):
      for flgFilePath in glob.iglob(os.path.join(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH), '*.flg')):
        result = Utility.deleteFiles([flgFilePath])
        if not result:
          ret = errors.ERROR_CLEANUP_DELETING_FLG_FILES_FAILED
          break
    
    if ret == NO_ERROR:
      #Removed files generated by idl compiler.
      if not Utility.deleteFolders([convertToPlatformPath(config.IDL_GENERATED_FILES_OUTPUT_PATH)]):
        ret = errors.ERROR_CLEANUP_DELETING_GENERATED_FILES_FAILED

    Utility.popd()

    return ret

  @classmethod
  def cleanPrepare(cls):
    """
      Remove all changes made during preparation process
      :return ret: NO_ERROR if all changes done in preparation are removed successfully. Otherwise returns error code.
    """
    ret = NO_ERROR
      
    #Switch working directory to root webrtc folder.
    Utility.pushd(Settings.webrtcPath)

    #Remove all files copied during preparation process.
    for destination in [val for d in config.FILES_TO_COPY for val in d.values()]:
        if not Utility.deleteFiles([destination]):
          ret = errors.ERROR_CLEANUP_REVERTING_PREPARE_CHANGES_FAILED

    if ret == NO_ERROR:
      #Remove links created for Ortc target.
      if not Utility.deleteFolderLinks(config.FOLDERS_TO_LINK_ORTC):
        ret = errors.ERROR_CLEANUP_REVERTING_PREPARE_CHANGES_FAILED
    
    if ret == NO_ERROR:
      #Delete created folders for Ortc target.
      if not Utility.deleteFolders(config.FOLDERS_TO_GENERATE_ORTC):
        ret = errors.ERROR_CLEANUP_REVERTING_PREPARE_CHANGES_FAILED

    if ret == NO_ERROR:
      #Remove links created for WebRtc target
      if not Utility.deleteFolderLinks(config.FOLDERS_TO_LINK):
        ret = errors.ERROR_CLEANUP_REVERTING_PREPARE_CHANGES_FAILED

    if ret == NO_ERROR:
      #Delete created folders for WebRtc target
      if not Utility.deleteFolders(config.FOLDERS_TO_GENERATE):
        ret = errors.ERROR_CLEANUP_REVERTING_PREPARE_CHANGES_FAILED
      
    Utility.popd()

    return ret

  @classmethod
  def run(cls, action, target='*', platform='*', cpu='*', configuration='*'):
    """
      Performs cleanup for provided action and specific imput arguments.
      :param action: Action to perform (cleanOutput, cleanUserDef, cleanIdls or cleanPrepare)
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return ret: NO_ERROR if clean was successful. Otherwise returns error code.
    """
    ret = NO_ERROR

    if action.lower() == 'cleanoutput':
      ret = cls.cleanOutput(target, platform, cpu, configuration)

    if action.lower() == 'cleanuserdef':
      ret = cls.cleanUserDef()

    if action.lower() == 'cleanidls':
      ret = cls.cleanIdls()

    if action.lower() == 'cleanprepare':
      ret = cls.cleanPrepare()

    if ret == NO_ERROR:
      cls.logger.info('Cleanup action ' + action + ' is finished successfully for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration)
    else:
      cls.logger.error(error_codes[ret])
      cls.logger.error('Cleanup action ' + action + ' has failed for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration)
    return ret
    