"""
  This file contains constant config values. 

"""

#Filename with user default values.
USER_DEFAULTS_FILE = 'userdef'

#args.gn template path. 
WEBRTC_GN_ARGS_TEMPLATE_PATH='./webrtc/windows/templates/gns/args.gn'

#Supported Python version
SUPPORTED_PYTHON_VERSION = '2.7.16'

#Paths are relative to the root SDK path
TEMPLATES_PATH = './templates'
ORTC_DEFAULTS_PATH = './ortc'
WEBRTC_DEFAULTS_PATH = './webrtc'
WEBRTC_SOLUTION_PATH = './webrtc/windows/solutions'
WEBRTC_WRAPPER_PROJECTS_OUTPUT_PATH = './webrtc/windows/solutions/Build/Output/Org.WebRtc'
WEBRTC_SOLUTION_TEMPLATES_PATH = './webrtc/windows/templates/solutions'
RELATIVE_DEPOT_TOOLS_PATH = './webrtc/xplatform/depot_tools'
RELATIVE_BUILD_TOOLS_PATH = './webrtc/xplatform/webrtc/buildtools'
PREPRATARION_WORKING_PATH = './webrtc/xplatform/webrtc'
GN_TARGET_OUTPUT_PATH = '[GN_OUT]/[TARGET]_[PLATFORM]_[CPU]_[CONFIGURATION]'
BUILT_LIBS_DESTINATION_PATH = '/[BUILD_OUTPUT]/[TARGET]/[PLATFORM]/[CPU]/[CONFIGURATION]/'

#Paths are relative to the root SDK path
LICENSE_PATH = './webrtc/windows/LICENSE'
NUGET_TEMPLATES_FOLDER = './webrtc/windows/nuget/templates/'
NUGET_LIBRARIES = '/libraries/[TARGET]/[PLATFORM]/[CPU]/[CONFIGURATION]/'
NUGET_URL = 'https://dist.nuget.org/win-x86-commandline/latest/nuget.exe'
NATIVE_LIB_SRC = './[TARGET]/windows/solutions/Build/Output/Org.[TARGET]/[CONFIGURATION]/[CPU]/[FILE]'
NATIVE_LIB_TARGET = 'runtimes\\win10-[CPU]\\native'
SAMPLES_FOLDER_PATH = './common/windows/samples/'
NUGET_EXECUTABLE_PATH = './webrtc/windows/nuget/nuget.exe'

#Paths are relative to the webrtc root path
GN_OUTPUT_PATH = './out'
#Path where will ba saved built libs, referenced by wrapper projects
BUILD_OUTPUT_PATH = './OUTPUT'

#WebRtc build tools
BUILD_TOOL_GN = 'gn'
BUILD_TOOL_CLANG_FORMAT = 'clang-format'

#Supported VS version
VISUAL_STUDIO_VERSION = 'vs2017'

#Comment that will be printed at the begining of userdef.py file
USERDEF_DESCRIPTION_MESSAGE = 'This file is generated from defaults.py. Be free to change any variable listed below.'

#Paths are relative to root webrtc folder (webrtc/xplatform/webrtc)

#List of folders to create during preparation process
FOLDERS_TO_GENERATE =  [  
                          './chromium/src', 
                          './chromium/src/tools',
                          './chromium/src/third_party',
                          './chromium/src/third_party/winsdk_samples',
                          './chromium/src/third_party/libjingle/source/talk/media/testdata',
                          './third_party',
                          './third_party/idl',
                          './third_party/llvm',
                          './tools',
                        ]

#List of folders, specific to ortc, to create during preparation process
FOLDERS_TO_GENERATE_ORTC =  [  
                            './third_party/ortc',
                          ]

