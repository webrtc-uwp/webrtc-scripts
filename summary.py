from datetime import timedelta

from logger import Logger, ColoredFormatter
from errors import NO_ERROR
from helper import iterateDict

class Summary:

  action_results = dict()

  @classmethod
  def addSummary(cls, action, target, platform, cpu, configuration, result, time = 0):
    key = target + '___' + platform + '___' + cpu + '___' + configuration

    resultActionDict =  cls.action_results.get(action,dict())
    resultDict = resultActionDict.get(key,dict())
    resultDict['result'] = result
    resultDict['time'] = time 
    resultActionDict[key] = resultDict

    cls.action_results[action] = resultActionDict

  @classmethod
  def addNugetSummary(cls, target, platform, result, time = 0):
    key = target + '___' + platform

    resultActionDict =  cls.action_results.get('createNuget',dict())
    resultDict = resultActionDict.get(key,dict())
    resultDict['result'] = result
    resultDict['time'] = time 
    resultActionDict[key] = resultDict

    cls.action_results['createNuget'] = resultActionDict

  @classmethod
  def checkIfCreateNugetFailed(cls, target, platform):
    ret = False
    actionDict = cls.action_results.get('createNuget',None)
    if actionDict != None:
      key = target + '___' + platform
      resultDict = actionDict.get(key,None)
      if resultDict != None:
        if resultDict['result'] != NO_ERROR:
          ret = True

    return ret

  @classmethod
  def printSummary(cls, executionTime = 0):
    Logger.printColorMessage('\n========================================= SUMMARY ========================================= \n', ColoredFormatter.YELLOW)
    for key, value in iterateDict(cls.action_results):
      if key != 'cleanup':
        Logger.printColorMessage('ACTION: ' + key + '', ColoredFormatter.WHITE)
        for resultKey, resultValue in iterateDict(value):
          if resultValue['result'] == NO_ERROR:
            Logger.printColorMessage('     SUCCESSFUL: ' + resultKey.replace('___', '   ') + '      execution time: ' + str(timedelta(seconds=resultValue['time'])) + '', ColoredFormatter.GREEN)
          else:
            Logger.printColorMessage('         FAILED: ' + resultKey.replace('___', '   ') + '      execution time: ' + str(timedelta(seconds=resultValue['time'])) +  '', ColoredFormatter.RED)
      Logger.printColorMessage('\n------------------------------------------------------------------------------------------- ', ColoredFormatter.YELLOW)
    Logger.printColorMessage('Total execution time: ' + str(timedelta(seconds=executionTime)), ColoredFormatter.YELLOW)

  @classmethod
  def checkIfActionFailed(cls, action, target, platform, cpu, configuration):
    ret = False
    actionDict = cls.action_results.get(action,None)
    if actionDict != None:
      key = target + '___' + platform + '___' + cpu + '___' + configuration
      resultDict = actionDict.get(key,None)
      if resultDict != None:
        if resultDict['result'] != NO_ERROR:
          ret = True

    return ret
