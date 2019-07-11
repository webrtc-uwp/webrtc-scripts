"""
  This file holds default settings value and it is used like template for creation userdef.py file.
  If you want to change any variable listed below do that in generated userdef.py file.
"""

#args.gn template path
webRTCGnArgsTemplatePath='./webrtc/windows/templates/gns/args.gn'

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

#=========== Supported actions: clean, createuserdef, prepare, build, backup, createnuget, publishnuget, uploadbackup. 
# In future it will be added support  updatesample.
#'clean' : Based on cleanup options set in cleanupOptions dict, it can be choosen desired cleanup actions.
#'createuserdef' : Deletes existing userdef.py if exists and create a new from defaults.py.
#'prepare' : Prepares developement environemnt for selected targets for choosen cpus, platforms and configurations.
#'build' : Builds selected targets for choosen cpus, platforms and configurations.
#'backup': Backup latest build.
#'createnuget' : Creates nuget package.
#'releasenote' : Gives user a choice on how to add a release note.
#'publishnuget' : Publishes nuget package
#'uploadbackup' : Creates a zipp file with pdb files and nuget package based on configuration and uploads it to onedrive
#List of actions to perform
actions = [ 'prepare', 'build' ]

buildWithClang = False
buildWithCpp17 = False
#Flag if wrapper library should be built. If it is False, it will be built only native libraries
buildWrapper = True

#Flag if rtc_include_tests should be defined. If False, native tests aren't built
includeTests = False

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

#Select ninja environemnt variables whose values will be logged. Available values are 'LIB', 'PATHEXT', 'LIBPATH', 'PATH', 'SYSTEMROOT', 'INCLUDE'
logNinjaEnvironmentFileVariables = ['INCLUDE', 'LIBPATH']

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

#Additional targets that can be built
#'target_name' : Name of target to build. You can name target as your wish.
#                e.g. peercc_server. It is dictionary key for a list
#                of gn targets that will be built for target you define, 
#                flag for linking obj files. (0 don't link, 1 link) and 
#                flag for copying libs, exes and pdbs to OUTPUT folder.
# {
#   'target_name'  : ( [list of gn target paths], merging libs flag, copying to ouptut flag ),    
# }
availableTargetsForBuilding = {
                                'peercc_server'  : (
                                                      [ 
                                                        'peerconnection_server'
                                                      ],0,1
                                                    ),    
                              }
                              
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

enableIdlImpl = False

#Put list of unit tests, present in unitTest dictionary, to execute, or '*' to run all unit tests from unitTest
unitTestsToRun = ['*']

#Dictionary of all availabe unit tests, with list of tests to execute. 
#Each unit test is associated with the list of tests. List can contain just '*' which will run all tests, for that unit test. 
#List can contain specific tests,  that will be run for specific unit test 
# (e.g. 'rtc_pc_unittests' : ['ExternalAuth/SrtpTransportTestWithExternalAuth.SendAndRecvPacket_SRTP_AEAD_AES_256_GCM/1', 
# ExternalAuth/SrtpTransportTestWithExternalAuth.SendAndRecvPacket_AES_CM_128_HMAC_SHA1_80/0]). 
#Also it can be specified to run particular test cases (e.g. 'rtc_pc_unittests' : ['ExternalAuth*','VoiceChannelSingleThreadTest*'],).
#If some of these unit tests are not of interest, remove it from the unitTests dictionary.
#For some specific configuration of unit tests goow practive would be to create a tamplate with tailored unitTests dictionary
unitTests = {
              'audio_codec_speed_tests' : ['*'],
              'audio_decoder_unittests' : ['*'],
              'common_audio_unittests' : ['*'],
              'common_video_unittests' : ['*'],
              'fake_network_unittests' : ['*'],
              'modules_tests' : ['*'],
              'modules_unittests' : [ '*'],
              'ortc_unittests' : ['*'],
              'peerconnection_unittests' : ['*'],
              'rtc_media_unittests' : ['*'],
              'rtc_pc_unittests' : ['*'],
              'rtc_stats_unittests' : ['*'],
              'rtc_unittests' : ['*'],
              'system_wrappers_unittests' : ['*'],
              'test_packet_masks_metrics' : ['*'],
              'tools_unittests' : ['*'],
              'video_capture_tests' : ['*'],
              'video_engine_tests' : ['*'],
              'webrtc_nonparallel_tests' : ['*'],
              'webrtc_opus_fec_test' : ['*'],
              'webrtc_perf_tests' : ['*'],
            }
