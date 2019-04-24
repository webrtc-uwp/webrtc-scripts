import os
import subprocess
import argparse
from datetime import datetime

from consts import MAX_SDK_ROOT_PATH_LENGTH
from utility import Utility
import run

def createDestinationFolder(repo, destinationRootPath, generateFolderName = True):
  """
    Determines path if path is not already provided, and creates folder in which repo will be cloned.
    :param repo: Repo to clone. Passed just to extract repo name.
    :param destinationRootPath: Root folder of the folder that will be created if generateFolderName is True.
                                Otherwise it is folder in which repo will be cloned.
    :param generateFolderName: If True, it will be generated folder name in which repo will be cloned.
                               If False it will used provided folder as cloning destination.
    :return destinationPath: Path where repo will be cloned, or empty string if some error occurs.
  """
  destinationPath = ''
  if not generateFolderName:
    #Check if lengt of the path is not longer than one supported by the webrtc develop system.
    if MAX_SDK_ROOT_PATH_LENGTH - len(destinationRootPath) < 0:
      print('Destination path ' + destinationRootPath + ' is too long. Please, specify another folder with shorter path where repo will be cloned.')
    else:
      if os.path.exists(destinationRootPath):
        print('Folder with that name already exists')
      else:
        destinationPath = destinationRootPath
  else:
    #Extract repo name from repo url
    repoName = repo.split("://")[1].split("/")[-1].split('.')[0]
    #Create time suffix whic will be added at the end of folder name
    timeSuffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    destinationPathTemp = os.path.join(destinationRootPath,repoName)
    lengthDelta = MAX_SDK_ROOT_PATH_LENGTH - len(destinationPathTemp)
    
    if lengthDelta > len(timeSuffix):
      #If path, with time suffix, length is not greater than MAX_SDK_ROOT_PATH_LENGTH (64), create folder with suffix.
      destinationPath = os.path.join(destinationRootPath, repoName + '_' + timeSuffix)
    elif lengthDelta > 3:
      #If path with time suffix is greater than allowed, create folder with name repo_name_XX
      destinationPathTemp = os.path.join(destinationRootPath, repoName + '_00')
      if os.path.exists(destinationPathTemp):
        index = 1
        while True:
          if index < 10:
            destinationPathTemp = os.path.join(destinationRootPath, repoName + '_0' + str(index))
          else:
            destinationPathTemp = os.path.join(destinationRootPath, repoName + '_' + str(index))
          if os.path.exists(destinationPathTemp):
            index += 1
            continue
          else:
            destinationPath = destinationPathTemp
            break
      else:
        destinationPath = destinationPathTemp
    else:
      print('Generated destination path ' + destinationPathTemp + ' is too long. Please, specify folder with shorter path where repo will be cloned.')

  #If path is valid, create a folder
  if destinationPath != '':
    os.makedirs(destinationPath)

  return destinationPath

def main():

  destinationPath = ''

  #Destination path is not mandatory input argument
  parser = argparse.ArgumentParser()
  parser.add_argument('destinationPath', nargs='?', help='Path where repo will be cloned')

  #Change to sdk root folder, and get info about repo and branch
  sdk_root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
  os.chdir(sdk_root_path)
  gitRepo = Utility.getRepo()
  gitBranch = Utility.getBranch()
  
  os.chdir('..')
  
  if parser.parse_args().destinationPath:
    #If destination path is provided as input parameter, pass False for generateFolderName
    destinationPath =  createDestinationFolder(gitRepo, parser.parse_args().destinationPath, False)
  else:
    #Create folder with auto generated name
    destinationPath =  createDestinationFolder(gitRepo, os.getcwd())

  
  if destinationPath != '':
    print('Cloning repo: ' + gitRepo + '           branch: ' + gitBranch)
    print('Cloning into ' + destinationPath + '  ...')
    #Change current working folder to one just created and clone repo in it
    os.chdir(destinationPath)
    result = Utility.executeCommand('git clone --recursive ' + gitRepo + ' -b ' + gitBranch + ' .')
    
    if result != 'error':
      #If repo is successfully cloned, run script for building webrtc libs. Log  will be saved in repoCheckLog_folder_name.txt
      logFile = os.path.join(os.getcwd(),'..','repoCheckLog_' + os.path.basename(destinationPath) + '.txt')
      os.chdir(os.path.join('.\\',destinationPath))
      print('Preparing and building projects ...')
      os.system('python scripts\\run.py --noColor > ' + logFile + ' 2>&1')
  else:
    print('Script execution is terminated.')
  


if  __name__ =='__main__': main()
  