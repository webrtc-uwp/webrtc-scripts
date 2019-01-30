import sys
import os
import re 
from helper import module_exists, yes_no, convertToPlatformPath 
from settings import Settings
from logger import Logger
from utility import Utility
from nugetUtility import NugetUtility


class ReleaseNotes:
    @classmethod
    def init(cls):
        cls.logger = Logger.getLogger('ReleaseNotes')

    @classmethod
    def select_input(cls):
        """
        Gives user a choice on how to write a release note
        """
        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)
        print('Would you like to insert release notes?')
        print('0) Cancel')
        print('1) Insert directly from command line')
        print('2) Insert from a file')

        cls.init()

        inputValue = 0
        inputNote = False
        try:
            try: input = raw_input
            except NameError: pass
            inputValue = input('Select option: ')
            inputValue = int(inputValue)
        except SyntaxError:
            inputValue = 0
        if inputValue is 0:
            cls.logger.warning('Failed to create a release note')
            return False
        elif inputValue is 1:
            inputNote = cls.cmd_note()
        elif inputValue is 2:
            inputNote = cls.select_file()
        if inputNote is not False:
            mode = 'r+' if os.path.exists(Settings.releaseNotePath) else 'w+'
            with open(Settings.releaseNotePath, mode) as release_notes:
                oldContent = release_notes.read()
                release_notes.seek(0, 0)
                release_notes.write(inputNote.rstrip('\r\n') + '\n' + oldContent)
                cls.logger.info('Successfuly created release note')
        # return to the base directory
        Utility.popd()
        return inputNote

    @classmethod
    def cmd_note(cls):
        """
        Writes a note trough a command line, it can be a multiline note
        :return note: string written in command line
        """  
        print("Enter/Paste your release note. To save use Ctrl-Z (windows) or Ctrl-D in a new line and press Enter.")
        inputNote = sys.stdin.readlines()
        note = ''
        for line in inputNote:
            note += line
        return note

    @classmethod
    def select_file(cls):
        """
        Shows a GUI for file selection, selected txt file will be read and its contents will be returned
        :return note: string read from txt file
        """
        cls.init()
        note = ''
        if module_exists('Tkinter'):
            from Tkinter import Tk
            import tkFileDialog
            root = Tk()
            root.filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
        if module_exists('tkinter'):
            import tkinter
            from tkinter import filedialog
            root = tkinter.Tk()
            root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
        if not root.filename:
            root.destroy()
            cancel_input = yes_no("Would you like to add a release note?")
            if cancel_input is True:
                cls.select_input()
            else:
                return False
        else:
            with open(root.filename, 'r') as file_notes:
                lines = file_notes.readlines()
            for line in lines:
                note += line
        if note == '':
            note = False
        cls.logger.debug("Note selected from a file.")
        return note

    @classmethod
    def get_note(cls, note_source):
        cls.init()
        note = ''
        with open(note_source, 'r') as read_src:
            for line in read_src:
                if '--------------------------------------------' in line:
                    break
                else:
                    note += line
        if note == '':
            note = False
            cls.logger.warning('Release note not written')
        return note
        

    @classmethod
    def set_note_version(cls, version):
        """
        Sets the version of the release note.
        :param version: version of the release note to be set
        """
        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)
        cls.init()
        notes_file = 'releases.txt'
        note = cls.get_note(notes_file)
        if note is not False:
            new_note = '---------------------------------------------------------------------\n' + \
                'Version:   '  + version + '\n' + \
                '---------------------------------------------------------------------\n'
            if os.path.isfile(notes_file):
                with open(notes_file,"r") as src:
                    all_notes=src.readlines()
                    if '--------------------------------------------' not in all_notes[0]:
                        all_notes.insert(0,new_note)
            else:
                all_notes = new_note

            with open(notes_file, 'w') as release_notes:
                release_notes.writelines(all_notes)
                cls.logger.info("Release notes vesion set: " + version)
        # return to the base directory
        Utility.popd()

    @classmethod
    def set_note_version_server(cls):
        """
        Sets the version of the release notes by getting the latest 
        published version of the nuget package published on nuget.org
        """
        #Change current working directory to root sdk directory
        Utility.pushd(Settings.rootSdkPath)
        cls.init()
        notes_file = 'releases.txt'
        #Get the list of WebRtc nuget pakcages with prereleases
        packages = NugetUtility.nuget_cli('list', 'Id:WebRtc', '-PreRelease')
        packages = packages.split('\r\n')
        webrtcRegex = r"^WebRtc+\s"
        #Search the list of the packages for a WebRtc package and set the version
        for package in packages:
            if re.match(webrtcRegex, package, flags=0):
                version = package

        note = cls.get_note(notes_file)
        if note is not False:
            new_note = '---------------------------------------------------------------------\n' + \
                'Version:   '  + version + '\n' + \
                '---------------------------------------------------------------------\n'
            if os.path.isfile(notes_file):
                with open(notes_file,"r") as src:
                    all_notes=src.readlines()
                    if '--------------------------------------------' not in all_notes[0]:
                        all_notes.insert(0,new_note)
            else:
                all_notes = new_note

            with open(notes_file, 'w') as release_notes:
                release_notes.writelines(all_notes)
                cls.logger.info("Release notes vesion set: " + version)    
                
        # return to the base directory
        Utility.popd()
            