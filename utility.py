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
  def checkIfGitIsInstalled():
    print("IMPLEMENT: GIT CHECK - SHOW MESSAGE IF NOT ISTALLED - BREAK THE APP")

  @staticmethod 
  def checkIfPerlIsInstalled():
    print("IMPLEMENT: Perl CHECK - SHOW MESSAGE IF NOT ISTALLED - BREAK THE APP")

  @staticmethod
  def addPath(path):
    print('Adding ' + path + ' to PATH.')
    sys.path.append(path)

@staticmethod
def makeLink(source,destination):
  subprocess.call('cmd', '/c', 'mklink', '/J', destination, source)