#List of folders and its links to create
FOLDERS_TO_LINK = [
                   {'../buildtools' : './buildtools'},
                   {'../chromium/build' : './build'},
                   {'../chromium/third_party/abseil-cpp' : './chromium/src/third_party/abseil-cpp' },
                   {'../chromium/third_party/jsoncpp' : './chromium/src/third_party/jsoncpp'},
                   {'../chromium/third_party/jsoncpp' : './third_party/jsoncpp'},
                   {'../jsoncpp' : './chromium/src/third_party/jsoncpp/source'},
                   {'../chromium/tools/protoc_wrapper' : './chromium/src/tools/protoc_wrapper'},
                   {'../chromium/tools/protoc_wrapper' : './tools/protoc_wrapper'},
                   {'../chromium/third_party/protobuf' : './chromium/src/third_party/protobuf'},
                   {'../chromium/third_party/yasm' : './chromium/src/third_party/yasm'},
                   {'../chromium/third_party/yasm' : './third_party/yasm'},
                   {'../chromium/third_party/opus' : './chromium/src/third_party/opus'},
                   {'../chromium/third_party/opus' : './third_party/opus'},
                   {'../chromium/third_party/boringssl' : './chromium/src/third_party/boringssl'},
                   {'../chromium/third_party/boringssl' : './third_party/boringssl'},
                   {'../boringssl' : './third_party/boringssl/src'},
                   {'../chromium/third_party/usrsctp' : './chromium/src/third_party/usrsctp'},
                   {'../chromium/third_party/usrsctp' : './third_party/usrsctp'},
                   {'../usrsctp' : './third_party/usrsctp/usrsctplib'},
                   {'../chromium/third_party/libvpx' : './chromium/src/third_party/libvpx'},
                   {'../libvpx' : './chromium/src/third_party/libvpx/source/libvpx'},
                   {'../chromium/third_party/rnnoise' : './chromium/src/third_party/rnnoise'},
                   {'../chromium/testing' : './chromium/src/testing'},
                   {'../chromium/testing' : './testing'},
                   {'../chromium/base' : './base'},
                   {'../yasm/binaries' : './third_party/yasm/binaries'},
                   {'../yasm/patched-yasm' : './third_party/yasm/source/patched-yasm'},
                   {'../opus' : './third_party/opus/src'},
                   {'../chromium/third_party/protobuf' : './third_party/protobuf'},
                   {'../chromium/third_party/expat' : './chromium/src/third_party/expat'},
                   {'../chromium/third_party/expat' : './third_party/expat'},
                   {'../chromium/third_party/googletest' : './chromium/src/third_party/googletest'},
                   {'../chromium/third_party/googletest' : './third_party/googletest'},
                   {'../googletest' : './third_party/googletest/src'},
                   {'../libsrtp' : './third_party/libsrtp'},
                   {'../chromium/third_party/libvpx' : './third_party/libvpx'},
                   {'../libyuv' : './third_party/libyuv'},
                   {'../openmax' : './third_party/openmax_dl'},
                   {'../libjpeg_turbo' : './third_party/libjpeg_turbo'},
                   {'../chromium/third_party/abseil-cpp' : './third_party/abseil-cpp'},
                   {'../chromium/third_party/rnnoise' : './third_party/rnnoise'},
                   {'../../windows/third_party/winuwp_compat' : './third_party/winuwp_compat'},
                   {'../../windows/third_party/winuwp_h264' : './third_party/winuwp_h264'},
                   {'../gflags-build' : './third_party/gflags'},
                   {'../gflags' : './third_party/gflags/src'},
                   {'../winsdk_samples_v71' : './third_party/winsdk_samples'},
                   {'../gyp' : './tools/gyp'},
                   {'../chromium/tools/clang' : './tools/clang'},
                   {'../chromium/third_party/harfbuzz-ng' : './third_party/harfbuzz-ng'},
                   {'../chromium/third_party/freetype' : './third_party/freetype'},
                   {'../chromium/third_party/zlib' : './third_party/zlib'},
                   {'../chromium/third_party/libpng' : './third_party/libpng'},
                   {'../icu' : './third_party/icu'},
                   {'../cryptopp' : './third_party/idl/cryptopp'},
                   {'../zsLib' : './third_party/idl/zsLib'},
                   {'../zsLib-eventing' : './third_party/idl/zsLib-eventing'},
                   {'../webrtc-apis/windows' : './sdk/windows'},
                   {'../webrtc-apis/idl' : './sdk/idl'},
                  ]

