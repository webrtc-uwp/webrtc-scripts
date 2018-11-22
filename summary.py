from logger import Logger, ColoredFormatter
from errors import NO_ERROR
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
  def printSummary(cls):
    Logger.printColorMessage('\n\n ========================================= SUMMARY ========================================= \n', ColoredFormatter.YELLOW)
    for key, value in cls.action_results.iteritems():
      if key != 'cleanup':
        Logger.printColorMessage('ACTION: ' + key + '\n', ColoredFormatter.WHITE)
        for resultKey, resultValue in value.iteritems():
          if resultValue['result'] == NO_ERROR:
            Logger.printColorMessage('     SUCCESSFUL: ' + resultKey.replace('___', '   ') + '\n', ColoredFormatter.GREEN)
          else:
            Logger.printColorMessage('         FAILED: ' + resultKey.replace('___', '   ') + '\n', ColoredFormatter.RED)
      Logger.printColorMessage('\n\n ------------------------------------------------------------------------------------------ \n', ColoredFormatter.WHITE)


      
