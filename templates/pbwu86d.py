#List of targets for which will be performed specified actions. Supported target is webrtc. In future it will be added support for ortc.
targets = [ 'webrtc' ]
#List of target cpus. Supported cpus are arm, x86 and x64
targetCPUs = [ 'x86' ]
#List of target platforms. Supported cpus are win and winuwp
targetPlatforms = [ 'winuwp' ]
#List of target configurations. Supported cpus are Release and Debug
targetConfigurations = [ 'Debug', ]
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
actions = [ 'prepare', 'build' ]

buildWithClang = False
#Flag if wrapper library should be built. If it is False, it will be built only native libraries
buildWrapper = True  
