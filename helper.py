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