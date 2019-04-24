import os
from datetime import datetime

import config
from settings import Settings
from utility import Utility
from helper import convertToPlatformPath
import errors
from errors import NO_ERROR
from logger import Logger
class Backup:

  @classmethod
  def init(cls):
    cls.logger = Logger.getLogger('backup')
    ret = NO_ERROR

    backupFolder = Settings.libsBackupPath
    if backupFolder == '':
      backupFolder = 'Backup'
          
    cls.backupPath = os.path.join(Settings.userWorkingPath,convertToPlatformPath(backupFolder))
    #If backup folder exists delete it, or add time suffix to folder name
    if os.path.exists(cls.backupPath):
      if Settings.overwriteBackup:
        if not Utility.deleteFolders([cls.backupPath]):
          ret = errors.ERROR_BUILD_BACKUP_DELETION_FAILED
      else:
        timeSuffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        cls.backupPath = os.path.join(Settings.userWorkingPath,convertToPlatformPath(backupFolder) + '_' + timeSuffix)

    return ret

  @classmethod
  def run(cls, target, platform, cpu, configuration):
    """
      Backups native and wrapper libs and pdbs.
      :param target: Target name (ortc or webrtc)
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration to build for
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    ret = NO_ERROR
    #Backup folder name
    targetFolder = target + '_' + platform + '_' + cpu + '_' + configuration 

    nativeOutputPath = convertToPlatformPath(config.BUILT_LIBS_DESTINATION_PATH.replace('[BUILD_OUTPUT]',config.BUILD_OUTPUT_PATH).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration))
    nativeOutputPathLib = os.path.join(Settings.webrtcPath, nativeOutputPath)

    if ret == NO_ERROR:
      nativeDestinationPath = os.path.join(cls.backupPath,targetFolder,'native')
      if not Utility.copyFolder(nativeOutputPathLib, nativeDestinationPath):
        ret = errors.ERROR_BUILD_BACKUP_FAILED
      if ret == NO_ERROR:
        cls.logger.debug("Native output copied: " + nativeOutputPathLib)
      else:
        cls.logger.error("Failed to copy native output: " + nativeOutputPathLib)

    if ret == NO_ERROR:  
      if Settings.buildWrapper:
        #Determine wrapper projects output path
        wrapperRelativeOutputPath = convertToPlatformPath(Utility.getValueForTargetAndPlatformDict(config.TARGET_WRAPPER_PROJECTS_OUTPUT_PATHS, target, platform))
        if wrapperRelativeOutputPath != '':
          wrapperRootOutputPath = os.path.join(Settings.rootSdkPath,wrapperRelativeOutputPath)
          #wrapperRootOutputPath = os.path.join(Settings.rootSdkPath,convertToPlatformPath(config.WEBRTC_WRAPPER_PROJECTS_OUTPUT_PATH))
          wrapperOutputPath =  os.path.join(wrapperRootOutputPath, configuration, cpu)
          wrapperDestinationPath = os.path.join(cls.backupPath,targetFolder,'wrapper')
          if not Utility.copyFolder(wrapperOutputPath, wrapperDestinationPath):
            ret = errors.ERROR_BUILD_BACKUP_FAILED
          if ret == NO_ERROR:
            cls.logger.debug("Wrapper projects copied: " + wrapperOutputPath)
          else:
            cls.logger.error("Failed to copy wrapper projects: " + wrapperOutputPath)
        else:
          cls.logger.warning('Wrapper output folder doesn\'t exist!')

    if ret != NO_ERROR:
      cls.logger.error('Backup failed!')

    return ret
    