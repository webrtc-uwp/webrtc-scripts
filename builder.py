import os
import subprocess
import shutil 
import signal

from errors import *
import config
from settings import Settings
from logger import Logger
from utility import Utility
from helper import convertToPlatformPath
from system import System

class Builder:
  @classmethod
  def init(cls):
    """
      Initiates logger object.
    """
    cls.logger = Logger.getLogger('Build')

  @classmethod
  def run(cls, targetName, targets, platform, cpu, configuration, shouldCombineLibs = False, builderWorkingPath = None):
    """
      Start target building process.
      :param targetName: Name of the main target (ortc or webrtc)
      :param targets: List of the targets to build
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration to build for
      :param shouldCombineLibs: Should all libs be merged into one library
      :param builderWorkingPath: Path where generated projects for specified target.
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #If path with generated projects is not specified generate path from input arguments
    if builderWorkingPath == None:
      builderWorkingPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH, targetName, platform, cpu, configuration)#os.path.join('out', targetName + '_' + platform + '_' + cpu + '_' + configuration)

    workingDir = os.path.join(Settings.webrtcPath,builderWorkingPath)

    #If folder for specified target and platform doesn't exist, stop further execution
    if not os.path.exists(workingDir):
      cls.logger.error('Output folder at ' + workingDir + ' doesn\'t exist. It looks like prepare is not executed. Please run prepare action.')
      return ERROR_BUILD_OUTPUT_FOLDER_DEOESNT_EXIST
    
    #Set the PATH and environment variables for command-line builds (e.g. vcvarsall.bat x64_x86)
    cls.cmdVcVarsAll = '\"' +  Settings.vcvarsallPath + '\" ' + config.WINDOWS_COMPILER_OPTIONS[System.hostCPU][cpu]
    cls.cmdVcVarsAllClean = '\"' +  Settings.vcvarsallPath + '\" ' + '/clean_env'

    
    #Change current working directory to one with generated projects
    Utility.pushd(workingDir)

    #Start building and merging libraries
    if not cls.buildTargets(targets, cpu):
      return ERROR_BUILD_FAILED
    
    destinationPath = convertToPlatformPath(config.BUILT_LIBS_DESTINATION_PATH.replace('[BUILD_OUTPUT]',config.BUILD_OUTPUT_PATH).replace('[TARGET]',targetName).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration))
    destinationPathLib = os.path.join(Settings.webrtcPath, destinationPath)

    #Merge libraries if it is required
    if shouldCombineLibs:
      cls.mergeLibs(cpu,destinationPathLib)

    cls.copyLibsToOutput(targetName, platform, cpu, configuration, destinationPathLib)

    if Settings.enableBackup and Settings.libsBackupPath != '':
      backupPath = os.path.join(Settings.userWorkingPath,Settings.libsBackupPath)
      if os.path.exists(backupPath):
        shutil.rmtree(backupPath) 
      shutil.copytree(destinationPathLib,backupPath)
    #Switch to previously working directory
    Utility.popd()
  
    if Settings.buildWrapper:
      if not cls.buildWrapper(targetName,cpu,configuration):
        return ERROR_BUILD_FAILED
      

    cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration + ', finished successfully!')
    return NO_ERROR

  @classmethod
  def buildWrapper(cls, target, targetCPU, configuration):
    """
      Builds wrapper projects.
    """
    ret = True
    cls.logger.info('Building ' + target + ' wrapper projects for ' + targetCPU + ' for configuration  '+ configuration)

    try:
      #Solution template path
      solutionSourcePath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_TEMPLATES_PATH),config.NUGET_WINUWP_WEBRTC_SOLUTION)
      #Path where solution template will be copied
      solutionDestinationPath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_SOLUTION_PATH),config.NUGET_WINUWP_WEBRTC_SOLUTION)
      
      #Copy template solution to solution folder
      shutil.copyfile(solutionSourcePath,solutionDestinationPath)

      #MSBuild command for building wrapper projects
      cmdBuild = 'msbuild ' + solutionDestinationPath + ' /t:Build' + ' /p:Configuration=\"' + configuration + '\" /p:Platform=\"' + targetCPU + '\"'

      #EXecute MSBuild command
      result = Utility.runSubprocess([cls.cmdVcVarsAll, cmdBuild, cls.cmdVcVarsAllClean], Settings.logLevel == 'DEBUG')
      if result != 0:
        cls.logger.error('Building ' + target + ' target has failed!')
        ret = False
    except Exception as error:
      ret = False
    finally:
      #Delete solution used for building wrapper projects.
      os.remove(solutionDestinationPath) 
    if ret:
      cls.logger.info('Successfully finished building wrappers for target ' + target)

    return ret

  @classmethod
  def buildTargets(cls, targets, targetCPU):
    """
      Build list of targets for specified cpu.
    """
    ret = True
    cls.logger.info('Following targets ' + str(targets) + ' will be built for cpu '+ targetCPU)

    mainBuildGnFilePath = os.path.join(Settings.webrtcPath,'BUILD.gn')

    try:
      for target in targets:
        cls.logger.debug('Building target ' + target)
        my_env = os.environ.copy()
        my_env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"    
        
        #Backup original BUILD.gn from webrtc root folder and add additional dependecies to webrtc target
        if target == config.WEBRTC_TARGET:
          Utility.backUpAndUpdateGnFile(mainBuildGnFilePath,config.WEBRTC_TARGET,config.ADDITIONAL_TARGETS_TO_ADD)

        #Run ninja to build targets
        result = subprocess.call([
            Settings.localNinjaPath + '.exe',
            target,
          ],env=my_env)

        if result != 0:
          cls.logger.error('Building ' + target + ' target has failed!')
          ret = False

    except Exception as error:
      cls.logger.error(str(error))
      cls.logger.error('Build failed for following targets ' + str(targets) + ' for cpu '+ targetCPU)
      ret = False
    finally:
      Utility.returnOriginalFile(mainBuildGnFilePath)

    if ret:
      cls.logger.info('Successfully finished building libs for target ' + target)

    return ret

  @classmethod
  def mergeLibs(cls, targetCPU, destinationPath):
    """
      Merges obj files and creates fat webrtc library.
      TODO: Make it returns error, instead of to terminate execution on error
    """
    cls.logger.info('Merging libs for cpu '+ targetCPU)

    #Determine lib.exe path
    cls.libexePath = os.path.join(Settings.msvcToolsBinPath, targetCPU, 'lib.exe')
    
    #Get list of strings, with file paths total length less than 7000,,
    listOfObjesToCombine = Utility.getFilesWithExtensionsInFolder(config.COMBINE_LIB_FOLDERS, ('.obj','.o'), config.COMBINE_LIB_IGNORE_SUBFOLDERS)

    #Create temporary folder where will be save libs created from the obj files ^^^
    tempCombinePath = 'combine'
    Utility.createFolders([tempCombinePath])

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
        cls.logger.error('Creating ' + output + ' library has failed!')
        System.stopExecution(ret)

     #Create webrtc lib from specified lib files
    if len(libsToMerge) > 0:
      ret = cls.combineLibs(targetCPU, libsToMerge, destinationPath, 'webrtc.lib')
      if ret != NO_ERROR:
        cls.logger.error('Creating webrtc library has failed!')
        System.stopExecution(ret)
    else:
      cls.logger.warning('There is no libs to merge for target CPU ' + targetCPU)

    shutil.rmtree(tempCombinePath) 

    cls.logger.info('Merging libs is finished')

  @classmethod
  def combineLibs(cls, targetCPU, inputFiles, outputFolder, outputFile):
    ret = NO_ERROR
    try:
      if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
      output = os.path.join(outputFolder, outputFile)

      #Call lib.exe to mergeobj files to webrtc[counter].lib files, which will be later merged to webrtc.lib
      cmdLibExe = '\"' +  cls.libexePath + '\" /IGNORE:' + ','.join(str(i) for i in config.WINDOWS_IGNORE_WARNINGS) +  ' /OUT:' + output + ' ' + inputFiles

      #Make cmdLibExe command dependent on cmdVcVarsAll
      commands = cls.cmdVcVarsAll + ' && ' + cmdLibExe + ' && ' + cls.cmdVcVarsAllClean

      #cls.logger.debug('Command line to execute: ' + commands)
      FNULL = open(os.devnull, 'w')
      result = subprocess.call(commands,stdout=FNULL, stderr=subprocess.STDOUT)

      if result != 0:
        cls.logger.error(error_codes[ERROR_BUILD_MERGE_LIBS_FAILED])
        ret = ERROR_BUILD_MERGE_LIBS_FAILED

    except Exception as error:
      cls.logger.error(str(error))
      ret = ERROR_BUILD_MERGE_LIBS_FAILED

    return ret

  @classmethod
  def copyLibsToOutput(cls, target, platform, cpu, configuration, destinationPathLib):
    destinationPathPdb = os.path.join(destinationPathLib,'pdbs')

    if not os.path.exists(destinationPathLib):
      os.makedirs(destinationPathLib)

    if not os.path.exists(destinationPathPdb):
      os.makedirs(destinationPathPdb)

    listOfLibsToCopy = Utility.getFilesWithExtensionsInFolder(['.'],('.dll'),config.COMBINE_LIB_IGNORE_SUBFOLDERS,0)
    
    for lib in listOfLibsToCopy:
      shutil.copyfile(lib, os.path.join(destinationPathLib,os.path.basename(lib)))

    listOfPdbsToCopy = Utility.getFilesWithExtensionsInFolder(['.'],('.pdb'),config.COMBINE_LIB_IGNORE_SUBFOLDERS,0)
    
    for pdb in listOfPdbsToCopy:
      shutil.copyfile(pdb, os.path.join(destinationPathPdb,os.path.basename(pdb)))

  @classmethod
  def makeBackup(cls):
    pass

  @classmethod
  def getTargetGnPath(cls, target):
    targetsToBuild, shouldCombineLibs = config.TARGETS_TO_BUILD.get(target,(target,0))
    return targetsToBuild, shouldCombineLibs