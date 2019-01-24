import sys
import os
from helper import module_exists, yes_no, convertToPlatformPath 
from settings import Settings


class ReleaseNotes:

    @classmethod
    def run(cls, note_file, target, platform, version):
        note = cls.default_note(note_file, target, platform, version)
        cls.set_note_version(note, note_file, target, platform, version)
        return note

    @classmethod
    def select_input(cls):
        """
        Gives user a choice on how to write a release note
        """
        print('Would you like to insert release notes?')
        print('0) Cancel')
        print('1) Insert directly from command line')
        print('2) Insert from a file')

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
            print('Failed to create a release note')
            return False
        elif inputValue is 1:
            inputNote = cls.cmd_note()
        elif inputValue is 2:
            inputNote = cls.select_file()
        if inputNote is not False:
            with open(Settings.releaseNotePath, 'w') as release_notes:
                release_notes.writelines(inputNote)
                print('Successfuly created release note')
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
        return note

    @classmethod
    def default_note(cls, note_source, target, platform, version):
        note = ''
        with open(note_source, 'r') as read_src:
            for line in read_src:
                if '--------------------------------------------' in line:
                    break
                else:
                    note += line
        return note
        

    @classmethod
    def set_note_version(cls, note, notes_file, target, platform, version):
        if note is not False:
            new_note = '---------------------------------------------------------------------\n' + \
                'Version:   ' + target + '.' + platform + ' ' + version + '\n' + \
                '---------------------------------------------------------------------\n'
            notes_file = convertToPlatformPath(notes_file)
            if os.path.isfile(notes_file):
                with open(notes_file,"r") as src:
                    all_notes=src.readlines()
                    if '--------------------------------------------' not in all_notes[0]:
                        all_notes.insert(0,new_note)
            else:
                all_notes = new_note

            with open(notes_file, 'w') as release_notes:
                release_notes.writelines(all_notes)
