import os
import sys
import re
import logging
import subprocess
import signal
from shutil import copyfile, rmtree

from logger import Logger
from helper import convertToPlatformPath
from errors import NO_ERROR, ERROR_SUBPROCESS_EXECUTAION_FAILED
class Utility:

  @classmethod
  def setUp(cls):
    cls.logger = Logger.getLogger('Utility')

  @staticmethod 
  def checkIfToolIsInstalled(toolName):
    executablePath = Utility.getExecutablePath(toolName)
    if executablePath != None:
      return True

    return False

  @staticmethod
  def getExecutablePath(executable):
    executablePath = None
    if sys.version_info[0] < 3.3:
      import distutils.spawn
      executablePath = distutils.spawn.find_executable(executable)
    else:
      import shutil 
      executablePath = shutil.which(executable)
    
    return executablePath

  @staticmethod
  def searchFileInPATH(fileName):
    for dirname in os.environ['PATH'].split(os.pathsep):
        filePath = os.path.join(dirname, fileName)
        if os.path.isfile(filePath):
            return dirname
    return None

  @staticmethod
  def addModulePath(path):
    sys.path.append(path)

  @staticmethod
  def addPath(path):
    newPath = os.environ['PATH']
    if newPath.endswith(';'):
      newPath = newPath[:-1]
    newPath += ';' + path
    os.environ['PATH'] = newPath

  @staticmethod
  def removePath(path):
    newPath = os.environ['PATH'].replace(path + os.pathsep,'').replace(path,'')
    os.environ['PATH'] = newPath

  @classmethod
  def makeLink(cls,source,destination):
    if not os.path.exists(destination):
      cls.logger.debug('Creating link ' + convertToPlatformPath(destination) + ' to point to ' + convertToPlatformPath(source))
      subprocess.call(['cmd', '/c', 'mklink', '/J', convertToPlatformPath(destination), convertToPlatformPath(source)])

  @staticmethod
  def deleteLink(linkToDelete):
    """
    TODO: Verify this is working correctly
    """
    if os.path.exists(linkToDelete):
      subprocess.call(['cmd', '/c', 'rmdir', convertToPlatformPath(linkToDelete)])

  @staticmethod
  def createFolders(foldersList):
    for path in foldersList:
      dirPath = convertToPlatformPath(path)
      if not os.path.exists(dirPath):
        os.makedirs(dirPath)

  @staticmethod
  def removeFolders(foldersList):
    for path in foldersList:
      dirPath = convertToPlatformPath(path)
      if os.path.exists(dirPath):
        rmtree(dirPath)

  @staticmethod
  def createFolderLinks(foldersToLink):
    for dict in foldersToLink:
      for source, destination in dict.items():
        Utility.makeLink(convertToPlatformPath(source), convertToPlatformPath(destination))

  @staticmethod
  def deleteFolderLinks(foldersToLink):
    for dict in foldersToLink:
      for source, destination in dict.items():
        Utility.deleteLink(convertToPlatformPath(destination))

  @staticmethod
  def copyFilesFromDict(filesToCopy):
    for dict in filesToCopy:
      for source, destination in dict.items():
        copyfile(convertToPlatformPath(source), convertToPlatformPath(destination))

  @staticmethod
  def changeWorkingDir(path):
    if os.path.isdir(path):
      os.chdir(path)
    else:
      return False
    return True 

  pushstack = list()

  @classmethod
  def pushd(cls, path):
    try:
      cls.logger.debug('pushd ' + path)
      cls.pushstack.append(os.getcwd())
      os.chdir(path)
    except Exception, errorMessage:
      cls.logger.error(errorMessage)

  @classmethod
  def popd(cls):
    try:
      cls.logger.debug('popd ' + cls.pushstack[-1])
      os.chdir(cls.pushstack.pop())
    except Exception, errorMessage:
      cls.logger.warning(errorMessage)

  @classmethod
  def getFilesWithExtensionsInFolder(cls, folders, extensions, folderToIgnore = (), stringLimit = 7000):
    listOfFiles = ''
    listOfPaths = []
    for folder in folders:
      if os.path.exists(convertToPlatformPath(folder)):
        for root, dirs, files in os.walk(convertToPlatformPath(folder)):
          if not root.endswith(folderToIgnore):
            for file in files:
              if file.endswith(extensions):
                listOfFiles += os.path.join(root, file) + ' '
                if len(listOfFiles) > stringLimit:
                  listOfPaths.append(listOfFiles[:-1])
                  listOfFiles = ''
      else:
        cls.logger.warning('Folder ' + folder + ' doesn\'t exist!')
    if len(listOfFiles) > 0:
      listOfPaths.append(listOfFiles)
    return listOfPaths

  @classmethod
  def importDependencyForTarget(cls, gnFile, target, dependency):
    if os.path.exists(gnFile):
      targetMark = '(\"' + target + '\")'
      depsRegex = r'\s*deps\s*=\s*\[*'
      depsFlag = False
      insertFlag = False
      with open(gnFile, 'r') as gnReadFile:
        gnContent = gnReadFile.readlines()
      with open(gnFile,'w') as gnWriteFile:
        for line in gnContent:
          gnWriteFile.write(line)
          if targetMark in line:
            depsFlag = True
          else:
            if depsFlag:
              if re.findall(depsRegex,line) != []:
                insertFlag = True
                depsFlag = False
            elif insertFlag:
              gnWriteFile.write('"' + dependency + '",')
              insertFlag = False

  @classmethod
  def backUpAndUpdateGnFile(cls, filePath, targetToUpdate, dependencyToAdd):
    if os.path.isfile(filePath):
      copyfile(filePath, filePath + '.bak')
      for dependecy in dependencyToAdd:
        cls.importDependencyForTarget(filePath, targetToUpdate, dependecy)

  @classmethod
  def returnOriginalFile(cls, filePath):
    backupFilePath = filePath + '.bak'
    if os.path.isfile(backupFilePath):
      copyfile(backupFilePath, filePath)
      os.remove(backupFilePath) 

  @classmethod
  def runSubprocess(cls, commands, shouldLog = False):
    """
      Run provided command line as subprocess.
    """
    result = NO_ERROR
    commandToExecute = ''
    for command in commands:
      if len(commandToExecute) > 0:
        commandToExecute = commandToExecute + ' && '
      if not shouldLog:
        commandToExecute = commandToExecute + command + '>NUL'
      else:
        commandToExecute = commandToExecute + command
    try:
      #Execute command
      process = subprocess.Popen(commandToExecute, shell=False, stderr=subprocess.PIPE)

      #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
      process.communicate()

      result = process.returncode

    except KeyboardInterrupt:
      os.kill(process.pid, signal.SIGTERM)
    except Exception as error:
      result = ERROR_SUBPROCESS_EXECUTAION_FAILED
      cls.logger.error(str(error))

    return result