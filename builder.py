import os
import subprocess
import shutil 

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
    cls.logger = Logger.getLogger('Build')

  @classmethod
  def run(cls, targetName, targets, platform, cpu, configuration, combineLibs = False, outputPath = None):
    cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    if outputPath == None:
      outputPath = os.path.join('out', targetName + '_' + platform + '_' + cpu + '_' + configuration)

    workingDir = os.path.join(Settings.preparationWorkingPath,outputPath)

    if not os.path.exists(workingDir):
      cls.logger.error('Output folder at ' + workingDir + ' doesn\'t exist. It looks like prepare is not executed. Please run prepare action.')
      return ERROR_BUILD_OUTPUT_FOLDER_DEOESNT_EXIST
    
    Utility.pushd(workingDir)

    if not cls.buildTarget(targets, cpu, combineLibs):
      return ERROR_BUILD_FAILED
    
    Utility.popd()

    return NO_ERROR

  @classmethod
  def buildTarget(cls, targets, targetCPU, combineLibs):
    for target in targets:
      result = subprocess.call([
          Settings.localNinjaPath + '.exe',
          target,
        ])

      if result != 0:
          cls.logger.error('Building ' + target + ' target libraries has failed!')
          return False
      
      cls.logger.info('Successfully finished building libs for target ' + target)

    if combineLibs:
      cls.mergeLibs(targetCPU)

    return True

  @classmethod
  def mergeLibs(cls, targetCPU):
    cls.libexePath = os.path.join(Settings.msvcToolsBinPath, targetCPU, 'lib.exe')
    
    listOfObjesToCombine = Utility.getFilesWithextensionsInFolder(config.COMBINE_LIB_FOLDERS, ('.obj','.o'))

    tempCombinePath = 'combine'
    Utility.createFolders([tempCombinePath])

    counter = 0
    libsToMerge = ''

    for objs in listOfObjesToCombine:
      output = 'webrtc' + str(counter) + '.lib'
      ret = cls.combineLibs(targetCPU, objs, tempCombinePath, output)
      if ret == NO_ERROR:
        libsToMerge += (os.path.join(tempCombinePath, output)) + ' '
        counter += 1
      else:
        System.stopExecution(ret)

    if len(libsToMerge) > 0:
      ret = cls.combineLibs(targetCPU, libsToMerge, '.', 'webrtc.lib')
      if ret != NO_ERROR:
        System.stopExecution(ret)
    else:
      cls.logger.warning('There is no libs to merge for target CPU ' + targetCPU)

    shutil.rmtree(tempCombinePath) 

  @classmethod
  def combineLibs(cls, targetCPU, inputFiles, outputFolder, outputFile):
    ret = NO_ERROR
    try:
      #Set the PATH and environment variables for command-line builds (e.g. vcvarsall.bat x64_x86)
      cmdVcVarsAll = '\"' +  Settings.vcvarsallPath + '\" ' + config.WINDOWS_COMPILER_OPTIONS[System.hostCPU][targetCPU]

      output = os.path.join(outputFolder, outputFile)

      #Call lib.exe to mergeobj files to webrtc[counter].lib files, which will be later merged to webrtc.lib
      cmdLibExe = '\"' +  cls.libexePath + '\" /IGNORE:' + ','.join(str(i) for i in config.WINDOWS_IGNORE_WARNINGS) +  ' /OUT:' + output + ' ' + inputFiles

      #Make cmdLibExe command dependent on cmdVcVarsAll
      commands = cmdVcVarsAll + ' && ' + cmdLibExe

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
  def getTargetGnPath(cls, target):
    targetsToBuild, combineLibs = config.TARGETS_TO_BUILD.get(target,(target,0))
    return targetsToBuild, combineLibs