#List of folders and its links to create, specific for ortc
FOLDERS_TO_LINK_ORTC = [
                        {'../../../ortc/xplatform/udns' : './third_party/ortc/udns'},
                        {'../../../ortc/xplatform/idnkit' : './third_party/ortc/idnkit'},
                        {'../../../ortc/xplatform/ortclib-cpp' : './third_party/ortc/ortclib'},
                        {'../../../ortc/xplatform/ortclib-services-cpp' : './third_party/ortc/ortclib-services-cpp'},
                      ]

FOLDERS_TO_LINK_LLVM = [
                        {'./chromium/src/third_party/llvm' : './third_party/llvm'},
                        {'./chromium/src/third_party/llvm-build' : './third_party/llvm-build'},
                      ]

#List of filse and its destinations for copying during preparation process
FILES_TO_COPY = [
                  {'../templates/gn/idl_BUILD.gn' : './third_party/idl/BUILD.gn'},
                  {'../templates/gn/tool_build.gni' : './third_party/idl/tool_build.gni'},
                ]

FOLDERS_CONTENT_TO_COPY = [
                            {'../chromium/third_party' : './third_party/'}
                          ]

FILES_TO_IGNORE_FOR_COPYING = [
                              '.git',
                              '.gitignore'
                            ]
#VS2017 folders name to append to Program files or Program Files (x86) parent folder
MSVS_FOLDER_NAME = '/Microsoft Visual Studio/2017'

#List of VS2017 supported versions
MSVS_VERSIONS = (
                  'Community',
                  'Professional',
                  'Enterprise',
                )

#MSVC tools path relative to VS path
MSVC_TOOLS_PATH = '/VC/Tools/MSVC'
VC_AUXILIARY_BUILD_PATH = '/VC/Auxiliary/Build'
VCVARSALL_PATH = '/VC/Auxiliary/Build/vcvarsall.bat'
VC_LIBS_STORE_PATH = 'Microsoft.VCLibs.140.00.Debug_[MAIN_VERSION_NUMBER].0.[BUILD_VERSION_NUMBER].[COUNTER]_[CPU]__8wekyb3d8bbwe'

#Compiler otions combinations for host CPU and target CPU
WINDOWS_COMPILER_OPTIONS = {
                              'x64' : {
                                        'x64' : 'amd64',
                                        'x86' : 'amd64_x86',
                                        'arm' : 'amd64_arm',
                                        'arm64' : 'amd64_arm64'
                                      },
                              'x86' : {
                                        'x64' : 'x86_amd64',
                                        'x86' : 'x86',
                                        'arm' : 'x86_arm',
                                        'arm64' : 'x86_arm64'
                                      }
                            }

#Additional libs to build for webrtc and ortc targets
#'target_name' : Name of target to build. You can name target as your wish.
#                e.g. peercc_server. It is dictionary key for a list
#                of gn targets that will be built for target you define, 
#                flag for linking obj files. (0 don't link, 1 link) and 
#                flag for copying libs, exes and pdbs to OUTPUT folder.
# {
#   'target_name'  : ( [list of gn target paths], merging libs flag, copying to ouptut flag ),    
# }
TARGETS_TO_BUILD = {
                                'webrtc'  : (
                                              [ 
                                                'webrtc',
                                                'third_party/jsoncpp:jsoncpp',
                                                'rtc_base:rtc_json'
                                              ],1,1
                                             ),                                            
                                'ortc'    : (
                                              [ 
                                                'third_party/ortc:ortc',
                                                'third_party/jsoncpp:jsoncpp',
                                                'rtc_base:rtc_json'
                                              ],1,1
                                            )
                              }


#TODO: !!!!! Make this platform dependent and generic !!!!!
COMBINE_LIB_FOLDERS = (
                        '/obj',
                        '/gen',
                        '/uwp_x86',
                        '/uwp_x64',
                        '/uwp_arm',
                        '/win_clang_x64'
                      )

