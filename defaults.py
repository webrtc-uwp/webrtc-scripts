"""
  This file holds default settings value and it is used like template for creation userdef.py file.
  If you want to change any variable listed below do that in generated userdef.py file.
"""

#args.gn template path
webRTCGnArgsTemplatePath='./webrtc/windows/templates/gns/args.gn'

#Path where nuget package and all of the fil
nugetFolderPath = './webrtc/windows/nuget'
nugetVersionInfo = {
                      #Main version number of the NuGet package 
                      'number': '66',
                      #False if not prerelease, Default is based on previous version, False if not prerelease
                      'prerelease': 'Default'
                   }
#Imput NuGet package version number manualy, used if selected version number does not exist on nuget.org
manualNugetVersionNumber = False

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
                              'winuwp'  : ['arm', 'arm64', 'x86', 'x64'],
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
targetPlatforms = [ 'win', 'winuwp' ]
#List of target configurations. Supported cpus are Release and Debug
targetConfigurations = [ 'Release', 'Debug' ]
#TODO: Implement logic to update zslib_eventing_tool.gni based on list of specified programming languages.
targetProgrammingLanguage = [ 'cx', 'cppwinrt', 'c', 'dotnet', 'python' ]

#=========== Supported actions: clean, createuserdef, prepare, build, backup, createnuget. 
# In future it will be added support publishnuget, updatesample.
#'clean' : Based on cleanup options set in cleanupOptions dict, it can be choosen desired cleanup actions.
#'createuserdef' : Deletes existing userdef.py if exists and create a new from defaults.py.
#'prepare' : Prepares developement environemnt for selected targets for choosen cpus, platforms and configurations.
#'build' : Builds selected targets for choosen cpus, platforms and configurations.
#'backup': Backup latest build.
#'createnuget' : Creates nuget package.
#List of actions to perform
actions = [ 'prepare', 'build' ]

buildWithClang = False
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
                'actions' : ['cleanOutput'],
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

#Log filename. If it is empty string, log will be shown in console. 
#In other case, it will log to specified file in folder from where script is run.
logToFile = ''
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