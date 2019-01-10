import os
import zipfile
import time
import tempfile
import shutil
import glob
import sys
from datetime import datetime

from helper import convertToPlatformPath, module_exists, install
from errors import NO_ERROR, ERROR_UPLOAD_BACKUP_FAILED, ERROR_UPLOAD_BACKUP_FILES_MISSING
from settings import Settings
from createNuget import CreateNuget
from settings import Settings
from logger import Logger


class UploadBackup:
    
    @classmethod
    def init(cls):
        """
        Initiates logger object.
        """
        cls.logger = Logger.getLogger('UploadBackup')

    @classmethod
    def run(cls):
        """
        Zipps latest backup based on configuration, and uploads it to onedrive
        :return ret: NO_ERROR if upload was successfull. Otherwise returns error code
        """
        ret = NO_ERROR
        
        cls.zip_name = ''
        latest_backup = cls.get_backup_dir()

        backup_path = convertToPlatformPath(os.getcwd()+'/' + latest_backup)
        if os.path.isdir(backup_path):
            ret = cls.zipdir(backup_path)
        else:
            ret = ERROR_UPLOAD_BACKUP_FAILED

        if ret == NO_ERROR:
            cls.upload_to_onedrive()
        return ret

    @classmethod
    def zipdir(cls, path):
        """
        Zip pdb files and nuget package if available
        :param path: path to the backup file that needs to be zipped.
        :return ret: NO_ERROR if zipp was successfull. Otherwise returns error code
        """
        ret = NO_ERROR
        cls.zip_name = datetime.now().strftime('Backup_%Y-%m-%d_%H-%M-%S') + '.zip'
        zipf = zipfile.ZipFile(cls.zip_name, 'w', zipfile.ZIP_DEFLATED)
        count = 0
        #Get number of files to be zipped in order to display percentage
        for root, dirs, files in os.walk(path):
            for file in files:
                count += 1
        file_no = 0
        nugetPackage = False
        #Get nuget package that was just created
        if hasattr(CreateNuget, 'version'):
            #Path to a newly created nuget package
            new_package_path = convertToPlatformPath(Settings.nugetFolderPath + '/' + 'webrtc.' + CreateNuget.version + '.nupkg')
            if os.path.isfile(new_package_path):
                nugetPackage = new_package_path
            else:
                ret = ERROR_UPLOAD_BACKUP_FILES_MISSING
        #Get latest nuget package created, if uploadBackup is called without calling createNuget
        else:
            has_package = False
            for fname in os.listdir(Settings.nugetFolderPath):
                if fname.endswith('.nupkg'):
                    has_package = True
                    break
            if has_package is True:
                list_of_files = glob.iglob(Settings.nugetFolderPath + '/*.nupkg')
                nugetPackage = max(list_of_files, key=os.path.getctime)
        if nugetPackage is not False:
            zipf.write(nugetPackage, os.path.basename(nugetPackage))
        else:
            cls.logger.warning('Missing NuGet package!')
            
        print('Zipping pdb files:')
        toolbar_width = 60
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        #Used to check if progress bar should progress
        previous_percentage = -1
        for root, dirs, files in os.walk(path):
            for file in files:
                file_no += 1
                percent = int(toolbar_width * file_no/count)

                # Add to progress bar
                if percent != previous_percentage:
                    sys.stdout.write("-")
                    sys.stdout.flush()

                # Zip only folders based on configuration from the userdef.py file
                for name in cls.get_config_names():
                    if name in root:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
                
                previous_percentage = percent
        sys.stdout.write("]\n")
        cls.logger.debug('Files zipped to: ' + cls.zip_name)
        zipf.close()
        return ret

    @classmethod
    def get_backup_dir(cls):
        """
        Get the latest backup folder name
        :return latest_backup: Name of the latest backup folder
        """
        all_backups = [b_dir for b_dir in os.listdir('.') if os.path.isdir(b_dir) and 'Backup' in b_dir]

        if len(all_backups) > 1:
            all_backups.remove('Backup')
            latest_backup = max(datetime.strptime(date, 'Backup_%Y-%m-%d_%H-%M-%S') for date in all_backups)
            latest_backup = latest_backup.strftime('Backup_%Y-%m-%d_%H-%M-%S')
        elif len(all_backups) == 1:
            latest_backup = all_backups[0]
        return latest_backup

    @classmethod
    def get_config_names(cls):
        """
        Gets the folder names based on configuration from userdef.py file
        :return names: list of names based on configuration
        """
        names = []
        for target in Settings.targets:
            for platform in Settings.targetPlatforms:
                for cpu in Settings.targetCPUs:
                    for configuration in Settings.targetConfigurations:
                        name = target + '_' + platform + '_' + cpu + '_' + configuration
                        names.append(name)
        return names

    @classmethod
    def checkBackup(cls):
        """
        Checks the latest backup folder based on the configuration from userdef.py file
         and returns True/False in order to know if backup should be run or not
        :return: True if backup needs to be called
        :return: False if backup does not needs to be called
        """
        cls.logger.debug("Checking backup directory")
        latest_backup = cls.get_backup_dir()
        existing_backups = os.listdir('./'+latest_backup)
        unexisting_backups = []
        for name in cls.get_config_names():
            if name not in existing_backups:
                unexisting_backups.append(name)
        if not unexisting_backups:
            return False
        else:
            cls.logger.warning("Backup directory not up to date.")
            return True

    @classmethod
    def upload_to_onedrive(cls):
        """
        Upload file to onedrive
        :return ret: NO_ERROR if upload was successfull. Otherwise returns error code
        """
        ret = NO_ERROR

        # Install onedrivesdk package if not installed, and import it
        if module_exists('onedrivesdk'):
            import onedrivesdk
            from onedrivesdk.helpers import GetAuthCodeServer
        else:
            install('onedrivesdk')
            import onedrivesdk
            from onedrivesdk.helpers import GetAuthCodeServer

        #Redirect url for the authentication application
        redirect_uri = "http://localhost:8080/"
        client_id = Settings.onedrive_client_id
        client_secret = Settings.onedrive_client_secret

        client = onedrivesdk.get_default_client(client_id=client_id,
                                                scopes=['wl.signin',
                                                        'wl.offline_access',
                                                        'onedrive.readwrite'])
        auth_url = client.auth_provider.get_auth_url(redirect_uri)

        # Block thread until we have the code
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
        # Finally, authenticate!
        client.auth_provider.authenticate(code, redirect_uri, client_secret)
        item_id = "root"

        directory_id = ''
        # Get all items inside root folder
        items = client.item(id=item_id).children.get()
        
        # Name of the folder inside onedrive to be uploaded to
        dir_name_onedrive = 'WebRTC'
        for count, item in enumerate(items):
            if dir_name_onedrive in item.name and item.folder:
                # Id of the folder inside onedrive to be uploaded to
                directory_id = item.id

        # File to be uploaded
        file_name = cls.zip_name
        # Full path of the file to be uploaded
        file_path = r'./' + file_name
        print('Uploading file...')

        # uploads file
        client.item(id = directory_id).children[file_name].upload_async(file_path)

        # Get all items inside selected folder
        directory_items = client.item(id=directory_id).children.get()

        ret = ERROR_UPLOAD_BACKUP_FAILED
        for count, item in enumerate(directory_items):
            # Check if selected folder on onedrive has the uploaded file 
            if file_name in item.name:
                ret = NO_ERROR

        if ret == NO_ERROR:
            cls.logger.info('Upload Successful!')
        return ret
