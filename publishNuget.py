import os
import time

from logger import Logger
from settings import Settings
from nugetUtility import NugetUtility
from utility import Utility
from errors import NO_ERROR, ERROR_LOADING_NUGET_PACKAGES, ERROR_SELECTING_NUGET_PACKAGES
from helper import convertToPlatformPath
from system import System
from createNuget import CreateNuget
from releaseNotes import ReleaseNotes


class PublishNuget:

    @classmethod
    def init(cls):
        cls.logger = Logger.getLogger("PublishNuget")
        cls.nugetFolderPath = Settings.nugetFolderPath
        cls.nugetExePath = cls.nugetFolderPath + '/nuget.exe'
        cls.serverURL = Settings.nugetServerURL
        cls.serverKey = Settings.nugetAPIKey
        cls.packages = []

    @classmethod
    def run(cls):
        """
        Start publish NuGet package process
        :return: NO_ERROR if successfull. Otherwise returns error code
        """
        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)

        start_time = time.time()
        ret =  NO_ERROR

        if Settings.nugetAPIKey != '':
            cls.set_api_key(cls.serverKey, cls.serverURL)
        
        #Select package that was just created.
        if hasattr(CreateNuget, 'version'):
            ret = cls.load_packages(['webrtc.'+CreateNuget.version+'.nupkg'])
        #Select package list from userdef.py
        elif Settings.nugetPackagesToPublish:
            ret = cls.load_packages(Settings.nugetPackagesToPublish)
        #Display a menu for selecting packages from NuGet folder.
        else:
            ret = cls.load_packages(cls.nugetFolderPath)
            if ret == NO_ERROR:
                ret = cls.ask_user()
        if ret == NO_ERROR:
            for package in cls.packages:
                packagePath = convertToPlatformPath(cls.nugetFolderPath+'/'+package['fullName'])
                #Api key needs to be placed diferently
                ret = cls.publish(packagePath, cls.serverURL)
        end_time = time.time()
        
        if ret == NO_ERROR:
            ReleaseNotes.set_note_version(package['packageVersionNumber'])
        cls.executionTime = end_time - start_time
        
        # return to the base directory
        Utility.popd()
        return ret

    @classmethod
    def load_packages(cls, packageList):
        """
        Evaluates and converts NuGet package name into dictionary, to make it easier to work with nuget cli
        :param packageList: List of packages to be converted, can also be a path to directory with nuget packages.
        :return: NO_ERROR if successfull. Otherwise returns error code
        """
        ret = NO_ERROR
        try:
            #Used to differenciate between a list and a path to directory
            if type(packageList) is str:
                #Check if directory exists and load the file names from it to a list
                if os.path.exists(packageList):
                    packageList = os.listdir(packageList)
                else:
                    raise Exception('NuGet folder does not exist!')
            for package in packageList:
                if package.endswith('.nupkg'):
                    packageName = package.replace('.nupkg', '')
                    #Get package id from the name
                    packageId = packageName.split('.', 1)[0]
                    #Get package version number from the name
                    packageVersionNumber = packageName.split('.', 1)[1]
                    #Convert package information into a dictionary
                    cls.packages.append({'fullName': packageName+'.nupkg', 'packageId': packageId, 'packageVersionNumber': packageVersionNumber})
        except Exception as error:
            cls.logger.error(str(error))
            ret = ERROR_LOADING_NUGET_PACKAGES
        return ret

    @classmethod
    def ask_user(cls):
        """
        Gives user an option to choose package he wishes to publish
        Must be called after load_packages method
        :return: NO_ERROR if successfull. Otherwise returns error code
        """
        ret = NO_ERROR
        try:
            print('Witch package would you like to publish to '+ cls.serverURL + ': ')
            print('0) Cancel')
            for package in cls.packages:
                index = cls.packages.index(package)+1
                #Show available packages
                print(str(index) + ') ' + package['fullName'])
            #Cancel if user didnt input number
            try:
                inputValue = input("Select package: ")
            except SyntaxError:
                inputValue = 0
            #Load only the package user selected
            if inputValue is not 0:
                inputIndex = int(inputValue) - 1
                cls.packages = [cls.packages[inputIndex]]
            else:
                raise Exception('Publishing NuGet package canceled!')
        except Exception as error:
            cls.logger.error(str(error))
            ret = ERROR_SELECTING_NUGET_PACKAGES
        return ret

    @classmethod
    def set_api_key(cls, key, address = 'default'):
        """
        Sets the api key for the nuget server
        :param key: key in a form of a string
        :param address: server URL address (optional) if left out nuget.org is assumed
        """
        if address is 'default':
            NugetUtility.nuget_cli('setapikey', key, '-Source', 'https://www.nuget.org/')
        else:
            NugetUtility.nuget_cli('setapikey', key, '-Source', address)


    @classmethod
    def publish(cls, nuget_package, address = 'default'):
        """
        Publishes NuGet package on a server of choice.
        :param nuget_package: full name of the nuget package to be published.
        :param address: server address.
        """
        ret = NO_ERROR
        if address is 'default':
            ret = NugetUtility.nuget_cli('push', nuget_package, '-Source', 'https://www.nuget.org/')
        else:
            ret = NugetUtility.nuget_cli('push', nuget_package, '-Source', address)
        return ret

    @classmethod
    def delete(cls, package_id, package_veresion, address):
        """
        Deletes NuGet package from the server.
        :param package_id: id of the package to be deleted from server.
        :param package_veresion: version number of the package to be deleted from server.
        :param address: server address.
        """
        ret = NO_ERROR
        ret = NugetUtility.nuget_cli('delete', package_id, package_veresion, '-Source', address)
        return ret
