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

    parser.add_argument('--cpus', nargs='*', choices=['x64', 'x86', 'arm', 'arm64'], help='Target cpu')

    parser.add_argument('-c','--configurations', nargs='*', choices=['debug', 'release'], help='Target build configuration')
    
    Settings.inputArgs = parser.parse_args()