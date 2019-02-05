actions = [ 'clean' ]

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
                'actions' : ['cleanOutput', 'cleanIdls', 'cleanPrepare'],
                'targets' : ['*'],
                'cpus' : ['*'],
                'platforms' : ['*'],
                'configurations' : ['*']
              }