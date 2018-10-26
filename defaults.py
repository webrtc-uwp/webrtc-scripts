from utility import *

userDefaultsFile = 'userdef'

currentTemplateFile = 'defaults'
ortcTemplateFile = 'ortc_defaults'
webrtcTemplateFile = 'webrtc_defaults'

templatesPath = Utility.convertToPlatformPath('./templates')
ortcDefaultsPath = Utility.convertToPlatformPath('./ortc')
webrtcDefaultsPath = Utility.convertToPlatformPath('./webrtc')
relativeDepotToolsPath = Utility.convertToPlatformPath('./webrtc/xplatform/depot_tools')
relativeBuildToolsPath = Utility.convertToPlatformPath('./webrtc/xplatform/buildtools')

BUILD_TOOL_GN = 'gn'
BUILD_TOOL_CLANG_FORMAT = 'clang-format'
VISUAL_STUDIO_VERSION = 'vs2017'

webRTCGnArgsTemplatePath='../../../webrtc/windows/templates/gns/args.gn'

testValue = 'default value'

runPrepare = True
runBuild = True
createNuget = False

#TODO: Add language target cx, cppwinrt, c, python, dotnet
#TODO: Copy output files, dll, pdbs etc to cwd

#Supported platforms for specific host OS are not changeable
supportedPlatformsForHostOs = { 'windows' : ['win', 'winuwp'],
                                'darwin' : ['ios', 'mac'],
                                'linux' : ['android', 'linux']
                              }

#TODO: Add dictionary with supported cpus for targetPlatform
targets = [ 'webrtc' ]
targetCPUs = [ 'arm', 'x86', 'x64' ]
targetPlatforms = [ 'win', 'winuwp' ]
targetConfigurations = [ 'Release', 'Debug' ]

#Supported actions: prepare, build, createNuget, publishNuget, updatePublishedSample 
actions = [ 'prepare', 'build']

"""
Supported formats: %(funcName)s - function name, %(levelname)s - log level name, %(asctime)s - time, %(message)s - log message, %(filename)s - curremt python filename, %(lineno)d - log message line no, %(name)d - module name
For the rest of available attributes you can check on https://docs.python.org/3/library/logging.html#logrecord-attributes

"""
#logFormat = '[%(levelname)-17s] - %(asctime)s - %(message)s (%(filename)s:%(lineno)d)'
logFormat = '[%(levelname)-17s] - %(funcName)s - %(message)s (%(filename)s:%(lineno)d)'

#Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (case sensitive)
logLevel = 'DEBUG'
logToFile = ''
overwriteLogFile = False

showTraceOnError = False
showSettingsValuesOnError = False