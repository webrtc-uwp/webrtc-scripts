import os
import sys
import re
import logging
import subprocess
import signal
import shutil
try:
  from _winreg import HKEY_LOCAL_MACHINE, OpenKey, QueryValueEx, CloseKey
except:
  pass

from logger import Logger
from helper import convertToPlatformPath
from errors import error_codes, NO_ERROR, ERROR_SUBPROCESS_EXECUTAION_FAILED, TERMINATED_BY_USER
import config
class Utility:

  #Used in pushd and popd
  pushstack = list()
  actviveSubprocessList  = list()

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
      :param path: Path to add.
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

  @staticmethod
  def getBranch():
    """
      Returns the branch name for the root SDK git repository
      :return branch: branch name
    """
    branch = Utility.executeCommand('git rev-parse --abbrev-ref HEAD')
    return branch
    
  @staticmethod
  def getRepo():
    """
      Returns the repo url for the root SDK git repository
      :return repo: repo url
    """
    repo = Utility.executeCommand('git remote get-url origin')
    if repo.endswith('.git'):
        repo = repo[:-len('.git')]
    return repo
    
  @staticmethod
  def getCommitHash():
    """
      Returns the last commit hash for the root SDK git repository
      :return commitHash: commit hash
    """
    commitHash = Utility.executeCommand('git rev-parse HEAD')
    return commitHash
    
  @staticmethod
  def getCommitTitle(commitHash):
    """
      Returns title for the given commit hash
      :param commitHash: hash value for the commit
      :return commitTitle: commit title
    """
    commitTitle = Utility.executeCommand('git log --format=%B -n 1 ' + commitHash)
    commitTitle = commitTitle.strip()
    return commitTitle

  @classmethod
  def addGitTag(cls, tagNumber):
    """
      Adds a tag to the git repository with a specific version number.
      :param tagNumber: Tag number
    """
    ret = Utility.executeCommand('git tag ' + tagNumber)
    if 'error' not in ret:
      cls.logger.debug("Git tag added: " + tagNumber)

  @classmethod
  def pushGitTag(cls, tagNumber):
    """
      Publishes a tag with a specific tag number to the git repository.
      :param tagNumber: Tag number
    """
    ret = Utility.executeCommand('git push origin ' + tagNumber)
    if 'error' not in ret:
      cls.logger.debug("Tag pushed to git repository: " + tagNumber)
  
  @classmethod
  def getCommitLog(cls, currentTag, commitKeywords):
    """
      Returns all the commits that contain at least one of the keywords in between current tag and a tag before that one 
      :param currentTag: Current tag
      :param commitKeywords: Array of keywords
      :return commits: Distionary with pairs of commit hashes and commit texts
    """
    commits = {}
    #Get previous tag
    previousTag = Utility.executeCommand('git describe --abbrev=0 ' + currentTag + '^')
    cls.logger.debug("Getting commits between " + previousTag + " and " + currentTag + " tags")
    #Get all commits between two tags
    log = Utility.executeCommand('git log ' + previousTag + '..' + currentTag + ' --pretty=oneline')
    log = log.splitlines()
    # check if any of the keywords are contained in commit
    if '*' not in commitKeywords[0]:
      for commit in log:
        if any(keyword in commit for keyword in commitKeywords):
          commit = commit.split(' ', 1)
          commits[commit[0]] = commit[1]
    else:
      for commit in log:
        commit = commit.split(' ', 1)
        commits[commit[0]] = commit[1]

    return commits

  @classmethod
  def makeLink(cls, source, destination):
    """
      Creates junction link.
      :param source: Source folder.
      :param destination: Junction link to make.
      :return ret: True if link is created.
    """
    ret = True
    if not os.path.exists(destination):
      cls.logger.debug('Creating link ' + convertToPlatformPath(destination) + ' to point to ' + convertToPlatformPath(source))
      cmd = 'cmd ' + '/c ' + 'mklink ' + '/J ' + convertToPlatformPath(destination) + ' ' + convertToPlatformPath(source)
      result = Utility.runSubprocess([cmd], True)
      if result == NO_ERROR:
        cls.logger.debug('Successfully created link ' + destination)
      else:
        ret = False
        cls.logger.error('Failed creating link ' + destination)

    return ret

  @classmethod
  def deleteLink(cls,linkToDelete):
    """
      Deletes junction link.
      :param linkToDelete: Path to link.
      :return ret: True if link is deleted.
    """
    ret = True
   
    if os.path.exists(linkToDelete):
      cmd = 'cmd ' + '/c ' + 'rmdir ' + convertToPlatformPath(linkToDelete)
      result = Utility.runSubprocess([cmd], True)
      if result != NO_ERROR:
        ret = False
        cls.logger.error('Failed removing link ' + linkToDelete)
    else:
      cls.logger.warning(linkToDelete + ' link doesn\'t exist.')

    return ret

  @classmethod
  def createFolders(cls, foldersList):
    """
      Creates folders specified in the list.
      :param foldersList: List of folders to create
      :return ret: True if folder exists or if it is created.
    """
    ret = True
    try:
      for path in foldersList:
        dirPath = convertToPlatformPath(path)
        if not os.path.exists(dirPath):
          os.makedirs(dirPath)
    except Exception as error:
      cls.logger.warning(str(error))
      ret = False

    return ret


  @classmethod
  def deleteFolders(cls, foldersList):
    """
      Deletes folders specified in the list.
      :param foldersList: List of folders to delete.
      return ret: True if folder is successfully deleted or if it doesn't exist.
    """
    ret = True
    try:
      for path in foldersList:
        dirPath = convertToPlatformPath(path)
        if os.path.exists(dirPath):
          shutil.rmtree(dirPath)
        else:
          cls.logger.warning(dirPath + ' folder doesn\'t exist.')
    except Exception as error:
      cls.logger.warning(str(error))
      ret = False

    return ret

  @classmethod
  def createFolderLinks(cls, foldersToLink):
    """
      Creates links from provided dict {source : link}.
      :param foldersList: List of dictionaries with source path as key and destination path (link) as value.
      :return ret: True if all links are created. Otherwise False.
    """
    ret = True
    for dict in foldersToLink:
      for source, destination in dict.items():
        if os.path.exists(source):
          ret = cls.makeLink(convertToPlatformPath(source), convertToPlatformPath(destination))
          if not ret:
            break

    return ret

  @classmethod
  def deleteFolderLinks(cls, foldersToLink):
    """
      Deletes links from provided dict {source : link}.
      :param foldersList: List of dictionaries with source path as key and destination path (link) as value.
      :return ret: True if all links are deleted. Otherwise False.
    """
    ret = True
    for dict in foldersToLink:
      for source, destination in dict.items():
        ret = cls.deleteLink(convertToPlatformPath(destination))
        if not ret:
          break

    return ret

  @classmethod
  def copyFolder(cls, source, destination):
    ret = True
    if os.path.exists(source):
      try:
        shutil.copytree(source,destination)
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
    else:
      cls.logger.error(source + ' folder doesn\'t exist.')
      ret = False
    return ret

  @classmethod
  def copyFile(cls, source, destination):
    """
      Copies file.
      :param source: File to copy
      :param destination: PAth to folder where file will be copied.
      :return ret: True if file successfully copied.
    """
    ret = True
    if os.path.isfile(source):
      try:
        shutil.copyfile(source, destination)
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
    else:
      cls.logger.warning(source + ' file doesn\'t exist')
      ret = False
    
    return ret

  @classmethod
  def deleteFiles(cls, files):
    """
      Deletes list of files.
      :param files. List of files to delete.
      :return ret: True if file is deleted or if it doesn't exist.
    """
    ret = True
    for file in files:
      if os.path.isfile(file):
        try:
          os.remove(file)
        except Exception as error:
          ret = False
          cls.logger.error(str(error))
      else:
        cls.logger.warning(file + ' file doesn\'t exist')
    
    return ret

  @classmethod
  def copyFilesFromDict(cls, filesToCopy):
    """
      Copies files from provided dict {sourceFilePath : destinationFilePath}.
      :param filesToCopy: List of dictionaries with source file path as key and destination path as value.
      :return ret: True if all files are successfully copied.
    """
    ret = True

    for dict in filesToCopy:
      for source, destination in dict.items():
        filePath = convertToPlatformPath(source)
        if os.path.isfile(filePath):
          try:
            shutil.copyfile(filePath, convertToPlatformPath(destination))
          except Exception as error:
            ret = False
            cls.logger.error(str(error))

    return ret

  @classmethod
  def pushd(cls, path):
    """
      Changes current working directory. Push old working path to stack.
      :param path: New working path
    """
    cls.logger.debug('pushd ' + path)
    cls.pushstack.append(os.getcwd())
    os.chdir(path)

  @classmethod
  def popd(cls):
    """
      Changes current working directory to previous. Pops old working path from stack.
    """
    cls.logger.debug('popd ' + cls.pushstack[-1])
    os.chdir(cls.pushstack.pop())


  @classmethod
  def getFilesWithExtensionsInFolder(cls, folders, extensions, folderToIgnores = (), stringLimit = 7000):
    """
      Creates list of all file paths with specified extensions in specified list of folders.
      :param folders: List of folders in which search for specified files will be performed.
      :param extensions: List of file extensions.
      :param folderToIgnores: List of folders to ignore in search.
      :param stringLimit: Max limit for the string with file paths
      :return listOfPaths: List of strings with file paths.
    """
    listOfFiles = ''
    listOfPaths = []
    for folder in folders:
      if os.path.exists(convertToPlatformPath(folder)):
        for root, dirs, files in os.walk(convertToPlatformPath(folder)):
          if not root.endswith(folderToIgnores):
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
    """
      Insert additional dependencies for specified target.
      :param gnFile: Gn file to update.
      :param target: Target whose dependencies need to be updated.
      :param dependency: Dependency to add.
      :return ret: True if successfully update, otherwise False.
    """
    ret = True
    if os.path.exists(gnFile):
      try:
        #Search for "name_of_target"
        targetMark = '(\"' + target + '\")'
        #regex search for deps i.e. 'deps = ['. Re search for: spaces, 'deps', spaces, '=', spaces, '[' 
        depsRegex = r'\s*deps\s*=\s*\[*'
        depsFlag = False
        insertFlag = False
        #Read gn file content
        with open(gnFile, 'r') as gnReadFile:
          gnContent = gnReadFile.readlines()
        #Open file for writing
        with open(gnFile,'w') as gnWriteFile:
          for line in gnContent:
            gnWriteFile.write(line)
            #Check if read line contains 'name_of_target', and set depsFlag to true if contains
            if targetMark in line:
              depsFlag = True
            else:
              if depsFlag:
                #If desired target is found, search fo deps and set insertFlag to true if found
                if re.findall(depsRegex,line) != []:
                  insertFlag = True
                  depsFlag = False
              elif insertFlag:
                #If deps is found insert new dependecy
                gnWriteFile.write('"' + dependency + '",')
                insertFlag = False
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
        cls.logger.error('Failed updating target ' + target + ' with dependency ' + dependency + ' in gn file ' + gnFile)
    else:
      ret = False
      cls.logger.error('Gn file ' + gnFile + ' doesn\'t exist')

    return ret

  @classmethod
  def backUpAndUpdateGnFile(cls, filePath, targetToUpdate, dependencyToAdd):
    """
      Backups specified gn files and updates dependency for target in that file.
      :param filePath: Gn file path.
      :param targetToUpdate: Name of the target to update.
      :param dependencyToAdd: List of dependecies to add.
      :return ret: True if successfully updated.
    """
    ret = True
    if os.path.isfile(filePath):
      try:
        #Backup gn file
        shutil.copyfile(filePath, filePath + '.bak')
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
        cls.logger.error('Failed creating ' + filePath + ' backup file')
      if ret:
        #Add dependencies
        for dependecy in dependencyToAdd:
          ret = cls.importDependencyForTarget(filePath, targetToUpdate, dependecy)
    else:
      ret = False
      cls.logger.warning(filePath + ' doesn\'t exist.')
    
    return ret

  @classmethod
  def returnOriginalFile(cls, filePath):
    """
      Replace file with its backup version.
      :param filePath: Path to file to revert to original state.
      :return ret: True if original file is recovered.
    """
    ret = True
    backupFilePath = filePath + '.bak'
    if os.path.isfile(filePath) and os.path.isfile(backupFilePath):
      try:
        shutil.copyfile(backupFilePath, filePath)
        os.remove(backupFilePath)
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
        cls.logger.error('Failed replacing ' + filePath + ' with its backup version.')
    else:
      ret = False
      cls.logger.warning(filePath + ' or its backup doesn\'t exist.')
    
    return ret

  @classmethod
  def getValueForTargetAndPlatformDict(cls, dict, target, platform):
    """
      Extracts value from dict for specific target and platform. Dict example: config.TARGET_WRAPPER_SOLUTIONS
      :param dict: Dictionary to extract from.
      :param target: Target name, that is the key for the inner dict.
      :param platform: Platform name, that is the key for the second inned dict.
      :return ret: Value if found. Otherwise ''.
    """
    ret = ''
    if dict == None:
      return ret

    targetDict = dict.get(target,None)
    if targetDict != None:
      ret = targetDict.get(platform,'')
      if ret == '':
        cls.logger.warning('There is no data for ' + target + ' ' + platform)
      else:
        cls.logger.info('Data for ' + target + ' ' + platform + ' is ' + str(ret))
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
    if cls.logger.logToFile:
      tempFile = subprocess.PIPE
    else:
      tempFile = None
    commandToExecute = ''
    for command in commands:
      if len(commandToExecute) > 0:
        commandToExecute = commandToExecute + ' && ' + command
      else:
        commandToExecute = commandToExecute + command
    try:
      if not shouldLog:
        tempFile = open(os.devnull, 'w')
      #Execute command
      cls.logger.debug('Running subprocess: \n' + commandToExecute)
      if userEnv == None:
        process = subprocess.Popen(commandToExecute, shell=False, stdin=subprocess.PIPE, stdout=tempFile, stderr=subprocess.STDOUT)
      else:
        process = subprocess.Popen(commandToExecute, shell=False, stdin=subprocess.PIPE, stdout=tempFile, stderr=subprocess.STDOUT, env=userEnv)

      #Add created subprocess to the list of active subprocesses, so it can be terminated on script termination.
      cls.actviveSubprocessList.append(process)

      #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
      stdout, stderr = process.communicate()
      
      if cls.logger.logToFile:
        cls.logger.debug(stdout)
      if process.returncode != 0:
        result = ERROR_SUBPROCESS_EXECUTAION_FAILED
        cls.logger.error(str(stderr))

    except Exception as error:
      result = ERROR_SUBPROCESS_EXECUTAION_FAILED
      cls.logger.error(str(error))
    finally:
      if process != None:
        cls.terminateSubprocess(process)

    if result != NO_ERROR:
      cls.logger.error(error_codes[result])

    return result
  
  @staticmethod
  def executeCommand(commandToExecute):
    """
      Runs provided command line as subprocess, and returns stdout.
      :param commandToExecute: Command to execute.
      :param stdout: Returns stdout, if command is executes successfully.  Otherwise it returns 'error' string.
    """
    try:
      process = subprocess.Popen(commandToExecute, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      stdout, stderr = process.communicate()

      if process.returncode == 0:
        if stdout.endswith("\r\n"): return stdout[:-2]
        if stdout.endswith("\n") or stdout.endswith("\r"): return stdout[:-1]
      else:
        raise Exception('Subprocess execution failed.\n' + str(stderr))

    except Exception as error:
      print("Error executing command: " + commandToExecute)
      print(str(error))
      return 'error'
    return stdout

  @classmethod
  def terminateSubprocess(cls, process = None):
    """
      Terminate running porcesses.
      :param process: Process to terminate. If passed value is None, 
                      terminate all processes.
    """
    try:
      if process != None:
        process.terminate()
        cls.actviveSubprocessList.remove(process)
      else:
        for prc in cls.actviveSubprocessList:
          prc.terminate()
        while len(cls.actviveSubprocessList) > 0:
          cls.actviveSubprocessList.pop()
    except Exception as error:
      cls.logger.error('Failed subprocess termination')
      cls.logger.error(str(error))

  @classmethod
  def filesInFolder(cls,path):  
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

  @classmethod
  def copyAllFilesFromFolder(cls, source, destination):
    """
      Copies all file from source folder (subfolders are ignored) to destination folder.
      :param source: Path to folder from where all file will be copied.
      :param destination: Path to folder where files will be copied.
      :return ret: True if all files are copied.
    """
    ret = True

    if os.path.exists(source):
      for file in cls.filesInFolder(source):
        if file not in config.FILES_TO_IGNORE_FOR_COPYING:
          if not os.path.exists(destination):
            cls.createFolders([destination])
          ret = cls.copyFile(os.path.join(source,file), os.path.join(destination,file))
          if not ret:
            break
    
    return ret

  @classmethod
  def getKeyValueFromRegistry(cls, parentKey, key, value_name):
    """
      Obtain key value from Windows regisry.
      :return: Key value if exists, otherwise None.
    """
    ret = None

    try:
      registryKey = OpenKey(parentKey, key)
      ret, typ = QueryValueEx(registryKey, value_name)
      CloseKey(registryKey)
    except Exception as error:
       cls.logger.error(str(error))

    return ret

  @classmethod
  def checkIfFolderContainsFiles(cls, folderPath, fileNames):
    """
      Checks if specified folder contains all specified files.
      :param folderPath: Path of the folder where files will be searched
      :param fileNames: list of the filenames to check
      :return ret: True if all files are found, otherwise False
    """
    ret = True
    for file in fileNames:
      destinationFile =  os.path.join(folderPath, file)
      ret = ret and os.path.isfile(destinationFile)

    return ret
    