from utility import *

userDefaultsFile = 'userdef'

currentTemplateFile = "defaults"
ortcTemplateFile = "ortc_defaults"
webrtcTemplateFile = "webrtc_defaults"

templatesPath = Utility.convertToPlatformPath("./templates")
ortcDefaultsPath = Utility.convertToPlatformPath("./ortc")
webrtcDefaultsPath = Utility.convertToPlatformPath("./webrtc")

testValue = "default value"

runPrepare = True
runBuild = True
createNuget = False

# ACTION - think about cwd logic, even outside root sdk
# ACTION - Implement args.py logic
# ACTION - Add language target cx, cppwinrt, c, python, dotnet
# ACTION - Copy output files, dll, pdbs etc to cwd

#Supported platforms for specific host OS are not changeable
supportedPlatformsForHostOs = { 'Windows' : ['win32', 'winuwp'],
                                'Darwin' : ['ios', 'mac'],
                                'linux' : ['android', 'linux']
                              }
#macSupportedPlatforms = ['iPhone', 'mac']
#linuxSupportedPlatforms = ['android', 'linux']
#windowsSupportedPlatforms = ['win32', 'winuwp']

targets = [ 'ortc' ]
targetCPUs = [ 'arm', 'x86', 'x64' ]
targetPlatforms = ['win32', 'winuwp' ]
targetConfigurations = [ 'Release', 'Debug' ]

#Supported actions: prepare, build, createNuget, publishNuget, updatePublishedSample 
actions = [ 'prepare', 'build']

"""
Supported formats: %(funcName)s - function name, %(levelname)s - log level name, %(asctime)s - time, %(message)s - log message, %(filename)s - curremt python filename, %(lineno)d - log message line no, %(name)d - module name
For the rest of available attributes you can check on https://docs.python.org/3/library/logging.html#logrecord-attributes

"""
#logFormat = "[%(levelname)-17s] - %(asctime)s - %(message)s (%(filename)s:%(lineno)d)"
logFormat = "[%(levelname)-17s] - %(funcName)s - %(message)s (%(filename)s:%(lineno)d)"

#Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (case sensitive)
logLevel = "DEBUG"
logToFile = ""
overwriteLogFile = False

showTraceOnError = False
showSettingsValuesOnError = False