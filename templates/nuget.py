# This file is generated from defaults.py. Be free to change any variable listed below.

#args.gn template path
webRTCGnArgsTemplatePath='./webrtc/windows/templates/gns/args.gn'

#Path where nuget package and all of the files used to create the package are stored
nugetFolderPath = './nugetpackages'
nugetVersionInfo = {
                      #Main version number of the NuGet package 
                      'number': '71',
                      #Use '' if not prerelease, 'Default' is based on previous version, or use some other prerelease ('Alpha', 'Beta', ...)
                      'prerelease': 'Default',
                      #Initial version number format
                      'format': '1.[number].0.1[prerelease]'
                   }
#Imput NuGet package version number manualy, used if selected version number does not exist on nuget.org, E.g., '1.66.0.3-Alpha'
manualNugetVersionNumber = ''

#Path to a release notes file
releaseNotePath = 'releases.txt'

#Keywords for selecting commits that should be placed inside release notes (use ['*'] in order to use all commits)
#(commits that have at least one of keywords will be placed inside release notes)
commitKeywords = ['notes', 'merge']

#Place where zipped backup(pdb) files will be uploaded inside onedrive folder for the uploadbackup action
onedrivePath = 'Public Symbols/WebRTC'

#Information about the sample to be updated
updateSampleInfo = {
                      'package' : 'default',
                      'samples' : [
                        {
                          'name' : 'PeerCC',
                          'url' : 'https://github.com/webrtc-uwp/PeerCC-Sample',
                          'branch': 'webrtc_merge_m66'
                        }
                      ]
                   }

#List of NuGet packages used to manualy publish nuget packages, E.g., 'webrtc.1.66.0.3-Alpha.nupkg'
#Packages must be placed in a folder referenced in nugetFolderPath variable
nugetPackagesToPublish = []

#API key used to publish nuget packages nuget.org
nugetAPIKey = ''

#URL for the nuget server, if 'default' nuget.org is used
nugetServerURL = 'default'

#Output path where will be stored nuget package as well as libs and pdbs
#releaseOutputPath = '.'

#Supported platforms for specific host OS 
supportedPlatformsForHostOs = { 
                                'windows' : ['win', 'winuwp'],
                                'darwin' : ['ios', 'mac'],
                                'linux' : ['android', 'linux']
                              }

#Supported cpus for specific platform
supportedCPUsForPlatform = { 
                              'winuwp'  : ['arm', 'x86', 'x64'],
                              'win'     : ['x86', 'x64'],
                              'ios'     : ['arm'],
                              'mac'     : [ 'x86', 'x64'],
                              'android' : ['arm'],
                              'linux'   : [ 'x86', 'x64'],
                            }

#List of targets for which will be performed specified actions. Supported target is webrtc. In future it will be added support for ortc.
targets = [ 'webrtc' ]
#List of target cpus. Supported cpus are arm, x86 and x64
targetCPUs = [ 'arm', 'x86', 'x64' ]
#List of target platforms. Supported cpus are win and winuwp
targetPlatforms = [ 'winuwp' ]
#List of target configurations. Supported cpus are Release and Debug
targetConfigurations = [ 'Release' ]
#TODO: Implement logic to update zslib_eventing_tool.gni based on list of specified programming languages.
targetProgrammingLanguage = [ 'cx', 'cppwinrt', 'c', 'dotnet', 'python' ]

#=========== Supported actions: clean, createuserdef, prepare, build, backup, createnuget, publishnuget, uploadbackup. 
# In future it will be added support  updatesample.
#'clean' : Based on cleanup options set in cleanupOptions dict, it can be choosen desired cleanup actions.
#'createuserdef' : Deletes existing userdef.py if exists and create a new from defaults.py.
#'prepare' : Prepares developement environemnt for selected targets for choosen cpus, platforms and configurations.
#'build' : Builds selected targets for choosen cpus, platforms and configurations.
#'backup': Backup latest build.
#'createnuget' : Creates nuget package.
#'publishnuget' : Publishes nuget package
#'uploadbackup' : Creates a zipp file with pdb files and nuget package based on configuration and uploads it to onedrive
#List of actions to perform
actions = [ 'prepare', 'build', 'backup', 'createnuget', 'publishnuget', 'updatesample' ]

#Flag if wrapper library should be built. If it is False, it will be built only native libraries
buildWrapper = True  

#=========== cleanupOptions
#'actions' : ['cleanOutput', 'cleanIdls', 'cleanUserDef','cleanPrepare'],
#'targets' :  If [], it will use values from targets variable above. 
#             If ['*'] it will delete output folders for all targets. 
#             If ['webrtc'] it will delete just webrtc target
#'cpus' :  If [], it will use values from targetCPUs variable above. 
#             If ['*'] it will delete output folders for all cpus. 
#             If ['x64'] it will delete just x64 output folder
#'platforms' :  If [], it will use values from targetPlatforms variable above. 
#             If ['*'] it will delete output folders for all platforms. 
#             If ['winuwp'] it will delete just winuwp output folder
#'configurations' :  If [], it will use values from targetConfigurations variable above. 
#             If ['*'] it will delete output folders for all configurations. 
#             If ['Release'] it will delete just Release output folder
cleanupOptions = {
                'actions' : ['cleanOutput','cleanIdls','cleanPrepare'],
                'targets' : [],
                'cpus' : [],
                'platforms' : [],
                'configurations' : []
              }
   
"""
Supported formats: %(funcName)s - function name, %(levelname)s - log level name, %(asctime)s - time, %(message)s - log message, %(filename)s - curremt python filename, %(lineno)d - log message line no, %(name)d - module name
For the rest of available attributes you can check on https://docs.python.org/3/library/logging.html#logrecord-attributes
"""
#logFormat = '[%(levelname)-17s] - %(asctime)s - %(message)s (%(filename)s:%(lineno)d)'
logFormat = '[%(levelname)-17s] - [%(name)-15s] - %(funcName)-30s - %(message)s (%(filename)s:%(lineno)d)'

#Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (case sensitive)
logLevel = 'DEBUG'

#If true logs to file with generic filename (platform-cpu-configuration-date), or to file with name entered in logFileName.
#If it is false, log will be shown in console. 
logToFile = False
#Log file name
logFileName = 'Log.txt'

#If true overwrite old log file, otherwise it will create a new log file with time suffix.
overwriteLogFile = False

#If set to False, log messages for different log levels will be shown colorized.
noColoredOutput = False

#If set to True script execution will be stopped on error.
stopExecutionOnError = False

#If set to True, shows trace log when script execution is stopped on error
showTraceOnError = True
#If set to True, shows all settings values when script execution is stopped on error
showSettingsValuesOnError = True
#If set to True, shows PATH variable when script execution is stopped on error
showPATHOnError = True

#Windows specific variables
#If VS is installed but it is not found,, it is required to set msvsPath variable
msvsPath = ''

#If set to True, output libraries and pdbs will be stored in Backup folder
enabledBackup = False
#Backup folder, in user working directory (folder from where script is run)
libsBackupPath = './Backup'
#Flag for overwriting current backup folder
overwriteBackup = False