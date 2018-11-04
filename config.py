"""
  This file contains constant config values. 

"""

#Filename with user default values.
USER_DEFAULTS_FILE = 'userdef'

#Paths are relative to the root SDK path
TEMPLATES_PATH = './templates'
ORTC_DEFAULTS_PATH = './ortc'
WEBRTC_DEFAULTS_PATH = './webrtc'
RELATIVE_DEPOT_TOOLS_PATH = './webrtc/xplatform/depot_tools'
RELATIVE_BUILD_TOOLS_PATH = './webrtc/xplatform/buildtools'
PREPRATARION_WORKING_PATH = './webrtc/xplatform/webrtc'

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

#List of filse and its destinations for copying during preparation process
FILES_TO_COPY = [
                  {'../chromium/third_party/BUILD.gn' : './third_party/BUILD.gn'},
                  {'../chromium/third_party/DEPS' : './third_party/DEPS'},
                  {'../chromium/third_party/OWNERS' : './third_party/OWNERS'},
                  {'../chromium/third_party/PRESUBMIT.py' : './third_party/PRESUBMIT.py'},
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
VCVARSALL_PATH = '/VC/Auxiliary/Build/vcvarsall.bat'

#Compiler otions combinations for host CPU and target CPU
WINDOWS_COMPILER_OPTIONS = {
                              'x64' : {
                                        'x64' : 'amd64',
                                        'x86' : 'amd64_x86',
                                        'arm' : 'amd64_arm'
                                      },
                              'x86' : {
                                        'x64' : 'x86_amd64',
                                        'x86' : 'x86',
                                        'arm' : 'x86_arm'
                                      }
                            }

#Additional libs to build for webrtc and ortc targets
TARGETS_TO_BUILD = {
                                'webrtc'  : (
                                              [ 
                                                'webrtc',
                                                'third_party/jsoncpp:jsoncpp',
                                                'rtc_base:rtc_json'
                                              ],1
                                             ),                                            
                                'ortc'    : (
                                              [ 
                                                'third_party/ortc:ortc',
                                                'third_party/jsoncpp:jsoncpp',
                                                'rtc_base:rtc_json'
                                              ],1
                                            )
                              }


COMBINE_LIB_FOLDERS = (
                        '/obj',
                        '/gen'
                      )

COMBINE_LIB_IGNORE_SUBFOLDERS = (
                                  'libOrtc',
                                  'zslib-eventing-tool',
                                  'test',
                                  'testing',
                                  'examples'
                                )

WINDOWS_IGNORE_WARNINGS = ( 4264, 4221, 4006 )

#Path relative to webrtc root folder where will ba saved built libs, referenced by wrapper projects
BUILT_LIBS_DESTINATION_PATH = '/BUILD_OUTPUT/[TARGET]/[PLATFORM]/[CPU]/[CONFIGURATION]/'

    