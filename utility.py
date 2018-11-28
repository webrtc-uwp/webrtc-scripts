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
import config
class Utility:

  @classmethod
  def setUp(cls):
    cls.logger = Logger.getLogger('Utility')

  @staticmethod 
  def checkIfToolIsInstalled(toolName):
    """
      Check if specific tool executable is in the path.
      :param toolName: Name of the tool executable.
      :return ret: True if tool is in the path. Otehrwise False.
    """
    ret = False
    executablePath = Utility.getExecutablePath(toolName)
    if executablePath != None:
      ret = True

    return ret

  @staticmethod
  def getExecutablePath(executable):
    """
      Finds executable path.
      :param executable: Name of the executable.
      :return executablePath: Executable path.
    """
    executablePath = None
    if sys.version_info[0] < 3.3:
      import distutils.spawn
      executablePath = distutils.spawn.find_executable(executable)
    else:
      #Used for Python 3.3 or newer
      import shutil 
      executablePath = shutil.which(executable)
    
    return executablePath

  @staticmethod
  def searchFileInPATH(fileName):
    """
      Search if file is present in one of the folders in the PATH.
      :param fileName: File to search for.
      :return dirname: Return folder name if file is found.
    """
    for dirname in os.environ['PATH'].split(os.pathsep):
        filePath = os.path.join(dirname, fileName)
        if os.path.isfile(filePath):
            return dirname
    return None

  @staticmethod
  def addModulePath(path):
    """
      Adds path to modules path.
      :param path: Path to add.
    """
    sys.path.append(path)

  @staticmethod
  def addPath(path):
    """
      Adds path to system PATH.
      :param path: PAth to add.
    """
    newPath = os.environ['PATH']
    if newPath.endswith(';'):
      newPath = newPath[:-1]
    newPath += ';' + path
    os.environ['PATH'] = newPath

  @staticmethod
  def removePath(path):
    """
      Removes path from the sytem PATH.
      :param path: Path to remove.
    """
    newPath = os.environ['PATH'].replace(path + os.pathsep,'').replace(path,'')
    os.environ['PATH'] = newPath

  @classmethod
  def makeLink(cls, source, destination):
    """
      Creates junction link.
      :param source: Source folder.
      :param destination: Junction link to make.
    """
    if not os.path.exists(destination):
      cls.logger.debug('Creating link ' + convertToPlatformPath(destination) + ' to point to ' + convertToPlatformPath(source))
      cmd = 'cmd ' + '/c ' + 'mklink ' + '/J ' + convertToPlatformPath(destination) + ' ' + convertToPlatformPath(source)
      result = Utility.runSubprocess([cmd], True)
      if result == NO_ERROR:
        cls.logger.debug('Successfully created link ' + destination)
      else:
        cls.logger.error('Failed creating link ' + destination)

  @classmethod
  def deleteLink(cls,linkToDelete):
    """
    TODO: Verify this is working correctly
    """
    if os.path.exists(linkToDelete):
      #subprocess.call(['cmd', '/c', 'rmdir', convertToPlatformPath(linkToDelete)])
      cmd = 'cmd ' + '/c ' + 'rmdir ' + convertToPlatformPath(linkToDelete)
      result = Utility.runSubprocess([cmd], True)
      if result != NO_ERROR:
        cls.logger.error('Failed removing link ' + linkToDelete)

  @staticmethod
  def createFolders(foldersList):
    """
      Creates folders specified in the list.
      :param foldersList: List of folders to create
    """
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
        if os.path.exists(source):
          Utility.makeLink(convertToPlatformPath(source), convertToPlatformPath(destination))

  @staticmethod
  def deleteFolderLinks(foldersToLink):
    for dict in foldersToLink:
      for source, destination in dict.items():
        if os.path.exists(destination):
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
    except Exception as error:
      cls.logger.error(error)

  @classmethod
  def popd(cls):
    try:
      cls.logger.debug('popd ' + cls.pushstack[-1])
      os.chdir(cls.pushstack.pop())
    except Exception as error:
      cls.logger.warning(error)

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
  def getSolutionForTargetAndPlatform(cls, target, platform):
    ret = None
    targetDict = config.TARGET_WRAPPER_SOLUTIONS.get(target,None)
    if targetDict != None:
      ret = targetDict.get(platform,'')
      if ret == '':
        cls.logger.info('There is no Wrapper solution file for ' + target + ' ' + platform)
      else:
        cls.logger.info('Wrapper solution file is ' + str(ret))
    return ret

  @classmethod
  def runSubprocess(cls, commands, shouldLog = False, userEnv = None):
    """
      Runs provided command line as subprocess.
      :param commands: List of commands to execute.
      :param shouldLog: Flag if subprocess stdout should be logged or not
      :param userEnv: Customized environment
      :return result: NO_ERROR if subprocess is executed successfully. Otherwise error or subprocess returncode
    """
    result = NO_ERROR
    commandToExecute = ''
    for command in commands:
      if len(commandToExecute) > 0:
        commandToExecute = commandToExecute + ' && '
      if not shouldLog:
        commandToExecute = commandToExecute + command + ' >NUL'
      else:
        commandToExecute = commandToExecute + command
    try:
      #Execute command
      cls.logger.debug('Running subprocess: \n' + commandToExecute)
      if userEnv == None:
        process = subprocess.Popen(commandToExecute, shell=False, stderr=subprocess.PIPE)
      else: 
        process = subprocess.Popen(commandToExecute, shell=False, stderr=subprocess.PIPE, env=userEnv)

      #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
      process.communicate()

      result = process.returncode

    except KeyboardInterrupt:
      os.kill(process.pid, signal.SIGTERM)
    except Exception as error:
      result = ERROR_SUBPROCESS_EXECUTAION_FAILED
      cls.logger.error(str(error))

    return result