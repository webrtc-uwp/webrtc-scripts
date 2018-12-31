import os
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
        cls.nugetExePath = Settings.nugetFolderPath + '/nuget.exe'
        cls.logger = Logger.getLogger('nugetUtility')

    @classmethod
    def nuget_cli(cls, nuget_command, *args):
        """
        Adds nuget cli functionality to python script trough nuget.exe
        If nuget.exe is not available, download_nuget method is called

        :param nuget_command: nuget cli command can be writtenwith or without nuget prefix.
        :param *args: aditional options and arguments for the nuget cli command
            example: CreateNuget.nuget_cli('help', '-All', '-Markdown')
        """
        ret = NO_ERROR
        if not os.path.exists(cls.nugetExePath):
            cls.download_nuget()

        # allows nuget command to be written with or wihout 'nuget ' prefix
        if 'nuget ' in nuget_command:
            nuget_command = nuget_command.replace('nuget ', '')
        try:
            # absolute path to nuget.exe
            exe_path = convertToPlatformPath(cls.nugetExePath)
            full_command = [exe_path, nuget_command]
            cls.logger.info(exe_path)
            # add options or other arguments to the nuget command
            for cmd in args:
                full_command.append(cmd)
            
            p = Popen(full_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()

            print(output)
            if err:                
                cls.logger.error(err)
            if '403 (Forbidden)' in err:
                print(cls.api_key_instruction)
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
            urllib.request.urlretrieve(config.NUGET_URL, cls.nugetExePath)

        # Python 2:
        if module_exists('urllib2'):
            import urllib2
            cls.logger.info('Downloading NuGet.exe file with urllib2...')
            with open(cls.nugetExePath, 'wb') as f:
                f.write(urllib2.urlopen(config.NUGET_URL).read())
                f.close()
        cls.logger.info("Download Complete!")
