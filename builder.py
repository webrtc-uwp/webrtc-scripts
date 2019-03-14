import os
import subprocess
import shutil 
import signal
import time
from datetime import datetime

import config
from logger import Logger
from system import System
from utility import Utility
from settings import Settings
from helper import convertToPlatformPath
import errors
from errors import error_codes, NO_ERROR
from nugetUtility import NugetUtility

class Builder:
  @classmethod
  def init(cls):
    """
      Initiates logger object.
    """
    cls.logger = Logger.getLogger('Build')

  @classmethod
  def run(cls, targetName, targets, platform, cpu, configuration, shouldCombineLibs = False, shouldCopyToOutput = True, builderWorkingPath = None):
    """
      Start target building process.
      :param targetName: Name of the main target (ortc or webrtc)
      :param targets: List of the targets to build
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration to build for
      :param shouldCombineLibs: Should all libs be merged into one library
      :param shouldCopyToOutput: should copy libs, exes and pdbs to output folder.
      :param builderWorkingPath: Path where generated projects for specified target.
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    start_time = time.time()
    ret = NO_ERROR
    cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #If path with generated projects is not specified generate path from input arguments
    if builderWorkingPath == None:
      builderWorkingPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH, targetName, platform, cpu, configuration)#os.path.join('out', targetName + '_' + platform + '_' + cpu + '_' + configuration)

    workingDir = os.path.join(Settings.webrtcPath,builderWorkingPath)

    #If folder for specified target and platform doesn't exist, stop further execution
    if not os.path.exists(workingDir):
      cls.logger.error('Output folder at ' + workingDir + ' doesn\'t exist. It looks like prepare is not executed. Please run prepare action.')
      return errors.ERROR_BUILD_OUTPUT_FOLDER_NOT_EXIST
    
    #Set the PATH and environment variables for command-line builds (e.g. vcvarsall.bat x64_x86)
    cls.cmdVcVarsAll = '\"' +  Settings.vcvarsallPath + '\" ' + config.WINDOWS_COMPILER_OPTIONS[System.hostCPU][cpu]
    cls.cmdVcVarsAllClean = '\"' +  Settings.vcvarsallPath + '\" ' + '/clean_env'

    #Change current working directory to one with generated projects
    Utility.pushd(workingDir)

    if Settings.logLevel == 'DEBUG':
      System.logEnvIncludeAndLibPaths(platform,cpu,'.')
    #Start building and merging libraries
    ret = cls.buildTargets(targets, cpu)

    if ret == NO_ERROR:
      destinationPath = convertToPlatformPath(config.BUILT_LIBS_DESTINATION_PATH.replace('[BUILD_OUTPUT]',config.BUILD_OUTPUT_PATH).replace('[TARGET]',targetName).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration))
      destinationPathLib = os.path.join(Settings.webrtcPath, destinationPath)

      #Merge libraries if it is required. Merged lib is saved in destinationPathLib
      if shouldCombineLibs:
        ret = cls.mergeLibs(cpu,destinationPathLib)
      elif shouldCopyToOutput:
        #Copy lib files to the destinationPathLib folder
        ret = cls.copyFilesToOutput(destinationPathLib, 'lib', config.COMBINE_LIB_IGNORE_SUBFOLDERS)
      
      if ret == NO_ERROR and shouldCopyToOutput:
        #Copy executable files to the destinationPathLib folder
        cls.copyFilesToOutput(destinationPathLib, 'exe', config.COMBINE_LIB_IGNORE_SUBFOLDERS, 'executables')

        #Copy pdb files to the destinationPathLib folder
        cls.copyFilesToOutput(destinationPathLib, 'pdb', config.COMBINE_LIB_IGNORE_SUBFOLDERS, 'pdbs')

    #Switch to previously working directory
    Utility.popd()
  
    #Build wrapper library if option is enabled
    if Settings.buildWrapper and ret == NO_ERROR:
      ret = cls.buildWrapper(targetName ,platform, cpu, configuration)

    if ret == NO_ERROR:
      cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration + ', finished successfully!')
    end_time = time.time()
    cls.executionTime = end_time - start_time
    return ret

  @classmethod
  def buildWrapper(cls, target, platform, targetCPU, configuration):
    """
      Builds wrapper projects.
      :param target: Name of the main target (ortc or webrtc)
      :param platform: Platform name
      :param targetCPU: Target CPU
      :param configuration: Configuration to build for
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    ret = NO_ERROR
    cls.logger.info('Building ' + target + ' wrapper projects for ' + targetCPU + ' for configuration  '+ configuration)

    #Get solution to build, for specified target and platform. Solution is obtained from config.TARGET_WRAPPER_SOLUTIONS
    solutionName = convertToPlatformPath(Utility.getValueForTargetAndPlatformDict(config.TARGET_WRAPPER_SOLUTIONS, target, platform))

    #If solution is not provided, return True like it was succefull
    if solutionName == '':
      cls.logger.warning('Solution with wrapper projects is not specified in config!')
      return NO_ERROR

    try:
      #Solution template path
      solutionSourcePath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_TEMPLATES_PATH),solutionName)
      #Path where solution template will be copied
      solutionDestinationPath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_PATH),solutionName)
      
      #Copy template solution to solution folder
      if not Utility.copyFile(solutionSourcePath,solutionDestinationPath):
        return errors.ERROR_BUILD_BUILDING_WRAPPER_FAILED

      #Restore nugets
      cmdBuild = Settings.nugetExecutablePath + ' restore ' + solutionDestinationPath
      result = NugetUtility.nuget_cli('restore', solutionDestinationPath)
      #result = Utility.runSubprocess([cmdBuild], Settings.logLevel == 'DEBUG')
      if result == NO_ERROR:
        #MSBuild command for building wrapper projects
        cmdBuild = 'msbuild ' + solutionDestinationPath + ' /t:Build' + ' /p:Configuration=\"' + configuration + '\" /p:Platform=\"' + targetCPU + '\"'
        #Execute MSBuild command
        result = Utility.runSubprocess([cls.cmdVcVarsAll, cmdBuild, cls.cmdVcVarsAllClean], Settings.logLevel == 'DEBUG')
        if result != NO_ERROR:
          ret = errors.ERROR_BUILD_BUILDING_WRAPPER_FAILED
          cls.logger.error('Failed building ' + target + ' wrapper projects for ' + targetCPU + ' for configuration  '+ configuration)
      else:
        ret = errors.ERROR_BUILD_RESTORING_NUGET_FAILED
    except Exception as error:
      cls.logger.error(str(error))
      cls.logger.error('Failed building ' + target + ' wrapper projects for ' + targetCPU + ' for configuration  '+ configuration)
      ret = errors.ERROR_BUILD_BUILDING_WRAPPER_FAILED
    finally:
      #Delete solution used for building wrapper projects.
      Utility.deleteFiles([solutionDestinationPath])

    if ret == NO_ERROR:
      cls.logger.info('Successfully finished building wrappers for target ' + target)

    return ret

  @classmethod
  def buildTargets(cls, targets, targetCPU):
    """
      Build list of targets for specified cpu.
      :param targets: List of targets to build.
      :param targetCPU: Target CPU.
      :return ret: NO_ERROR if preparation was successfull. Otherwise returns error code.
    """
    ret = NO_ERROR
    cls.logger.info('Following targets ' + str(targets) + ' will be built for cpu '+ targetCPU)

    try:
      for target in targets:
        cls.logger.debug('Building target ' + target)
        my_env = os.environ.copy()
        my_env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
        
        #Used to set pass impl flag to idl compiler
        if Settings.enableIdlImpl:
          my_env['IDL_COMPILER_IMPL'] = "1" 

        #Backup original BUILD.gn from webrtc root folder and add additional dependecies to webrtc target.
        #This is necessary to do, because ninja regenerates ninja files at startup, and it is required 
        # to have the sam BUILD.gn as in prepare process.
        if target == config.WEBRTC_TARGET:
          if not Utility.backUpAndUpdateGnFile(Settings.mainBuildGnFilePath,config.WEBRTC_TARGET,config.ADDITIONAL_TARGETS_TO_ADD):
            ret = errors.ERROR_BUILD_UPDATING_DEPS_FAILED

        if ret == NO_ERROR:
          #Run ninja to build targets
          cmd = Settings.localNinjaPath + '.exe ' +  target
          result = Utility.runSubprocess([cmd], Settings.logLevel == 'DEBUG', my_env)
          if result != 0:
            ret = errors.ERROR_BUILD_FAILED

    except Exception as error:
      cls.logger.error(str(error))
      cls.logger.error('Build failed for following targets ' + str(targets) + ' for cpu '+ targetCPU)
      ret = errors.ERROR_BUILD_FAILED
    finally:
      Utility.returnOriginalFile(Settings.mainBuildGnFilePath)

    if ret == NO_ERROR:
      cls.logger.info('Successfully finished building target ' + target)

    return ret

  @classmethod
  def mergeLibs(cls, targetCPU, destinationPath):
    """
      Merges obj files and creates fat webrtc library.
      :param targetCPU: Target CPU.
      :param destinationPath: Folder path where will be saved merged lib.
      :return ret: NO_ERROR if merge is completed successfully. Otherwise returns error code.
    """
    ret = NO_ERROR
    cls.logger.info('Merging libs for cpu '+ targetCPU)

    #Determine lib.exe path
    cls.libexePath = os.path.join(Settings.msvcToolsBinPath, targetCPU, 'lib.exe')
    
    if not os.path.isfile(cls.libexePath):
      cls.logger.error('Merging libraries cannot be done. Missing file ' + cls.libexePath + '!')
      cls.logger.warning('Please, install VS component Visual c++ compiler and libraries for ' + targetCPU)
      return errors.ERROR_BUILD_MISSING_LIB_EXECUTABLE

    #Get list of strings, with file paths total length less than 7000,,
    listOfObjesToCombine = Utility.getFilesWithExtensionsInFolder(config.COMBINE_LIB_FOLDERS, ('.obj','.o'), config.COMBINE_LIB_IGNORE_SUBFOLDERS)

    #Create temporary folder where will be save libs created from the obj files ^^^
    tempCombinePath = 'combine'
    if not Utility.createFolders([tempCombinePath]):
      return errors.ERROR_BUILD_MERGE_LIBS_FAILED

    counter = 0
    libsToMerge = ''

    #Create webrtc libs from specified obj files and name it like webrtc0..n.lib
    for objs in listOfObjesToCombine:
      output = 'webrtc' + str(counter) + '.lib'
      cls.logger.debug('Creating ' + output + ' library')
      ret = cls.combineLibs(targetCPU, objs, tempCombinePath, output)
      if ret == NO_ERROR:
        #Generated lib add to the list, which will be used for creation one fat webrtc lib
        libsToMerge += (os.path.join(tempCombinePath, output)) + ' '
        counter += 1
      else:
        break

     #Create webrtc lib from specified lib files
    if ret == NO_ERROR and len(libsToMerge) > 0:
      cls.logger.debug('Creating webrtc library')
      ret = cls.combineLibs(targetCPU, libsToMerge, destinationPath, 'webrtc.lib')
    else:
      cls.logger.warning('There is no libs to merge for target CPU ' + targetCPU)

    Utility.deleteFolders([tempCombinePath])

    cls.logger.info('Merging libs is finished')
    return ret

  @classmethod
  def combineLibs(cls, targetCPU, inputFiles, outputFolder, outputFile):
    ret = NO_ERROR
    try:
      if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
      output = os.path.join(outputFolder, outputFile)

      #Call lib.exe to mergeobj files to webrtc[counter].lib files, which will be later merged to webrtc.lib
      cmdLibExe = '\"' +  cls.libexePath + '\" /IGNORE:' + ','.join(str(i) for i in config.WINDOWS_IGNORE_WARNINGS) +  ' /OUT:' + output + ' ' + inputFiles

      result = Utility.runSubprocess([cls.cmdVcVarsAll, cmdLibExe, cls.cmdVcVarsAllClean], Settings.logLevel == 'DEBUG')

      if result != 0:
        cls.logger.error(error_codes[errors.ERROR_BUILD_MERGE_LIBS_FAILED])
        ret = errors.ERROR_BUILD_MERGE_LIBS_FAILED

    except Exception as error:
      cls.logger.error(str(error))
      cls.logger.info('Failed combining libraries')
      ret = errors.ERROR_BUILD_MERGE_LIBS_FAILED

    return ret

  @classmethod
  def copyFilesToOutput(cls, destinationPathLib, extension, listOfIngoredSubFolders, destinationSubfolder=''):
    """
      Copy files with specifed extension to the output folder.
      :param destinationPathLib: Path to folder where files will be copied.
      :param extension: Files extension.
      :param listOfIngoredSubFolders: List of folders whose content will be ignored.
      :param destinationSubfolder: Subfolder in destinationPathLib where files will be copied
      :return ret: NO_ERROR if files are copied, othervise ERROR_BUILD_COPYING_TO_OUTPUT_FAILED
    """
    result = True

    destinationFilesPath = os.path.join(destinationPathLib,destinationSubfolder)

    try:
      if not os.path.exists(destinationPathLib):
        os.makedirs(destinationPathLib)

      if not os.path.exists(destinationFilesPath):
        os.makedirs(destinationFilesPath)

      listOfFilessToCopy = Utility.getFilesWithExtensionsInFolder(['.'],('.'+extension),listOfIngoredSubFolders,0)
      
      for fileToCopy in listOfFilessToCopy:
        result = Utility.copyFile(fileToCopy, os.path.join(destinationFilesPath,os.path.basename(fileToCopy)))
    
    except Exception as error:
      cls.logger.warning(str(error))
      cls.logger.warning('Failed copying files with extension .' + extension + ' to output folder ' + destinationFilesPath + '!')
      result = False

    if not result:
      return  errors.ERROR_BUILD_COPYING_TO_OUTPUT_FAILED
    return NO_ERROR

  @classmethod
  def getTargetGnPath(cls, target):
    #Check if target is defined in userdef.py availableTargetsForBuilding. If not, returns target name as 
    # gn path and 0 for combininglibs flag. In that case check is performed also in config.py TARGETS_TO_BUILD
    targetsToBuild, shouldCombineLibs, shouldCopyToOutput = Settings.availableTargetsForBuilding.get(target,([target],0,1))
    if target in targetsToBuild and shouldCombineLibs == 0:
      targetsToBuild, shouldCombineLibs, shouldCopyToOutput = config.TARGETS_TO_BUILD.get(target,([target],0,1))
    
    return targetsToBuild, shouldCombineLibs, shouldCopyToOutput
    