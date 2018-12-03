import os
import subprocess
from datetime import datetime
from errors import NO_ERROR

from utility import Utility
import run

def executeCommand(commandToExecute):
  process = subprocess.Popen(commandToExecute, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
  stdout, stderr = process.communicate()

  if stdout.endswith("\r\n"): return stdout[:-2]
  if stdout.endswith("\n") or stdout.endswith("\r"): return stdout[:-1]


  return stdout

def main():

  sdk_root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
  os.chdir(sdk_root_path)
  gitRepo = executeCommand('git remote get-url origin')
  gitBranch = executeCommand('git rev-parse --abbrev-ref HEAD')

  timeSuffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  folderName = os.path.basename(os.getcwd()) + '_' + timeSuffix
  
  os.chdir('..')
  print('Cloning repo: ' + gitRepo + '           branch: ' + gitBranch)
  print('Cloning into ' + folderName + '  ...')
  #result = Utility.runSubprocess(['git clone --recursive ' + gitRepo + ' -b ' + gitBranch + ' ..\\' + folderName + ' > ' + logFile + ' 2>&1'], True)
  result = Utility.runSubprocess(['git clone --recursive ' + gitRepo + ' -b ' + gitBranch + ' .\\' + folderName ], True)
  
  if result == NO_ERROR:
    logFile = os.path.join(os.getcwd(),'repoCheckLog_' + timeSuffix + '.txt')
    os.chdir(os.path.join('.\\',folderName))
    print('Preparing and building projects ...')
    os.system('python scripts\\run.py --noColor > ' + logFile + ' 2>&1')
  


if  __name__ =='__main__': main()