COMBINE_LIB_IGNORE_SUBFOLDERS = (
                                  'libOrtc',
                                  'zslib-eventing-tool',
                                  'test',
                                  'testing',
                                  'examples'
                                )

WINDOWS_IGNORE_WARNINGS = ( 4264, 4221, 4006 )

#Path relative to webrtc root folder
#Path where will be saved .flg files that are used like flags for successfully generated files by idl compiler.
IDL_FLAG_OUTPUT_PATH = '/third_party/idl/zsLib-eventing'
#Path where will be saved . generated files by idl compiler.
IDL_GENERATED_FILES_OUTPUT_PATH = '/sdk/windows/wrapper/generated'

CLANG_CL_PATH = '/third_party/llvm-build/Release+Asserts/bin/clang-cl.exe'
CLANG_UPDATE_SCRIPT_PATH = '/tools/clang/scripts/update.py'
    
#lastcghange.py path
LAST_CHANGE_MODULE_PATH = '/build/util'

PYTHON_PACKAGES_TO_INSTALL = {
                              'win32file' : 'pywin32'
                            }

WEBRTC_TARGET = 'webrtc'
ADDITIONAL_TARGETS_TO_ADD = [
                              '//third_party/idl:idl'
                            ]

#Currently not in use
WEBRTC_WRAPPER_PROJECTS = [
                            'Api/Org_WebRtc/Org_WebRtc_WrapperGlue',
                            'Api/Org_WebRtc/Org_WebRtc',
                          ]


NUGET_WINUWP_WEBRTC_SOLUTION = 'WebRtc.Wrapper.Universal.sln'

TARGET_WRAPPER_SOLUTIONS = {
                              'webrtc' :  {
                                            'winuwp' : 'WebRtc.Wrapper.Universal.sln',
                                            'win' : 'WebRtc.Wrapper.Win32.sln',
                                          },
                              'ortc' :  {
                                          'winuwp' : '',
                                          'net' : ''
                                        }
                            }

WEBRTC_WRAPPER_PROJECTS_OUTPUT_PATH = './webrtc/windows/solutions/Build/Output/Org.WebRtc'

TARGET_WRAPPER_PROJECTS_OUTPUT_PATHS = {
                                          'webrtc' :  {
                                                        'winuwp' : './webrtc/windows/solutions/Build/Output/Org.WebRtc',
                                                        'win' : './webrtc/windows/solutions/Build/Output/Net/Org.WebRtc',
                                                      },
                                          'ortc' :  {
                                                      'winuwp' : '',
                                                      'net' : ''
                                                    }
                                        }

FILES_TO_COPY_FOR_WRAPPER_BUILD = [
                  {'../chromium/third_party/BUILD.gn' : './third_party/BUILD.gn'},
                ]

RUNTIME_STORE_DLLS = {
                        'debug' :  [ 'msvcp140d_app.dll', 'vcruntime140d_app.dll' ],
                        'release' :  [ 'msvcp140_app.dll', 'vcruntime140_app.dll' ]
                      }


UNIT_TESTS_LOG_SEPARATOR = '***UNIT_TEST_FINISHED***\n'
UNIT_TEST_RESULTS_SEPARATOR = '[----------] Global test environment tear-down'
UNIT_TEST_RESULTS_TOTAL_NUMBER_SEPARATOR = '[==========] '
UNIT_TEST_RESULTS_FAILED_SEPARATOR = '[  FAILED  ]'
UNIT_TEST_SUMMARY_SEPARATOR = '========================'
UNIT_TEST_SUMMARY_TEST_SEPARATOR = '-----------------------------\n'
UNIT_TEST_SUMMARY_TOTAL_SEPARATOR = '***********************************\n'
UNIT_TEST_RETRY_NUMBER_FALIED_TESTS = 5
  
ACTION_START_MESSAGE = '\n===================================== [ACTION] STARTED =====================================\n'
ACTION_END_MESSAGE = '\n====================================== [ACTION] ENDED ======================================\n'
  