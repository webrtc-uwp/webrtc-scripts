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
    executablePath = None
    if sys.version_info[0] < 3.3:
      import distutils.spawn
      executablePath = distutils.spawn.find_executable(toolName)
    else:
      import shutil 
      executablePath = shutil.which(toolName)

    if executablePath != None:
      return True

    return False

  @staticmethod
  def addPath(path):
    print('Adding ' + path + ' to PATH.')
    sys.path.append(path)

@staticmethod
def makeLink(source,destination):
  subprocess.call('cmd', '/c', 'mklink', '/J', destination, source)
