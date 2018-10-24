import os
import subprocess
import defaults
from utility import Utility
from settings import Settings
from system import System
from logger import Logger
from shutil import copyfile

class Preparation:

  PREPRATARION_WORKING_PATH = './webrtc/xplatform/webrtc'
  
  foldersToGenerate =  [  './chromium/src', 
                          './chromium/src/tools',
                          './chromium/src/third_party',
                          './chromium/src/third_party/winsdk_samples',
                          './chromium/src/third_party/libjingle/source/talk/media/testdata',
                          './third_party',
                          './tools'
                        ]

  foldersToLink = [
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
  ]
  
  @classmethod
  def setUp(cls):
    cls.logger = Logger.getLogger('Prepare')

    if not System.setWorkingDirectory(Utility.convertToPlatformPath(cls.PREPRATARION_WORKING_PATH)):
      System.stopExecution('Unable to set preparation working directory', 1)
    
    cls.createWebRtcChromiumFolders()
    cls.createFolderLinks()

    copyfile(Utility.convertToPlatformPath('../chromium/third_party/BUILD.gn'), Utility.convertToPlatformPath('third_party/BUILD.gn'))
    copyfile(Utility.convertToPlatformPath('../chromium/third_party/DEPS'), Utility.convertToPlatformPath('third_party/DEPS'))
    copyfile(Utility.convertToPlatformPath('../chromium/third_party/OWNERS'), Utility.convertToPlatformPath('third_party/OWNERS'))
    copyfile(Utility.convertToPlatformPath('../chromium/third_party/PRESUBMIT.py'), Utility.convertToPlatformPath('third_party/PRESUBMIT.py'))
    

  @classmethod
  def run(cls, target, platform, cpu, configuration):
    gnOutputPath = os.path.join('out', target + '_' + platform + '_' + cpu + '_' + configuration)
    if not os.path.exists(gnOutputPath):
      os.makedirs(gnOutputPath)

    argsPath = os.path.join(gnOutputPath, 'args.gn')

    copyfile(defaults.webRTCGnArgsTemplatePath, argsPath)

    with open(argsPath) as argsFile:
      newArgs=argsFile.read().replace('-target_os-', platform).replace('-target_cpu-', cpu).replace('-is_debug-',str(configuration.lower() == 'debug').lower())

    with open(argsPath, "w") as argsFile:
      argsFile.write(newArgs)

    os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
    result = subprocess.call([
      'gn',
      'gen',
      gnOutputPath,
      '--ide=' + defaults.VISUAL_STUDIO_VERSION,
    ])

    if result != 0:
      cls.logger.error('Projects generation has failed! ($target, $platform, $cpu, $configuration)')
    """    
    :generateProjectsForPlatform

    %powershell_path% -ExecutionPolicy ByPass -File ..\..\..\bin\RecurseReplaceInFiles.ps1 !outputPath! *.vcxproj "call ninja.exe" "call %DepotToolsPath%\ninja.exe"

    IF EXIST ..\..\..\%webRtcLibsTemplatePath%\WebRtc.%~2.sln CALL:copyTemplates ..\..\..\%webRtcLibsTemplatePath%\WebRtc.%~2.sln !outputPath!\WebRtc.sln
    GOTO:EOF
    """
  @classmethod
  def createWebRtcChromiumFolders(cls):
    for path in cls.foldersToGenerate:
      dirPath = Utility.convertToPlatformPath(path)
      if not os.path.exists(dirPath):
        os.makedirs(dirPath)

  @classmethod
  def createFolderLinks(cls):
    for dict in cls.foldersToLink:
      for source, destination in dict.items():
        Utility.makeLink(source, destination)
