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
    
    parser.add_argument('-a','--actions', nargs='*', choices=['clean','createuserdef', 'prepare', 'build', 'backup', 'createnuget'], type=str.lower, help='Actions to perform')

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

    parser.add_argument('--cpus', nargs='*', choices=['x64', 'x86', 'arm', 'arm64'], type=str.lower, help='Target cpu')

    parser.add_argument('-c','--configurations', nargs='*', choices=['debug', 'release'], type=str.lower, help='Target build configuration')

    parser.add_argument('--noColor', action='store_true', help='Do not colorize output')

    parser.add_argument('--noWrapper', action='store_true', help='Do not build wrapper projects')

    parser.add_argument('--cleanOptions', nargs='*', choices=['cleanoutput', 'cleanidls', 'cleanuserDef','cleanprepare'], type=str.lower, help='Target build configuration')
    
    parser.add_argument('--clang', action='store_true', help='Build with clang')
    
    Settings.inputArgs = parser.parse_args()