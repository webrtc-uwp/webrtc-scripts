"""
  Holds some helper fumctions.
"""
import os

def convertToPlatformPath(path):
  listOfString = []
  if '/' in path:
    listOfString = path.split('/')
  elif '\\\\' in path:
    listOfString = path.split('\\\\')
  elif '\\' in path:
    listOfString = path.split('\\')
  return os.path.join(*listOfString)