import os
import sys
import logging
import subprocess
class Utility:

  @staticmethod
  def convertToPlatformPath(relativePath):
    listOfString = relativePath.split("/")
    return os.path.join(*listOfString)

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
    print('Adding ' + path + ' to PATH.')
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

  @staticmethod
  def makeLink(source,destination):
    if not os.path.exists(destination):
      print(source + '------------>' + destination)
      subprocess.call(['cmd', '/c', 'mklink', '/J', Utility.convertToPlatformPath(destination), Utility.convertToPlatformPath(source)])
