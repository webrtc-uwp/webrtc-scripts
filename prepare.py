import os
from utility import Utility
from settings import Settings
from system import System

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

  foldersToLink = {
                    '../buildtools' : './buildtools',
                    '../chromium/build' : './build',
                    '../chromium/third_party/jsoncpp' : './chromium/src/third_party/jsoncpp',
                    '../jsoncpp' : './chromium/src/third_party/jsoncpp/source',
                    './chromium/src/tools/protoc_wrapper' : '../chromium/tools/protoc_wrapper',
                    './chromium/src/third_party/protobuf' : '../chromium/third_party/protobuf',
                    './chromium/src/third_party/yasm' : '../chromium/third_party/yasm',
                    './chromium/src/third_party/opus' : '../chromium/third_party/opus',
                    './chromium/src/third_party/boringssl' : '../chromium/third_party/boringssl',
                    './chromium/src/third_party/usrsctp' : '../chromium/third_party/usrsctp',
                    './chromium/src/third_party/libvpx' : '../chromium/third_party/libvpx',
                    './chromium/src/third_party/libvpx/source/libvpx' : '../libvpx',
                    './chromium/src/testing' : '../chromium/testing',
                    './testing' : './chromium/src/testing',
                    './base' : '../chromium/base',
                    './tools/protoc_wrapper' : './chromium/src/tools/protoc_wrapper',
                    './third_party/yasm' : './chromium/src/third_party/yasm',
                    './third_party/yasm/binaries' : '../yasm/binaries',
                    './third_party/yasm/source/patched-yasm' : '../yasm/patched-yasm',
                    './third_party/opus' : './chromium/src/third_party/opus',
                    './third_party/opus/src' : '../opus',
                    './third_party/boringssl' : './chromium/src/third_party/boringssl',
                    './third_party/boringssl/src' : '../boringssl',
                    './third_party/usrsctp' : './chromium/src/third_party/usrsctp',
                    './third_party/usrsctp/usrsctplib' : '../usrsctp',
                    './third_party/protobuf' : './chromium/src/third_party/protobuf',
                    './chromium/src/third_party/expat' : '../chromium/third_party/expat',
                    './third_party/expat' : './chromium/src/third_party/expat',
                    './chromium/src/third_party/googletest' : '../chromium/third_party/googletest',
                    './third_party/googletest' : './chromium/src/third_party/googletest',
                    './third_party/googletest/src' : '../googletest',
                    './third_party/libsrtp' : '../libsrtp',
                    './third_party/libvpx' : './chromium/src/third_party/libvpx',
                    './third_party/libyuv' : '../libyuv',
                    './third_party/openmax_dl' : '../openmax',
                    './third_party/libjpeg_turbo' : '../libjpeg_turbo',
                    './third_party/jsoncpp' : './chromium/src/third_party/jsoncpp',
                    './third_party/winuwp_compat' : '../../windows/third_party/winuwp_compat',
                    './third_party/winuwp_h264' : '../../windows/third_party/winuwp_h264',
                    './third_party/gflags' : '../gflags-build',
                    './third_party/gflags/src' : '../gflags',
                    './third_party/winsdk_samples' : '../winsdk_samples_v71',
                    './tools/gyp' : '../gyp',
                    './tools/clang' : '../chromium/tools/clang',
                    './third_party/harfbuzz-ng' : '../chromium/third_party/harfbuzz-ng',
                    './third_party/freetype' : '../chromium/third_party/freetype',
                    './third_party/zlib' : '../chromium/third_party/zlib',
                    './third_party/libpng' : '../chromium/third_party/libpng',
                    './third_party/icu' : '../icu',
  }
  
  @classmethod
  def setUp(cls):
    if not System.setWorkingDirectory(Utility.convertToPlatformPath(cls.PREPRATARION_WORKING_PATH)):
      System.stopExecution('Unable to set preparation working directory', 1)
    
    cls.createWebRtcChromiumFolders()



  @classmethod
  def run(cls):
    pass
    
  
  @classmethod
  def createWebRtcChromiumFolders(cls):
    for path in cls.foldersToGenerate:
      dirPath = Utility.convertToPlatformPath(path)
      if not os.path.exists(dirPath):
        os.makedirs(dirPath)

  @classmethod
  def createFolderLinks(cls):
    pass

  foldersToLink = {
                    '../buildtools' : './buildtools',
                    '../chromium/build' : './build',
                    '../chromium/third_party/jsoncpp' : './chromium/src/third_party/jsoncpp',
                    '../jsoncpp' : './chromium/src/third_party/jsoncpp/source',
                    './chromium/src/tools/protoc_wrapper' : '../chromium/tools/protoc_wrapper',
                    './chromium/src/third_party/protobuf' : '../chromium/third_party/protobuf',
                    './chromium/src/third_party/yasm' : '../chromium/third_party/yasm',
                    './chromium/src/third_party/opus' : '../chromium/third_party/opus',
                    './chromium/src/third_party/boringssl' : '../chromium/third_party/boringssl',
                    './chromium/src/third_party/usrsctp' : '../chromium/third_party/usrsctp',
                    './chromium/src/third_party/libvpx' : '../chromium/third_party/libvpx',
                    './chromium/src/third_party/libvpx/source/libvpx' : '../libvpx',
                    './chromium/src/testing' : '../chromium/testing',
                    './testing' : './chromium/src/testing',
                    './base' : '../chromium/base',
                    './tools/protoc_wrapper' : './chromium/src/tools/protoc_wrapper',
                    './third_party/yasm' : './chromium/src/third_party/yasm',
                    './third_party/yasm/binaries' : '../yasm/binaries',
                    './third_party/yasm/source/patched-yasm' : '../yasm/patched-yasm',
                    './third_party/opus' : './chromium/src/third_party/opus',
                    './third_party/opus/src' : '../opus',
                    './third_party/boringssl' : './chromium/src/third_party/boringssl',
                    './third_party/boringssl/src' : '../boringssl',
                    './third_party/usrsctp' : './chromium/src/third_party/usrsctp',
                    './third_party/usrsctp/usrsctplib' : '../usrsctp',
                    './third_party/protobuf' : './chromium/src/third_party/protobuf',
                    './chromium/src/third_party/expat' : '../chromium/third_party/expat',
                    './third_party/expat' : './chromium/src/third_party/expat',
                    './chromium/src/third_party/googletest' : '../chromium/third_party/googletest',
                    './third_party/googletest' : './chromium/src/third_party/googletest',
                    './third_party/googletest/src' : '../googletest',
                    './third_party/libsrtp' : '../libsrtp',
                    './third_party/libvpx' : './chromium/src/third_party/libvpx',
                    './third_party/libyuv' : '../libyuv',
                    './third_party/openmax_dl' : '../openmax',
                    './third_party/libjpeg_turbo' : '../libjpeg_turbo',
                    './third_party/jsoncpp' : './chromium/src/third_party/jsoncpp',
                    './third_party/winuwp_compat' : '../../windows/third_party/winuwp_compat',
                    './third_party/winuwp_h264' : '../../windows/third_party/winuwp_h264',
                    './third_party/gflags' : '../gflags-build',
                    './third_party/gflags/src' : '../gflags',
                    './third_party/winsdk_samples' : '../winsdk_samples_v71',
                    './tools/gyp' : '../gyp',
                    './tools/clang' : '../chromium/tools/clang',
                    './third_party/harfbuzz-ng' : '../chromium/third_party/harfbuzz-ng',
                    './third_party/freetype' : '../chromium/third_party/freetype',
                    './third_party/zlib' : '../chromium/third_party/zlib',
                    './third_party/libpng' : '../chromium/third_party/libpng',
                    './third_party/icu' : '../icu',
  }



