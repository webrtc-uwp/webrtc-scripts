import os
import time
import subprocess
from datetime import datetime

import config
from logger import Logger
from utility import Utility
from settings import Settings
import errors
from errors import error_codes, NO_ERROR
import helper

class UnitTestRunner:
  @classmethod
  def init(cls):
    """
      Initiates logger object.
    """
    cls.logger = Logger.getLogger('Unit tests')

  @classmethod
  def run(cls, targetName, platform, cpu, configuration, builderWorkingPath = None):
    """
      Start target building process.
      :param targetName: Name of the main target (ortc or webrtc)
      :param platform: Platform name
      :param cpu: Target CPU
      :param configuration: Configuration
      :param builderWorkingPath: Path where generated projects for specified target.
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    start_time = time.time()
    ret = NO_ERROR
    cls.failedTestsCounter = 0
    cls.totalNumberOfTests = 0
    cls.logger.info('Running unit tests for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #If path with generated projects is not specified generate path from the input arguments
    if builderWorkingPath == None:
      builderWorkingPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH, targetName, platform, cpu, configuration)

    workingDir = os.path.join(Settings.webrtcPath,builderWorkingPath)

    #If folder for specified target and platform doesn't exist, stop further execution
    if not os.path.exists(workingDir):
      cls.logger.error('Output folder at ' + workingDir + ' doesn\'t exist. It looks like prepare is not executed. Please run prepare action.')
      return errors.ERROR_UNIT_TESTS_WORKING_FOLDER_NOT_EXIST

    #Change current working directory to one with built unit tests
    Utility.pushd(workingDir)

    #Unit tests summary file
    summaryFileName = 'UnitTests_' + platform + '_' + cpu + '_' + configuration
    summaryPath = os.path.join(Settings.userWorkingPath ,summaryFileName + '.log')
    #If unit tests summary file already exists add date and time sufix
    if os.path.isfile(summaryPath):
      summaryFileName += '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
      summaryPath = os.path.join(Settings.userWorkingPath ,summaryFileName)
    cls.unitTestSummaryLogFile = open(summaryPath,'w')

    #Run all specified unit tests
    for unitTest in Settings.unitTestsToRun:
      ret = cls.executeUnitTest(unitTest)
    
    cls.unitTestSummaryLogFile.write(config.UNIT_TEST_SUMMARY_TOTAL_SEPARATOR + 'TOTAL NUMBER OF TESTS: ' + str(cls.totalNumberOfTests) + '\n')
    cls.unitTestSummaryLogFile.write('TOTAL NUMBER OF FAILED TESTS: ' + str(cls.failedTestsCounter) + '\n')
    cls.unitTestSummaryLogFile.close()
    
    cls.logger.info('Total number of unit tests is ' + str(cls.totalNumberOfTests))

    if cls.failedTestsCounter == 0:
      cls.logger.info('All unit tests passed.')
    elif cls.failedTestsCounter == 1:
      cls.logger.warning(str(cls.failedTestsCounter) + ' unit test has failed. You can check details in file ' + os.path.abspath(cls.unitTestSummaryLogFile.name))
    else:
        cls.logger.warning(str(cls.failedTestsCounter) + ' unit tests have failed. You can see the details in file ' + os.path.abspath(cls.unitTestSummaryLogFile.name))      

    #Switch to previously working directory
    Utility.popd()

    if ret == NO_ERROR:
      cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration + ', finished successfully!')
    end_time = time.time()
    cls.executionTime = end_time - start_time
    return ret

  @classmethod
  def executeUnitTest(cls, unittest):
    """
      Executes specified unit test.
      :param unittest: Unit test executable
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    ret = NO_ERROR
    #Take tests that would be execute under specified unit test
    #listOfTests = config.AVAILABLE_UNIT_TESTS[unittest]
    listOfTests = Settings.unitTests[unittest]
    #Unit test is an exeutable file
    cmdLine = unittest
    testsToRunSeparately = ''
    cls.filter = '--gtest_filter='
    outputFile = unittest + '.txt'
    #Delete old unit test log file
    if not Utility.deleteFiles([outputFile]):
      return errors.ERROR_UNIT_TESTS_FAILED_TO_DELETE_OLD_LOG

    if '*' in listOfTests:
      #Check if there are some tests that needs to be run separately
      if len(listOfTests) > 1:
        #Tests that wiil be executed eparately, needs to be excluded from main tests bundle
        for testName in listOfTests[1:]:
          testsToRunSeparately += testName + ':'
        cmdLine += ' ' + cls.filter + '-' + testsToRunSeparately
        ret = cls.runUnitTestSubprocess(cmdLine, outputFile)
        if ret == NO_ERROR or ret == errors.ERROR_UNIT_TEST_FAILED:
          #Run separately tests
          for testName in listOfTests[1:]:
            cmdLine = unittest + ' ' + cls.filter + testName
            ret = cls.runUnitTestSubprocess(cmdLine, outputFile, True)
            if not ret == NO_ERROR and not ret == errors.ERROR_UNIT_TEST_FAILED:
              cls.logger.error('Failed running unit test ' + cmdLine)
              break
        else:
          cls.logger.error('Failed running unit test ' + unittest)
      else:
        #Run all unit tests in the bundle
        ret = cls.runUnitTestSubprocess(cmdLine, outputFile)
    else:
      #Run only specified unit tests
      for testName in listOfTests:
        cmdLine = unittest + ' ' + cls.filter + testName
        ret = cls.runUnitTestSubprocess(cmdLine, outputFile, True)
        if not ret == NO_ERROR and not ret == errors.ERROR_UNIT_TEST_FAILED:
          cls.logger.error('Failed running unit test ' + cmdLine)
          break
    
    if ret == NO_ERROR or ret == errors.ERROR_UNIT_TEST_FAILED:
      #Parse output file to get info about total/failed tests
      ret = cls.parseResults(unittest, outputFile)
    return ret

  @classmethod
  def parseResults(cls, unitTestName, unitTestLogFile):
    """
      Parses unit tests log file, and writes to summary info about total number of tests, and list of failed tests.
      :param unitTestName: Unit test name
      :param unitTestLogFile: File to parse
    """
    ret = NO_ERROR
    unitTestFailures = 0
    numberOfUnitTests = 0
    outputRecoveryFile = unitTestName + '_Recovery.txt'
    
    if not Utility.deleteFiles([outputRecoveryFile]):
      return errors.ERROR_UNIT_TESTS_FAILED_TO_DELETE_OLD_LOG

    with open(unitTestLogFile, 'r') as fileToParse:
      fileContent = fileToParse.read()

    executedUnitTests = fileContent.split(config.UNIT_TESTS_LOG_SEPARATOR)

    cls.unitTestSummaryLogFile.write(unitTestName)
    cls.unitTestSummaryLogFile.write('\n' + config.UNIT_TEST_SUMMARY_SEPARATOR + '\n')

    for unitTest in executedUnitTests:
      testResults = unitTest.split(config.UNIT_TEST_RESULTS_SEPARATOR)
      testResult = testResults[-1]
      
      for line in testResult.split('\n'):
        if config.UNIT_TEST_RESULTS_TOTAL_NUMBER_SEPARATOR in line:
          listForNumberOfTests = line.split(' ')
          if len(listForNumberOfTests) > 1:
            numberOfTests = listForNumberOfTests[1]
            numberOfUnitTests += int(numberOfTests)
        if config.UNIT_TEST_RESULTS_FAILED_SEPARATOR in line and 'listed below' not in line:
          testName = helper.remove_prefix(line, config.UNIT_TEST_RESULTS_FAILED_SEPARATOR + ' ')
          testName = testName.split(',')[0]
          testName = helper.remove_carriage_return(testName)
          cmdLine = unitTestName + ' ' + cls.filter + testName
          recoveryTestCounter = 0
          testPassed = False
          while recoveryTestCounter < config.UNIT_TEST_RETRY_NUMBER_FALIED_TESTS and not testPassed:
            ret = cls.runUnitTestSubprocess(cmdLine, outputRecoveryFile, True)
            recoveryTestCounter += 1
            if ret == NO_ERROR:
              testPassed = True
          if not testPassed:
            unitTestFailures += 1
            cls.unitTestSummaryLogFile.write(line + '\n')
          

    cls.totalNumberOfTests += numberOfUnitTests
    cls.failedTestsCounter += unitTestFailures
    
    #Write log to unit tests summary file
    if unitTestFailures > 0:
      cls.unitTestSummaryLogFile.write(config.UNIT_TEST_SUMMARY_TEST_SEPARATOR)
    cls.unitTestSummaryLogFile.write('Total number of tests: ' + str(numberOfUnitTests) + '\n') 
    cls.unitTestSummaryLogFile.write('Total number of failed tests: ' + str(unitTestFailures) + '\n')
    cls.unitTestSummaryLogFile.write(config.UNIT_TEST_SUMMARY_SEPARATOR + '\n\n\n\n')
    cls.unitTestSummaryLogFile.flush()

    return ret


  @classmethod
  def runUnitTestSubprocess(cls, unittest, logToFile = '', appendToFile = False):
    """
      Runs specified unit test as subprocess.
      :param unittest: Unit test to run.
      :param logToFile: Path to unit tests log file
      :para, appendToFile: Flag to append to existing log file.
      :return result: NO_ERROR if subprocess is executed successfully. Otherwise error or subprocess returncode
    """
    result = NO_ERROR
    logFile = None
    strLog = ''
    commandToExecute = ''

    try:
      #Create a new log file, or open existing, depending on appendToFile flag
      if len(logToFile) > 0:
        if appendToFile:
          logFile = open(logToFile, 'a+')
        else:
          logFile = open(logToFile, 'w')

      #Execute command. Log goes to stdout
      cls.logger.debug('\n Running unit test: ' + unittest + '\n')
      process = subprocess.Popen(unittest, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   
      #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
      stdout, stderr = process.communicate()

      if process.returncode != 0:
        result = errors.ERROR_UNIT_TEST_FAILED
        if stderr != '':
          cls.logger.warning(str(stderr))
      #Write unit test log to file
      if stdout != None and stdout != '':
        logFile.write(stdout)
    except Exception as error:
      result = errors.ERROR_UNIT_TESTS_EXECUTION_FAILED
      cls.logger.error(str(error))
    finally:
      if process != None:
        process.terminate()
      if logFile != None:
        logFile.write(config.UNIT_TESTS_LOG_SEPARATOR)
        logFile.flush()

    if result != NO_ERROR:
      cls.logger.error(error_codes[result])

    return result
    