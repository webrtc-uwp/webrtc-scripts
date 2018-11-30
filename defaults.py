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

#gnOutputPath = r'[GN_OUT]/[TARGET]_[PLATFORM]_[CPU]_[CONFIGURATION]'

#Output path where will be stored nuget package as well as libs and pdbs
#releaseOutputPath = '.'

#Supported platforms for specific host OS 
supportedPlatformsForHostOs = { 
                                'windows' : ['win', 'winuwp'],
                                'darwin' : ['ios', 'mac'],
                                'linux' : ['android', 'linux']
                              }

#Supported cpus for specific target
supportedCPUsForPlatform = { 
                              'winuwp'  : ['arm', 'x86', 'x64'],
                              'win'     : ['x86', 'x64'],
                              'ios'     : ['arm'],
                              'mac'     : [ 'x86', 'x64'],
                              'android' : ['arm'],
                              'linux'   : [ 'x86', 'x64'],
                            }

#TODO: Add dictionary with supported cpus for targetPlatform
targets = [ 'webrtc' ]
targetCPUs = [ 'arm', 'x86', 'x64' ]
targetPlatforms = [ 'win', 'winuwp' ]
targetConfigurations = [ 'Release', 'Debug' ]
targetProgrammingLanguage = [ 'cx', 'cppwinrt', 'c', 'dotnet', 'python' ]

#Supported actions: clean, createuserdef, prepare, build, createNuget, publishNuget, updatePublishedSample 
actions = [ 'prepare', 'build' ]

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

buildWrapper = True     
"""
Supported formats: %(funcName)s - function name, %(levelname)s - log level name, %(asctime)s - time, %(message)s - log message, %(filename)s - curremt python filename, %(lineno)d - log message line no, %(name)d - module name
For the rest of available attributes you can check on https://docs.python.org/3/library/logging.html#logrecord-attributes

"""
#logFormat = '[%(levelname)-17s] - %(asctime)s - %(message)s (%(filename)s:%(lineno)d)'
logFormat = '[%(levelname)-17s] - [%(name)-15s] - %(funcName)-30s - %(message)s (%(filename)s:%(lineno)d)'

#Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (case sensitive)
logLevel = 'DEBUG'
logToFile = ''
overwriteLogFile = False
noColoredOutput = False

stopExecutionOnError = False
showTraceOnError = True
showSettingsValuesOnError = True
showPATHOnError = True

#Windows specific variables
msvsPath = ''

enableBackup = False
libsBackupPath = 'Backup'