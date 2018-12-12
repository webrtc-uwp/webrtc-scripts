"""
  Holds some helper fumctions.
"""
import os
import platform

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
