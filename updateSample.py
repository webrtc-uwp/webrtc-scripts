import os
import filecmp
import shutil
from xml.etree import ElementTree as ET

from logger import Logger
from helper import convertToPlatformPath
from errors import NO_ERROR, ERROR_UPDATE_SAMPLE_COPY_FAILED, ERROR_UPDATE_SAMPLE_CLONE_FAILED, ERROR_UPDATE_SAMPLE_USE_NUGET_FAILED
from settings import Settings
from utility import Utility
from nugetUtility import NugetUtility
from createNuget import CreateNuget
import config

class UpdateSample:

    @classmethod
    def init(cls):
        cls.logger = Logger.getLogger('UpdateSample')
    
    @classmethod
    def run(cls):
        ret = NO_ERROR

        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)

        samples_directory = './Published_Samples/'
        if Settings.updateSampleInfo['package'] is not 'default':
            latestNugetVersion = Settings.updateSampleInfo['package']
        #Get nuget package version if updatesample is run alongside the createnuget action
        elif hasattr(CreateNuget, 'version'):
            latestNugetVersion = CreateNuget.version
        #Get nuget package version if updatesample is run separatly from the createnuget action
        else:
            latestNugetVersion = NugetUtility.get_latest_package()
        #Add nuget folder to nuget source in Nuget.Config
        NugetUtility.add_nuget_local_source()

        #Get sample name and repo url from userdef file
        for sample in Settings.updateSampleInfo['samples']:
            repo_name = sample['name']
            repo_url = sample['url']
            repo_branch = sample['branch']
            #Path of the sample folder to wich to clone to
            cloned_sample_path = convertToPlatformPath(samples_directory + repo_name)
            #Path to the sample folder inside commons directory
            common_sample_path = convertToPlatformPath(config.SAMPLES_FOLDER_PATH + repo_name + '/Client')

            ret = cls.clone_sample(repo_url, repo_branch, cloned_sample_path)
            if ret == NO_ERROR:
                ret = cls.copy_dirs(common_sample_path, cloned_sample_path)
            if ret == NO_ERROR:
                #Make the sample use nuget package by changing .csproj file
                ret = cls.use_nuget_package(cloned_sample_path, latestNugetVersion)

        # return to the base directory
        Utility.popd()
        
        return ret

    @classmethod
    def clone_sample(cls, git_url, git_branch, sample_dir_name):
        """
        Clones the sample from the repository to a dir
        """
        ret = NO_ERROR
        try:
            if not os.path.isdir(sample_dir_name):
                os.makedirs(sample_dir_name)
                cls.logger.debug("Cloning sample...")
                cloneCommand = 'git clone -b ' + git_branch + ' ' + git_url + ' ' + sample_dir_name
                cloneCommand = cloneCommand.strip()
                ret = Utility.runSubprocess([cloneCommand])
                if ret == NO_ERROR:
                    cls.logger.debug("Cloning sample finished.")
            else:
                cls.logger.debug("Sample already Exists.")
        except Exception as error:
            cls.logger.error(str(error))
            ret = ERROR_UPDATE_SAMPLE_CLONE_FAILED
        return ret
    
    @classmethod
    def copy_dirs(cls, source, destination):
        """
        Compare two directories recursively and copy files from the source to destination path if they are different. 
        Files and directories contained only in destination path are removed

        :param source: Source directory path
        :param destination: Destination directory path

        :return ret: NO_ERROR if copy was successfull. Otherwise returns error code
        """
        ret = NO_ERROR

        diff_src_files = []

        dirs_cmp = filecmp.dircmp(source, destination, ignore=['.git', '.gitattributes', '.gitignore'])

        # Get all files and directories contained only in the source directory
        if dirs_cmp.left_only:
            for element in dirs_cmp.left_only:
                diff_src_files.append(element)

        # Get all files that have different contents
        if dirs_cmp.diff_files:
            for element in dirs_cmp.diff_files:
                diff_src_files.append(element)

        # Get all files which could not be compared
        if dirs_cmp.funny_files:
            for element in dirs_cmp.funny_files:
                diff_src_files.append(element)

        # Get all directories that are same for both source and destination paths
        if dirs_cmp.common_dirs:
            for element in dirs_cmp.common_dirs:
                diff_src_files.append(element)
        
        # Get all files and directories contained only in the destination directory
        if dirs_cmp.right_only:
            for element in dirs_cmp.right_only:
                dlete_path = convertToPlatformPath(destination + '/' + element)
                if os.path.isdir(dlete_path):
                    shutil.rmtree(dlete_path)
                elif os.path.isfile(dlete_path):
                    os.remove(dlete_path)
            cls.logger.debug("Content Removed: {}".format(dirs_cmp.right_only))

        try:
            if diff_src_files:
                #Go trough every file that should be copied from source to destination
                for element in diff_src_files:
                    src_path = convertToPlatformPath(source + '/' + element)
                    dst_path = convertToPlatformPath(destination + '/' + element)
                    #Copy file from source to destionation(replace if already exists)
                    if os.path.isfile(src_path):
                        cls.logger.debug("Copying file: {}".format(src_path))
                        shutil.copy(src_path, dst_path)
                    elif os.path.isdir(src_path):
                        #Create directory if it does not exist already
                        cls.logger.debug("Creating subdirectory: {}".format(dst_path))
                        if not os.path.isdir(dst_path):
                            os.makedirs(dst_path)
                        # Run copy_dirs for the subdirectory
                        cls.copy_dirs(src_path, dst_path)
        except Exception as error:
            cls.logger.error(str(ERROR_UPDATE_SAMPLE_COPY_FAILED))
            ret = ERROR_UPDATE_SAMPLE_COPY_FAILED

        return ret

    @classmethod
    def get_file_name(cls, dir_path):
        """
        :return file_: name of the .csproj file whose name contains WebRtc
        """
        files = os.listdir(dir_path)
        for file_ in files:
            if 'WebRtc' in file_ and file_.endswith('.csproj'):
                return file_


    @classmethod
    def use_nuget_package(cls, sample_dir_path, nuget_version):
        """
        Make the sample use nuget package, if it already is update the version
        :param sample_dir_path: Name of the sample to be changet to nuget package
        :param nuget_version: Version of the nuget to be used
        :return ret: NO_ERROR if copy was successfull. Otherwise returns error code
        """
        ret = NO_ERROR

        fileName = cls.get_file_name(sample_dir_path)
        filePath = convertToPlatformPath(sample_dir_path + '/' + fileName)

        xmlns = {'xmlns':'http://schemas.microsoft.com/developer/msbuild/2003'}
        try:
            ET.register_namespace('', "http://schemas.microsoft.com/developer/msbuild/2003")
            with open(filePath, 'r') as csproj:
                tree = ET.parse(csproj)
            #Find all ItemGroup elements inside .csproj file
            itemGroups = tree.findall('xmlns:ItemGroup', xmlns)
            for element in itemGroups:
                #Check if the ItemGroup element contains ProjectReference element 
                projectReference =  element.find('xmlns:ProjectReference', xmlns)
                if projectReference is not None:
                    #Remove ProjectReference element from ItemGroup
                    element.remove(projectReference)
                    cls.logger.debug('ProjectReference element removed from .csproj file')

                #Check if the ItemGroup element contains PackageReference element 
                packageReferences = element.findall('xmlns:PackageReference', xmlns)
                if packageReferences:
                    for reference in packageReferences:
                        #Check if the PackageReference element has Include attribute with value WebRtc
                        if 'webrtc' in reference.get('Include').lower():
                            version = reference.find('xmlns:Version', xmlns)
                            if version is not None:
                                #Update nuget version for the PackageReference element
                                version.text = nuget_version
                                
                                cls.logger.debug('Nuget reference in .csproj file updated successfuly.')
                                tree.write(filePath)

                                return ret
            
            #If the nuget version has not been set already add a new ItemGroup element with nuget package reference
            #Get the Project element from the .csproj file
            project = tree.getroot()

            #Add a new ItemGroup element to the Project element
            newItemGroup = ET.SubElement(project, 'ItemGroup')
            #Add a PackageReference element to the new ItemGroup element with the attribute that includes WebRtc
            newPackageReference = ET.SubElement(newItemGroup, 'PackageReference', attrib={'Include': 'WebRtc'})
            #Add a version element to the new PackageReference element
            newVersion = ET.SubElement(newPackageReference, 'Version')
            #Add a version number of the package to be used to the new Version element
            newVersion.text = nuget_version
            newItemGroup.tail = "\n"
            cls.logger.debug('Nuget reference added to .csproj file')
            #Write the changes to the .csproj file
            tree.write(filePath)
        except Exception as error:
            ret = ERROR_UPDATE_SAMPLE_USE_NUGET_FAILED
            cls.logger.error(str(error))

        return ret
