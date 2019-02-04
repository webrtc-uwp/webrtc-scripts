import os
import shutil
import itertools
import json
import time
from xml.etree import ElementTree as ET

from errors import NO_ERROR, ERROR_NUGET_CREATION_MISSING_FILE, ERROR_GET_NUGET_PACKAGE_VERSIONS_FAILED,\
ERROR_PACKAGE_VERSION_NOT_SUPPORTED, ERROR_CREATE_NUGET_FILE_FAILED,\
ERROR_CHANGE_NUSPEC_FAILED
import config
from logger import Logger,ColoredFormatter
from settings import Settings
from helper import convertToPlatformPath, module_exists, yes_no
from utility import Utility
from summary import Summary
from nugetUtility import NugetUtility
from releaseNotes import ReleaseNotes


class CreateNuget:
    """
    Creates .nuspec and .targets files that are needed for creating NuGet package
    for more info check out:
    https://docs.microsoft.com/en-us/nuget/guides/create-uwp-packages#create-and-update-the-nuspec-file

    Add, update, delete file elements in .nuspec based on configuration
    After making .nuspec and .targets run command -nuget pack WebRtc.nuspec
    using nuget_cli method, if you do not have nuget.exe download_nuget method
    will be run, which will download the latest nuget.exe file available
    """
    @classmethod
    def init(cls):
        """
        Initiates logger object.
        """
        cls.logger = Logger.getLogger('CreateNuget')

    @classmethod
    def run(cls, target, platform, cpus, configurations, targetFolder, versionInfo):
        """
        Method used to call all other methods in order necessary to create NuGet package
        First creates .nuspec, then .targets then adds files to .nuspec
        based on parameters
        :param target: webrtc or ortc
        :param platform: win or winuwp
        :param cpus: list of target cpus.
        :param configurations: Debug/Release.
        :param targetFolder: base folder where all files will be placed including created package
        :param versionInfo: Dictionary with the basic information about NuGet version number
        :return: NO_ERROR if successfull. Otherwise returns error code
        """
        start_time = time.time()
        
        cls.nugetFolderPath = targetFolder
        cls.nuspec_file = cls.nugetFolderPath + '/[TARGET].nuspec'
        cls.changelog_file = cls.nugetFolderPath + '/[TARGET].[VERSION]-changelog.txt'
        cls.targets_file = cls.nugetFolderPath + '/[TARGET].targets'
        cls.versions_file = cls.nugetFolderPath + '/versions.json'
        cls.destinationLibPath = cls.nugetFolderPath + config.NUGET_LIBRARIES
        ret = NO_ERROR
        release_note = ''
        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)
        if Settings.manualNugetVersionNumber is '':
            ret = cls.get_versions(target)
            if ret == NO_ERROR:
                ret = cls.create_versions_storage(cls.versions, target)
            if ret == NO_ERROR:
                ret = cls.get_latest_version(versionInfo['number'], target, versionInfo['prerelease'])
        else:
            cls.version = Settings.manualNugetVersionNumber
        if ret == NO_ERROR:
            if os.path.isfile(Settings.releaseNotePath):
                release_note = ReleaseNotes.get_note(Settings.releaseNotePath)
            ret = cls.create_nuspec(cls.version, target, release_note)
        if ret == NO_ERROR:
            ret = cls.create_targets(target)
        if ret == NO_ERROR:
            for cpu, configuration in itertools.product(cpus, configurations):                
                # check and copy all lib files to the specified folder 
                ret = cls.copy_files(target, platform, configuration, cpu)
                
                # go to specified nuget folder
                Utility.pushd(cls.nugetFolderPath)
                if ret == NO_ERROR:
                    # add .dll and .pri files to .nuspec file
                    ret = cls.add_nuspec_files(target, platform, configuration, cpu)
                if ret == NO_ERROR:
                    # update .winmd and .xml tags in nuspec file with the copied files
                    ret = cls.update_nuspec_files(target, platform, configuration, cpu,f_type=['.winmd', '.xml'], target_path=r'lib\uap10.0')
                # return to the root sdk directory
                Utility.popd()
        if ret == NO_ERROR:
            ret = NugetUtility.nuget_cli('pack', cls.nugetFolderPath + '/webrtc.nuspec')
        if ret == NO_ERROR:
            ret = cls.check_and_move(target, cls.version)            
        if ret == NO_ERROR:
            cls.logger.info('NuGet package created succesfuly: ' + cls.nugetFolderPath + '/' + cls.version)
            #Add nuget folder as nuget source in Nuget.Config
            NugetUtility.add_nuget_local_source()
            cls.delete_used()
        end_time = time.time()
        cls.executionTime = end_time - start_time

        # return to the base directory
        Utility.popd()
        
        return ret

    @classmethod
    def get_versions(cls, target):
        """
        Get NuGet package versions from nuget.org
        :param target: webrtc and/or ortc
        :return versions: List of NuGet package versions
        """
        ret = NO_ERROR
        # Works only if number of published versions of the nuget packet is less than 500
        search = 'https://api-v2v3search-0.nuget.org/search/query?q=packageid:' + target + '&ignoreFilter=true&prerelease=true&take=500'

        cls.logger.info('Collecting ' + target + ' NuGet package versions from nuget.org...')
        try:
            # Python 3:
            if module_exists('urllib.request'):
                import urllib.request
                with urllib.request.urlopen(search) as url:
                    data = json.loads(url.read().decode())
            # Python 2:
            if module_exists('urllib.request') is False:
                import urllib
                response = urllib.urlopen(search)
                data = json.loads(response.read())
            data_array = data['data']

            versions = []
            for item in data_array:
                for key, val in item.items():
                    if key == 'Version':
                        versions.append(val)
            versions = set(versions)
            versions = sorted(versions)
            if versions:
                cls.versions = versions
            else:
                ret = ERROR_GET_NUGET_PACKAGE_VERSIONS_FAILED
                cls.logger.error("Failed to collect NuGet package version numbers for target: " + target)
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to collect NuGet package version numbers for target: " + target)
            ret = ERROR_GET_NUGET_PACKAGE_VERSIONS_FAILED
        return ret

    @classmethod
    def create_versions_storage(cls, versions, target):
        """
        Creates a file with the NuGet package versions
        :param versions: list of NuGet package versions
        :param target: webrtc and/or ortc
        """
        ret = NO_ERROR
        try:
            if not os.path.exists(cls.nugetFolderPath):
                os.makedirs(cls.nugetFolderPath)
            formated_versions = {}
            version_numbers = set()
            storrage = {}
            if not versions:
                return ERROR_GET_NUGET_PACKAGE_VERSIONS_FAILED
            # Get package version numbers
            for version in versions:
                v_split = version.split('.')
                version_number = int(v_split[1])
                if version_number>40:
                    version_numbers.add(version_number)
            version_numbers = sorted(version_numbers, reverse=True)
            # Set up dictionary format for every version
            for v in version_numbers:
                formated_versions[v] = {}
            # Get latest major number for every version of the package
            for version in versions:
                v_split = version.split('.')
                major_number = False
                for v in version_numbers:
                    # Find major number only if the version number matches
                    if v is int(v_split[1]):
                        major_number = int(v_split[0])
                        if "major_number" in formated_versions[v]:
                            major_number = max(major_number, formated_versions[v]["major_number"])
                        formated_versions[v]["major_number"] = major_number
            # Get latest change number if exists for all version numbers
            for version in versions:
                v_split = version.split('.')
                for v in version_numbers:
                    # Find change number only if the major number and version number match
                    if v is int(v_split[1]) and formated_versions[v]["major_number"] is int(v_split[0]):
                        change_number = False
                        if len(v_split) > 3:
                            change_number = int(v_split[2])
                        if change_number is not False:
                            if "change_number" in formated_versions[v]:
                                change_number = max(change_number, formated_versions[v]["change_number"])
                            formated_versions[v]["change_number"] = change_number
            # Get latest build number for all version numbers while checking if it has chang number or not
            for version in versions:
                v_split = version.split('.')
                is_prerelease = False
                if '-' in v_split[-1]:
                    is_prerelease = v_split[-1].split('-')
                    v_split[-1] = is_prerelease[0]
                for v in version_numbers:
                    # Find build number only if the major number and version number match
                    if v is int(v_split[1]) and formated_versions[v]["major_number"] is int(v_split[0]):
                        if "change_number" in formated_versions[v]:
                            if len(v_split) > 3 and int(v_split[2]) is formated_versions[v]["change_number"]:
                                if is_prerelease is not False:
                                    build_number = int(is_prerelease[0])
                                else:
                                    build_number = int(v_split[3])
                                if "build_number" in formated_versions[v]:
                                    build_number = max(build_number, formated_versions[v]["build_number"])
                                formated_versions[v]["build_number"] = build_number
                        else:
                            if is_prerelease is not False:
                                build_number = int(is_prerelease[0])
                            else:
                                build_number = int(v_split[2])
                            if "build_number" in formated_versions[v]:
                                build_number = max(build_number, formated_versions[v]["build_number"])
                            formated_versions[v]["build_number"] = build_number
            # Check if the latest package version is prerelease or not
            for version in versions:
                v_split = version.split('.')
                is_prerelease = False
                if '-' in v_split[-1]:
                    is_prerelease = v_split[-1].split('-')
                    v_split[-1] = is_prerelease[0]
                for v in formated_versions.keys():
                    # Check if version number matches, and if latest major number for that version matches
                    if v is int(v_split[1]) and formated_versions[v]["major_number"] is int(v_split[0]):
                        # Check if the latest version has a change number
                        if "change_number" in formated_versions[v]:
                            if len(v_split) > 3:
                                if int(v_split[3]) is formated_versions[v]["build_number"] and int(v_split[2]) is formated_versions[v]["change_number"]:
                                    if is_prerelease is not False:
                                        formated_versions[v]["prerelease"] = is_prerelease[1]
                                    elif "prerelease" in formated_versions[v]:
                                        del formated_versions[v]["prerelease"]
                        else:
                            if len(v_split) is 3:
                                if int(v_split[2]) is formated_versions[v]["build_number"]:
                                    if is_prerelease is not False:
                                        formated_versions[v]["prerelease"] = is_prerelease[1]
                                    elif "prerelease" in formated_versions[v]:
                                        del formated_versions[v]["prerelease"]
            storrage[target] = formated_versions

            with open(cls.versions_file, 'w') as f:
                json.dump(storrage, f, indent=4)
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed file to store NuGet package version numbers for target: " + target)
            ret = ERROR_GET_NUGET_PACKAGE_VERSIONS_FAILED
        return ret

    @classmethod
    def get_latest_version(cls, version, target, prerelease="Default"):
        """
        Determines the full version number for the selected NuGet package version
        :param version: Version of the package that is to be built
        :param prerelease: By default selects version number will have the same prerelease value as the previous one
            If the version is not prerelease, the value of prerelease parameter should be False
            If the prerelease type is different put that type in the prerelease parameter instead
        """
        ret = NO_ERROR
        with open(cls.versions_file, 'r') as f:
            all_versions = json.load(f)
        if version in all_versions[target]:
            this_version = all_versions[target][version]
            build_no = int(this_version["build_number"])
            build_no = build_no + 1
            format_version = str(this_version["major_number"]) + '.' + str(version) + '.'
            if "change_number" in this_version:
                format_version += str(this_version["change_number"]) + '.'
            format_version += str(build_no)
            if "prerelease" in this_version and prerelease is "Default":
                format_version += '-' + str(this_version["prerelease"])
            if prerelease is 'false' or prerelease is 'False':
                prerelease = False
            if prerelease is not "Default" and prerelease is not False:
                format_version += '-' + prerelease
            cls.version = format_version
        else:
            cls.logger.error(str(ERROR_PACKAGE_VERSION_NOT_SUPPORTED))
            cls.logger.error("Failed retreve latest version of NuGet package for target: " + target)
            ret = ERROR_PACKAGE_VERSION_NOT_SUPPORTED
        return ret

    @classmethod
    def copy_files(cls, target, platform, configuration, cpu, f_type=['.dll', '.pri', '.winmd', '.xml']):
        """
        Copy lib files that will be used for building nuget package to the destination folder
        :param target: webrtc or ortc
        :param platform: win or winuwp
        :param configuration: Release or Debug.
        :param cpu: target cpu.
        :param f_type: array of file types to be updated (Default ['.dll', '.pri']).
        """
        ret = NO_ERROR
        try:
            # Create libraries directory if needed
            if not os.path.exists(cls.nugetFolderPath + '/libraries'):
                os.makedirs(cls.nugetFolderPath + '/libraries')
            
            for ft in f_type:
                f_name = 'Org.' + target + ft
                src_path = convertToPlatformPath(
                    config.NATIVE_LIB_SRC
                    .replace('[TARGET]', target)
                    .replace('[PLATFORM]', platform)
                    .replace('[CONFIGURATION]', configuration)
                    .replace('[CPU]', cpu)
                    .replace('[FILE]', f_name)
                )
                dst_path = convertToPlatformPath(
                    cls.destinationLibPath
                    .replace('[TARGET]', target)
                    .replace('[PLATFORM]', platform)
                    .replace('[CONFIGURATION]', configuration)
                    .replace('[CPU]', cpu)
                )
                # Create directory for the specified configuration if needed
                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)
                # Check if file exists and copy it to the specified directory
                if os.path.exists(src_path):
                    shutil.copy(src_path, dst_path)
                    cls.logger.debug('FIle copied: ' + dst_path + f_name)
                else:
                    cls.logger.warning('File does NOT exist! ' + src_path)
                    return ERROR_NUGET_CREATION_MISSING_FILE
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to copy files for: " + target + "; platform: " + platform + "; configuration: " + configuration + "; cpu: " + cpu)
            ret = ERROR_NUGET_CREATION_MISSING_FILE

        return ret

    @classmethod
    def update_nuspec_files(cls, target, platform, configuration, cpu, f_type=['.dll', '.pri'], f_name='Org.WebRtc', target_path=False):
        """
        Updates existing file elements contained in .nuspec file
        :param target: webrtc or ortc
        :param platform: win or winuwp
        :param configuration: Release or Debug.
        :param cpu: target cpu.
        :param f_type: array of file types to be updated (Default ['.dll', '.pri']).
        :param f_name: name of the lib file that needs to be added(Default: Org.WebRtc)
        :param target_path: path for the target attribute of the file element that
            needs to be provided for all non default file types (.dll, .pri).
        """
        ret = NO_ERROR
        try:
            """
            in order for update to work nuspec must not have   xmlns="..."
            inside the package tag, otherwise files tag will not be found
            """
            nuspecName = target + '.nuspec'
            with open(nuspecName, 'rb') as nuspec:
                tree = ET.parse(nuspec)
            files = tree.find('files')
            # Element is <file> element, ft is each file type
            for element, ft in itertools.product(files, f_type):
                src_attrib = element.attrib.get('src')
                # Check if <file> element has a src with given cpu, configuration and file type
                if all(val in src_attrib for val in [cpu, configuration.capitalize(), ft]):
                    file_name = f_name + ft
                    # New src path to the lib file with required cpu, configuration and file type
                    src_path = convertToPlatformPath(
                        config.NUGET_LIBRARIES
                        .replace('[TARGET]', target)
                        .replace('[PLATFORM]', platform)
                        .replace('[CONFIGURATION]', configuration)
                        .replace('[CPU]', cpu)
                    )
                    src_path += file_name
                    # New target attribute of the <file> element
                    # (place where lib file will be placed inside NuGet package)
                    if target_path is False:
                        target_path = convertToPlatformPath(config.NATIVE_LIB_TARGET.replace('[CPU]', cpu))
                    # Check if the file from the new src exists
                    if os.path.exists(src_path):
                        element.set('src', src_path)
                        element.set('target', target_path)
                        # Save changes to the .nuspec file
                        tree.write(nuspecName)
                        cls.logger.debug("File updated: " + src_path)
                    else:
                        raise Exception('File does NOT exist: ' + src_path)
        except Exception as error:
            cls.logger.error(str(error))
            ret = ERROR_CHANGE_NUSPEC_FAILED
            cls.logger.error("Failed to update file element in .nuspec file for target: " + target + "; platform: " + platform + "; configuration: " + configuration + "; cpu: " + cpu)
        return ret

    @classmethod
    def delete_nuspec_files(cls, target, platform, configuration, cpu, f_type=['.dll', '.pri']):
        """
        Delete file element in .nuspec based on src attribute
        :param target: webrtc or ortc
        :param platform: win or winuwp
        :param configuration: Release or Debug.
        :param cpu: target cpu.
        :param f_type: array of file types to be updated (Default ['.dll', '.pri']).
        """
        try:
            """
            in order for update to work nuspec must not have   xmlns="..."
            inside the package tag, otherwise files tag will not be found
            """
            nuspecName = target + '.nuspec'
            with open(nuspecName, 'rb') as nuspec:
                tree = ET.parse(nuspec)
            files = tree.find('files')
            # Element is <file> element, ft is each file type
            for element, ft in itertools.product(files, f_type):
                src_attrib = element.attrib.get('src')
                # Check if <file> element has a src with given cpu, configuration
                # and file type, then remove it from .nuspec
                if all(val in src_attrib for val in [target, platform, cpu, configuration, ft]):
                    files.remove(element)
                    cls.logger.debug("File Deleted: " + src_attrib)
            # Save changes to the .nuspec file
            tree.write(nuspecName)
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to delete file elements inside .nuspec file")

    @classmethod
    def add_nuspec_files(cls, target, platform, configuration, cpu, f_type=['.dll', '.pri'], f_name='Org.WebRtc', target_path=False):
        """
        Add file elements to .nuspec file based on config
        Every cpu type that you want to add to NuGet package must be built in
        eather Release or Debug configuration

        :param target: webrtc or ortc
        :param platform: win or winuwp
        :param configuration: Release or Debug.
        :param cpu: target cpu.
        :param f_type: array of file types to be updated (Default ['.dll', '.pri']).
        :param f_name: name of the lib file that needs to be added(Default: Org.WebRtc)
        :param target_path: path for the target attribute of the file element that
            needs to be provided for all non default file types (.dll, .pri).
        """
        ret = NO_ERROR
        try:
            """
            in order for update to work nuspec must not have   xmlns="..."
            inside the package tag, otherwise files tag will not be found
            """
            nuspecName = target + '.nuspec'
            with open(nuspecName, 'rb') as nuspec:
                tree = ET.parse(nuspec)
            files = tree.find('files')
            for ft in f_type:
                # Add extention to the file name
                file_name = f_name + ft
                # Src path to the lib file with required cpu, configuration and file type
                src_path = convertToPlatformPath(
                    config.NUGET_LIBRARIES
                    .replace('[TARGET]', target)
                    .replace('[PLATFORM]', platform)
                    .replace('[CONFIGURATION]', configuration)
                    .replace('[CPU]', cpu)
                )
                src_path += file_name
                # Target attribute of the <file> element (place where lib file will be placed inside NuGet package)
                if target_path is False:
                    target_path = convertToPlatformPath(config.NATIVE_LIB_TARGET.replace('[CPU]', cpu))
                # Check if the file from the new src exists
                if os.path.exists(src_path):
                    file_attrib = {'src': src_path, 'target': target_path}
                    # Make a new file element with the attributes from above
                    new_file = ET.SubElement(files, 'file', attrib=file_attrib)
                    new_file.tail = "\n\t\t"
                    cls.logger.debug("File added: " + file_attrib['src'])
                else:
                    raise Exception('File does NOT exist! \n' + src_path)
            # Save changes to the .nuspec file
            tree.write(nuspecName)
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to add file element to .nuspec file for target: " + target + "; platform: " + platform + "; configuration: " + configuration + "; cpu: " + cpu)
            ret = ERROR_CHANGE_NUSPEC_FAILED
        return ret

    @classmethod
    def add_targets_itemgroup(
        cls, target, items_condition, sub_include, sub_elem='Reference',
        sub_sub_elem=False
    ):
        """
        Method used to change .targets file when making ORTC NuGet package
        delete_targets_itemgroups method must be run before adding itemgroups

        :param items_condition: Condition attribute for the ItemGroup element.
        :param sub_elem: sub element for the ItemGroup element(Default:'Reference').
        :param sub_include: Include attribute for the sub element
        :param sub_sub_elem: elements that are second level sub elements to
            ItemGroup element in a form of a dictionary (Optional)
            dictionary key is the element tag and value is element text
        """
        try:
            """
            in order for update to work targets must not have   xmlns="..."
            inside the Project tag, otherwise tag will not be found
            """
            with open(cls.targets_file.replace('[TARGET]', target), 'rb') as targets:
                tree = ET.parse(targets)
            project = tree.getroot()
            # Add new ItemGroup element to .targets file
            new_itemgroup = ET.Element('ItemGroup')
            # Set Contition attribute to the ItemGroup element
            new_itemgroup.set('Condition', items_condition)
            new_itemgroup.text = '\n\t'
            # Element inside ItemGroup element
            element = ET.Element(sub_elem)
            # Set Include attribute to that element
            sub_include = '$(MSBuildThisFileDirectory)' + sub_include
            element.set('Include', sub_include)
            # Check if that element needs sub element
            if sub_sub_elem is not False:
                element.text = '\n\t'
                # For each element in provided dictionary
                for key, val in sub_sub_elem.items():
                    # Set sub elements attribute(dictionary key)
                    sub_sub = ET.Element(key)
                    # Set sub elements text(dictionary value)
                    sub_sub.text = val
                    sub_sub.tail = '\n\t'
                    # Add sub element to its parrent element
                    element.append(sub_sub)
            element.tail = '\n\t'
            # Add the element to the ItemGroup element
            new_itemgroup.append(element)
            new_itemgroup.tail = '\n\t'
            project.append(new_itemgroup)
            # Save changes to the .targets file
            tree.write(cls.targets_file.replace('[TARGET]', target))
        except Exception as error:
            cls.logger.error(str(error))

    @classmethod
    def delete_targets_itemgroups(cls, target):
        """
        Delete all ItemGroup elements from .targets file
        :param target: webrtc or ortc
        """
        try:
            with open(cls.targets_file.replace('[TARGET]', target), 'rb') as targets:
                tree = ET.parse(targets)
            project = tree.getroot()
            for element in project:
                if 'ItemGroup' in element.tag:
                    project.remove(element)
            tree.write(cls.targets_file.replace('[TARGET]', target))
        except Exception as error:
            cls.logger.error(str(error))

    @classmethod
    def create_nuspec(cls, version, target, release_note = False):
        """
        Create .nuspec file based on a template with default values
        :param version: version of the nuget package must be specified when
            copying nuspec file
        :param target: webrtc or ortc
        """
        ret = NO_ERROR
        try:
            if not os.path.exists(cls.nugetFolderPath):
                os.makedirs(cls.nugetFolderPath)
            # .nuspec file that is used to build the NuGet package
            with open(cls.nuspec_file.replace('[TARGET]', target), 'w') as destination:
                # Template .nuspec file
                with open(config.NUGET_TEMPLATES_FOLDER + target + '.nuspec', 'r') as source:
                    for line in source:
                        if '<version>' in line:
                            destination.write('\t\t<version>' + version + '</version>\n')
                            if release_note:
                                cls.logger.debug('Release note added: ' + release_note)
                                # Template .nuspec file
                                with open(cls.changelog_file.replace('[TARGET]', target).replace('[VERSION]', version), 'w') as changelog:
                                    changelog.write(release_note)
                                destination.write('\t\t<releaseNotes>' + release_note + '</releaseNotes>\n')
                        else:
                            destination.write(line)
            cls.logger.debug('Nuspec file created successfuly!')
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to create .nuspec file!")
            ret = ERROR_CREATE_NUGET_FILE_FAILED
        return ret

    @classmethod
    def create_targets(cls, target):
        """
        Create .targets file based on a template with default values
        :param target: webrtc or ortc
        """
        ret = NO_ERROR
        try:
            if not os.path.exists(cls.nugetFolderPath):
                os.makedirs(cls.nugetFolderPath)
            # .targets file that is used to build the NuGet package
            with open(cls.targets_file.replace('[TARGET]', target), 'w') as destination:
                # Template .targets file
                with open(config.NUGET_TEMPLATES_FOLDER + target + '.targets', 'r') as source:
                    for line in source:
                        destination.write(line)
            cls.logger.debug('Targets file created successfuly!')
        except Exception as error:
            cls.logger.error(str(error))
            cls.logger.error("Failed to create .targets file!")
            ret = ERROR_CREATE_NUGET_FILE_FAILED
        return ret

    @classmethod
    def check_and_move(cls, target, version):
        """
        Checks if nuget package was made successfully and moves it to nuget folder
        :param target: webrtc or ortc
        :param version: Version of the created NuGet file
        """
        ret = NO_ERROR
        try:
            package = target + '.' + version + '.nupkg'
            if os.path.isfile(package):
                shutil.move(package, cls.nugetFolderPath + '/' + package)
            else:
                ret = ERROR_CREATE_NUGET_FILE_FAILED
                cls.logger.error('NuGet package does not exist')
        except Exception as error:
            cls.logger.error(str(error))
            ret = ERROR_CREATE_NUGET_FILE_FAILED
        return ret


    @classmethod
    def delete_used(cls):
        content = os.listdir(cls.nugetFolderPath)
        try:
            for element in content:
                if 'libraries' in element:
                    libraries = convertToPlatformPath(cls.nugetFolderPath + '/' + element)
                    shutil.rmtree(libraries)
                if '.nuspec' in element:
                    nuspec = convertToPlatformPath(cls.nugetFolderPath + '/' + element)
                    os.remove(nuspec)
                if '.targets' in element:
                    targets = convertToPlatformPath(cls.nugetFolderPath + '/' + element)
                    os.remove(targets)
        except Exception as error:
            cls.logger.warning("Failed to delete unnecessary files from nuget folder.")
