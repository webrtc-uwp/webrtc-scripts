import os
import subprocess

from errors import *
import config
from settings import Settings
from logger import Logger
from utility import Utility
from helper import convertToPlatformPath

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

    if not cls.buildTarget(targets, combineLibs):
      return ERROR_BUILD_FAILED
    
    Utility.popd()

    return NO_ERROR

  @classmethod
  def buildTarget(cls, targets, combineLibs):
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
        cls.combineLibs()

    return True

  @classmethod
  def combineLibs(cls):
    objsToCombine = ''
    for subFolder in config.COMBINE_LIB_FOLDERS:
      for root, dirs, files in os.walk(convertToPlatformPath(subFolder)):
        for file in files:
          if file.endswith(('.obj','.o')):
            objsToCombine += os.path.join(root, file) + ' '



  @classmethod
  def getTargetGnPath(cls, target):
    targetsToBuild, combineLibs = config.TARGETS_TO_BUILD.get(target,(target,0))
    return targetsToBuild, combineLibs