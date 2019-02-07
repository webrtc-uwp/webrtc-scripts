import os
import glob
import re
from subprocess import Popen, PIPE, call

from errors import NO_ERROR, ERROR_ACQUIRE_NUGET_EXE_FAILED
from settings import Settings
from helper import convertToPlatformPath, module_exists
from logger import Logger,ColoredFormatter
import config

class NugetUtility:
  api_key_instruction = '\033[94m' + r"""
    ===================================================================================================================
    Nuget server API key not set or not valid. To set the api key do the following:
    1) Get the API key from nuget.org
    2) Set the API key by eather:
        a) Changing the value of the nugetAPIKey variable inside userdef.py
        b) running command 'python .\scripts\run.py -setnugetkey <key>' from the command line (webrtc-uwp-sdk folder)
        c) running command nuget 'nuget setapikey <key>' from the command line (assuming you have nuget cli installed)
    ===================================================================================================================
    """ + '\033[0m'
  @classmethod
  def setUp(cls):
      cls.logger = Logger.getLogger('nugetUtility')

  @classmethod
  def nuget_cli(cls, nuget_command, *args):
    """
      Adds nuget cli functionality to python script trough nuget.exe
      If nuget.exe is not available, download_nuget method is called

      :param nuget_command: nuget cli command can be writtenwith or without nuget prefix.
      :param *args: aditional options and arguments for the nuget cli command
      :return: NO_ERROR if nuget command is executed successfully. Otherwise returns error code
        example: CreateNuget.nuget_cli('help', '-All', '-Markdown')
    """
    ret = NO_ERROR
    if not os.path.isfile(Settings.nugetExecutablePath):
      cls.download_nuget()

    # allows nuget command to be written with or wihout 'nuget ' prefix
    if 'nuget ' in nuget_command:
      nuget_command = nuget_command.replace('nuget ', '')
    try:
      # absolute path to nuget.exe
      full_command = [Settings.nugetExecutablePath, nuget_command]
      #Used to print command to cmd
      printCommand = 'Running command: nuget ' + nuget_command + ' '
      # add options or other arguments to the nuget command
      for cmd in args:
        printCommand += cmd + ' '
        full_command.append(cmd)

      cls.logger.info(printCommand)

      p = Popen(full_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
      output, err = p.communicate()

      if 'The name specified has already been added to the list of available package sources. Please provide a unique name.' in err:
        cls.logger.warning('Source with that name already exists.')
        return 'run update'
      if 'The source specified has already been added to the list of available package sources. Please provide a unique source.' in err:
        cls.logger.warning(err)
        return 'alerady added'

      if '403' in err:
        print(cls.api_key_instruction)
          
      if p.returncode != 0:
        ret = ERROR_ACQUIRE_NUGET_EXE_FAILED
        cls.logger.error(err)

      if 'nuget list' in printCommand:
        return output
      else:
        cls.logger.debug("Output: ")
        cls.logger.debug(output)
  
    except Exception as errorMessage:
      cls.logger.error(errorMessage)
      ret = ERROR_ACQUIRE_NUGET_EXE_FAILED
    return ret

  @classmethod
  def download_nuget(cls):
    """
      Download latest nuget.exe file from nuget.org
    """
    # Python 3:
    if module_exists('urllib.request'):
      import urllib
      cls.logger.info('Downloading NuGet.exe file with urllib.request...')
      urllib.request.urlretrieve(config.NUGET_URL, Settings.nugetExecutablePath)
    elif module_exists('urllib2'):  # Python 2:
      import urllib2
      cls.logger.info('Downloading NuGet.exe file with urllib2...')
      with open(Settings.nugetExecutablePath, 'wb') as f:
        f.write(urllib2.urlopen(config.NUGET_URL).read())
        f.close()
    cls.logger.info("Download Complete!")

  @classmethod
  def get_latest_package(cls):
    search = convertToPlatformPath(Settings.nugetFolderPath+'/*.nupkg')
    list_of_files = glob.glob(search)
    if list_of_files != []:
      latest_file = max(list_of_files, key=os.path.getctime)
      #Remove folder path from the latest file string
      latest_file = latest_file.replace(convertToPlatformPath(Settings.nugetFolderPath), '')
      #Remove target from the file exposing the version and .nupkg extention
      latest_file = latest_file.split('.', 1)[-1]
      #Remove .nupkg extention exposing only the latest built version of the nuget file.
      latest_version = latest_file.replace('.nupkg', '')
      
      return latest_version
    else:
      cls.logger.warning('No nuget package found inside the selected folder, please run createnuget action.')

  @classmethod
  def add_nuget_local_source(cls, name='Local_NuGet_packages'):
    """
      Adds nuget folder from userdef as a non-HTTP nuget package source.
    """
    #Package source name (how it will be set in NuGet.Config)
    srcName = name
    if convertToPlatformPath(Settings.nugetFolderPath) in convertToPlatformPath('./webrtc/windows/nuget'):
      srcName = 'SDK_NuGet_package'
    #Package source path for the srcName (how it will be set in NuGet.Config)
    srcPath = os.path.abspath(Settings.nugetFolderPath)
    try:
      result = NugetUtility.nuget_cli('sources', 'Add', '-Name', srcName, '-Source', srcPath)

      if result == NO_ERROR:
        cls.logger.debug('Package Source with Name: ' + srcName + ' and path: ' + srcPath + ' added successfully.')
      #If package source with the same name already exists update path for that source
      elif 'run update' in result and 'SDK NuGet package' in srcName:
        cls.logger.debug('Running source update.')
        NugetUtility.nuget_cli('sources', 'update', '-Name', srcName, '-Source', srcPath)
        cls.logger.debug('Package Source with Name: ' + srcName + ' and path: ' + srcPath + ' updated successfully.')
      elif name in srcName and 'alerady added' not in result:
        number = re.search(r'\d+$', srcName)
        # if srcName does't end in number add a number, else increment that number.
        if number is None:
          srcName = srcName + '_2'
        else:
          number = number.group()
          newNumber = int(number) + 1
          srcName = srcName.replace(str(number), str(newNumber))
        #Add new name to nuget sources
        NugetUtility.add_nuget_local_source(name=srcName)
    except Exception as error:
      cls.logger.error(str(error))

