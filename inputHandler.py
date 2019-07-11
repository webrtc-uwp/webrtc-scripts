import os
import sys
import argparse

from system import System
from settings import Settings

class Input:

  @classmethod
  def parseInput(cls,inputArgs):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('template', nargs='?', help='Template name, where default settings are overwritten')
    
    parser.add_argument('-a','--actions', nargs='*', choices=['clean', 'createuserdef', 'prepare', 'build', 'backup', 'uploadbackup', 'createnuget', 'releasenotes', 'updatesample', 'publishnuget', 'rununittests'], type=str.lower, help='Actions to perform')

    if System.checkIfTargetIsSupported('ortc'):
      parser.add_argument('-t','--targets', nargs='*', choices=['ortc', 'webrtc'], help='Target')
    else:
      parser.add_argument('-t','--targets', nargs='*', choices=['webrtc'], help='Target')
    
    if System.hostOs == 'mac':
      parser.add_argument('-p','--platforms', nargs='*', choices=['mac', 'iOS'], help='Target platform')
    elif System.hostOs == 'linux':
      parser.add_argument('-p','--platforms', nargs='*', choices=['linux', 'android'], help='Target platform')
    else:
      parser.add_argument('-p','--platforms', nargs='*', choices=['winuwp', 'win'], help='Target platform')

    parser.add_argument('-x','--cpus', nargs='*', choices=['x64', 'x86', 'arm', 'arm64'], type=str.lower, help='Target cpu architecture')

    parser.add_argument('-c','--configurations', nargs='*', choices=['debug', 'release'], type=str.lower, help='Target build configuration')

    parser.add_argument('--noColor', action='store_true', help='Do not colorize output')

    parser.add_argument('--noWrapper', action='store_true', help='Do not build wrapper projects')

    parser.add_argument('--cleanOptions', nargs='*', choices=['cleanoutput', 'cleanidls', 'cleanuserdef','cleanprepare'], type=str.lower, help='Target build configuration')
    
    parser.add_argument('--clang', action='store_true', help='Build with clang')
    
    parser.add_argument('--cpp17', action='store_true', help='Build with /std:c++17')
    
    parser.add_argument('--prerelease', nargs='?', action='store', dest='cmdPrerelease', help='Set the prerelease for the created nuget package')

    parser.add_argument('--uploadurl', nargs='?', action='store', dest='uploadBackupURL', help='Cloud storrage URL to wich backup will be uploaded')

    parser.add_argument('--setnugetkey', nargs='?', action='store', dest='setnugetkey', help='Set the api key for the nuget server')

    parser.add_argument('-u','--userTarget', nargs='?', help='Target to build if not webrtc or ortc')

    parser.add_argument('--includeTests', action='store_true', help='Include webrtc native tests (rtc_include_tests=true)')
    
    parser.add_argument('--setservernoteversion', action='store_true', help='Set release notes version from latest nuget package on nuget.org')
    
    parser.add_argument('--idlImpl', action='store_true', help='Pass impl flag when compiling idls.')
    
    parser.add_argument('--unitTests', nargs='*', help='Unit tests to run.')

    parser.add_argument('--logToFile', action='store_true',  help='Log to file.')

    Settings.inputArgs = parser.parse_args()
