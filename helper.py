"""
  Holds some helper fumctions.
"""
import os
import platform
import sys
import pip

try:
    input = raw_input
except NameError:
    pass

def convertToPlatformPath(path):
  listOfString = []
  if '/' in path:
    listOfString = path.split('/')
  elif '\\\\' in path:
    listOfString = path.split('\\\\')
  elif '\\' in path:
    listOfString = path.split('\\')
  if len(listOfString) > 0:
    #For win it is necessary to add \\ for drive letter
    if ':' in listOfString[0]:
      listOfString[0] = listOfString[0] + os.sep
    return os.path.join(*listOfString)
  return path

def getCPUFamily(machineType):
  if machineType.lower() == 'i386':
    return 'x86'
  elif  machineType.lower() == 'amd64':
    return 'x64'

  return 'x64'

def iterateDict(dictonary):
  if hasattr(dict, 'iteritems'):
    return dictonary.iteritems() 
  else: 
    return iter(dictonary.items())

def str_to_bool(value):
  if value.lower() == 'true':
    return True
  else:
    return False

def bool_to_str(value):
  if value:
    return 'True'
  else:
    return 'False'

def module_exists(module_name):
  """
  :param module_name: name of the module that needs to be checked.
  :return: True/False based on if the input module exists or not
  """
  try:
    __import__(module_name)
  except ImportError:
    return False
  else:
    return True

def install(package):
    try:
        import package
    except:
        import sys
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def yes_no(question):
  """
  Ask user a yes or no question and evaluate answer.
  :param question: question user is asked in a form of a string.
  :return answer: returns True/False based on input.
  """
  yes = {'yes', 'y', 'ye', ''}
  no = {'no', 'n'}
  while True:
    sys.stdout.write(question + ' (y/n) ')
    choice = input().strip()
    choice = choice.lower()
    if choice in yes:
      return True
    elif choice in no:
      return False
    else:
      sys.stdout.write("Please respond with 'yes' or 'no'\n")
