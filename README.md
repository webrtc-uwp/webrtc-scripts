# WebRTC Scripts

These scripts are used for preparing the development environment, building, and creating WebRTC NuGet packages for the Universal Windows Platform (UWP). The Chromium platform flag used for UWP is `winuwp`.

**Requirements (Windows 10)**
>Note: The below requirements apply only to running the Python scripts. Compiling the binaries has additional requirements which are listed in the [webrtc-uwp-sdk](https://github.com/webrtc-uwp/webrtc-uwp-sdk) repo.
- Visual Studio 2017 or VS Code
- Python 2.7 (Scripts supports Python 3 too, but Google's build system for WebRtc doesn't)
- Strawberry Perl (Supported perl version can be obrained from http://strawberryperl.com/)

## Getting Started
The simplest way to build WebRTC which doesn't require familiarizing yourself with the scripts and how to pass input arguments is opening the `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` solution and building the Org.WebRtc project. This way the WebRTC environment for winuwp will be prepared and built for selected cpu and configuration. You can immediately try it by compiling and running PeerConnectionClient.WebRtc project for a sample app that demonstrates audio\video calls.

## Python Preparation Scripts
These scripts are new so we expect there to be some rough edges - please log any issues on GitHub. If you are eager to try it, you can just run the `run.py` Python script from scripts folder. It can be run from any folder on your disk. (i.e. e:\my_working>python d:\test\webrtc-uwp-sdk\scripts\run.py). The folder from which run.py is called will be the working directory and the file `userdef.py` which contains the default values will be created there. This file can be edited to modify the default actions and platforms. For further details see the section "How to pass input args?"

By running this line of code:
>python run.py
	
the development environment will be prepared for win and winuwp platforms, for ARM, x86 and x64 CPUs and for debug and release configurations. In summary, the build system will pe prepared for all supported combinations. After the preparation process is finished the same script will proceed with building WebRTC for all combinations that were prepared successfully. That will take at least 2 hours. So be patient, or read on for information on specifying the platforms to prepare.

## Python Script Configuration

### How to prepare developement environment

Before you are able to build the WebRTC projects it is required to prepare the development environemnt. To do that, run the `run.py` Python script with the 'prepare' parameter. The script will download and install missing tools. It will create junction links in the directory structure and copy files to the proper locations.  It will also generate ninja files and Visual Studio projects. By default, generated ninja files will use toolchain with Microsoft's cl.exe compiler. If you want to use clang-cl compiler it is necessary to pass --clang input argument.
The folder where these generated files will be saved is: 

>`webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\webrtc_[platform]_[cpu]_[configuration]`
(e.g. `webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\webrtc_winuwp_x86_Release`)
	
## Examples for preparing the development environment

1. The easiest way for those who don't want to play with scripts and are interested in specific cpu and configuration is to open `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` and to build Org.WebRtc project. This won't just prepare environemnt but it will build WebRTC native libs and the wrapper project too.

2. If you want to prepare the environment for all platforms and CPUs and configurations, without building, you can run following command:
    >`python run.py -a prepare`

    Basically, on first run, this command is creating userdef.py file from defaults.py and loading options from it, and then proceeding with preparation. By default options are set to prepare environment for all platforms, CPUs and configurations, but modifying file you can selecte options that are of interest for you. 
    This line can be used if you running this from scripts folder, otherwise you need to specify full or relative path to the run.py script. The result of prepare action can be found in the `webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\` folder.

    In case you want to prepare the environment for specific CPUs and configuration the next command will do the job:
    >`python run.py -a prepare --cpus x64 arm -c debug`

    In case you want to prepare the environment only for win32 platform, x86 CPU and all configurations, and to use clang-cl compiler for building use following command:
    >`python run.py -a prepare -p win --cpus x86 --clang`
	
3. If you want to have even more control over script execution, modifying userdef.py file is right solution for you. First what you need to do is to create that file. To do that it is enough to run: 
    >`python run.py -a createuserdef`
  
    Once userdef.py is created you can start making modifications. That file is created using `default.py` as template. Every option has comments that describes available values and their use.

    **Configuration Example:** Build WebRTC and backup the results of that build for win and winuwp platforms, but only for x64 and release. Your setup should look like this:
    ```
    targets = [ 'webrtc' ]
    targetCPUs = [ 'x64' ]
    targetPlatforms = [ 'win', 'winuwp' ]
    targetConfigurations = [ 'Release' ]
    actions = [ 'prepare', 'build', 'backup' ]
    ```
  
    If you don't run the action to create the `userdef.py` file, the script will be generated automatically. In case you want to reset `userderf.py` to its defaults just run the action `createuserdef` again, or delete the file and run preparation.
  
    If you are satisfied with your changes in userdef.py file and you want to keep it for future use, you can copy that file to `webrtc-uwp-sdk\scripts\templates` folder and name it as you wish.
  This leads us to fourth way of passing input arguments.
  
4. By creating templates and placing them in the`webrtc-uwp-sdk\scripts\templates` folder you are getting a new option for passing input arguments. The best way to create a template is to use the `userdef.py` file as reference. Once you modify variables that are of interest, you can delete rest of them and save it to a template file.
  
    Running the script with the template file looks like this:

    >```python run.py template_file.py ```

    or 
    >```python run.py template_file```
    
    By creating templates for the most common actions you can simplify running scripts.

## Building projects

Beside opening WebRtc.Universal.sln and building WebRTC native libs as well as wrapper libs, from VS, these libs can be built from command line too. Using command line gives you more control over build process. 

Syntax for selecting build options is the same as for prepare action.

## Examples for building WebRTC native and wrapper libs

1. Open `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` and build Org.WebRtc project. This will build WebRTC native and wrapper libs.

2. If you want to prepare the environment and build native and wrapper libs for all platforms and CPUs and configurations that are supported, you can run following command:
    >`python run.py -a prepare build`

    If you already have prepared developer environment and you don't want to build wrapper libs, you can run scripts without prepare action:
    >`python run.py -a build --noWrapper`

    In case you want to build antive and wrapper libs for specific CPUs and configuration the next command will do the job:
    >`python run.py -a build --cpus x64 arm -c debug`

    For preparing and building WebRTC native libs for WinUWP platform, all CPUs and configurations, using clang-cl.exe compiler and skipping building wrapper libs try this:
    >`python run.py -a prepare build -p winuwp --clang --noWrapper`

3. If you want to control scripts execution by modifying userdef.py file, you have to add build action in actions list:
   **Configuration Example:** Build WebRTC native and wrapper libs with Microsoft's cl.exe:
    ```
    actions = [ 'build' ]
    #To build with clang-cl set this variable to True and run prepare action again
    buildWithClang = False
    #To skip building wrapper libs set this variable to False
    buildWrapper = True
    ```

## Build cleanup

  Scripts are giving an option to perform build and environment cleanup. Syntax is the same as for build and prepare actions. It is possible to pass input using userdef.py file or through command line. Depends of settings it can perform build cleanup for specified platforms, CPUs and configurations.

## Cleanup examples

  1.  If you were using `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` to build Org.WebRtc project, you can run just clean on that project and WebRTC native libs as well as generated ninja files and wrapper projects will be cleaned.

  2.  If you want to clean WebRTC native and wrapper libs and ninja files for all platforms, CPUs and configurations, that can be achieved with this command:
      >`python run.py -a clean --cleanOptions cleanoutput`

      To perform the same cleanup, but just for winuwp platform, x64 CPU and debug configuration, it will look like this:
      >`python run.py -a clean --cpus x64 -c debug -p winuwp --cleanOptions cleanoutput`

      To delete results of idl and evenet compiler, command is this:
      >`python run.py -a clean --cleanOptions cleanidls`

      To reset userdef to default settings:
      >`python run.py -a clean --cleanOptions cleanuserdef`

      To revert to state before preparation process use following command:
      >`python run.py -a clean --cleanOptions cleanoutput cleanidls cleanuserdef cleanprepare`

  3.  All of this can be achieved using userdef.py.
      **Configuration Example:** To clean output for all cpus and win platform (in this example targets and configurations are read from targets and configuration variable in userdef.py):
      ```
      actions = [ 'clean' ]
      cleanupOptions = {
                'actions' : ['cleanOutput'],
                'targets' : [],
                'cpus' : ['*'],
                'platforms' : ['win'],
                'configurations' : []
              }
      ```

## Release Notes  

Release notes are created automatically whenever nuget package is created, these notes consist of following:  
```
Package version - version number of the package that is being created  
Latest commit hash value - hash number value for the latest commit of the webrtc-uwp-sdk repository  
Latest commit title - title for that same commit  
Latest commit URL - URL link for that commit  
Date created - date when the package is created  
Github tag link - link for the latest git tag of the webrtc-uwp-sdk repository  
Commits - list of the commits of the webrtc-uwp-sdk repository that have been published in between the latest git tag and the tag before that one, commit titles need to have certain keywords in order to be displayed, these keywords can be selected inside userdef.py file by adding the keyword to the `commitKeywords` array  
```
You can add more information to the automatically created release notes in two different ways:
1. By running the following command:
>```python run.py -a releasenotes```
2. Or by adding 'releasenotes' action into `actions` variable inside userdef.py and running the command: 
>```python run.py```

By following the instruction in the console you will be able to choose a way to insert the release notes, either by typing it directly in the cmd window or by selecting notes from a file (selecting from a file copies files contents and from them creates a release note.)

These manually added release notes are stored in **releases.txt** file inside root sdk directory and are displayed underneath automatically created notes as `Additional information`

Version of the manually added release notes will be added automatically when running `publishnuget` action. It can also be set manually by adding in `--setservernoteversion` option. In that case it will take the latest published version of the nuget package and set it as a release note version in releases.txt.

If the `releasenotes` action is called, and release.txt file already has a note that doesn't have a version set, newly created note will be appended to the top of the previous note that doesn't have a version set.

When running `createnuget` action, release notes, that don't have a version set, are added to the  NuGet package release notes as `Additional information`. 
Every time NuGet package is created trough `createnuget` action notes that have been added to the package are also copied to a .txt file and placed along side the created package.

## Creating NuGet package  
Creating NuGet package for WebRtc UWP can be done by running createnuget action.  

1. Prefered way to do this is to insert 'createnuget' into actions variable inside userdef.py file and set up    the configuration.  
   **Configuration Example:** Create WebRtc NuGet package for WinUWP platform for x64 release version:
   ```
    targets = [ 'webrtc' ]
    targetCPUs = [ 'x64' ]
    targetPlatforms = [ 'winuwp' ]
    targetConfigurations = [ 'Release' ]
    actions = [ 'createnuget' ]
   ```
   *If the prepare and build actions for the selected configuration have not been done before running createnuget action, action variable should have those actions as well in order for the nuget creation process to succeed.* 
   example: ``` actions = [ 'prepare', 'build', 'createnuget' ]```   
   After configuration has been setup, run the following command:   
   >```python run.py ```  

2. All of this can also be done by running the following command:  
   >```python run.py -a createnuget <configuration>```   
   
   ---
   **Configuration**  
   
   Platforms: `-t winuwp`  
   Cpu architectures: `-x x64 x86 arm`  
   Configuration: `-c debug release`   
   
   **Command Example:**  Create WebRtc NuGet package for WinUWP platform for x64 release version:
   >```python run.py -a createnuget -t winuwp -x x64 -c release```  
   *Assuming the prepare and build has been done beforehand*
   
   ---
To select nuget package version, change the `nugetVersionInfo` in userdef.py, this will to automatically select a version for the WebRtc package. Use `number` to select a major number that will determine which version of the WebRtc is used. Use `prerelease` to select what will be appended to the version number E.g., 'Alpha', 'Beta', by setting the value of `prerelease` to 'Default' prerelease will be taken from the last published package for the selected major number(`number`) of the WebRtc NuGet package. If there was no previously published version of the package for the selected version of the WebRtc, created package will automatically be an 'Alpha' prerelease if value of `prerelease` is 'Default'.  
```
nugetVersionInfo = {
                      #Main version number of the NuGet package 
                      'number': '71',
                      #Use '' if not prerelease, 'Default' is based on previous version, or use some other prerelease ('Alpha', 'Beta', ...)
                      'prerelease': 'Default',
                      #Initial version number format
                      'format': '1.[number].0.1[prerelease]'
                   }
```
To create a NuGet package with a custom version number, use `manualNugetVersionNumber` variable in userdef.py to manually add in a version of the nuget package, for example:
>manualNugetVersionNumber = '1.71.0.1-Alpha'
This will override the automated process for finding the version number.

To select a directory where the newly created NuGet packages will be placed, change the value of the `nugetFolderPath` variable inside userdef.py to a path of your choosing.  

Whenever package for the `winuwp` platform is created, git tag is created alongside it. Git tag version number is taken from the created NuGet package version number, this tag is only created locally and is published when the package with the same version number is published trough `publishnuget` action.

When `createnuget` action is called, a file with the release notes is created, these release notes are taken from nuget.org server for the package being created file name will have the following format `ReleaseNotes({name}).txt` where `{name}` is the name of the NuGet package or the ID of the package on nuget.org.  

## Update published sample

Purpose of this action is to clone the sample from the url and branch given in the userdef.py file and place it inside Published_Samples directory, then the cloned sample is compared to the sample inside common\windows\samples directory and the differences are copied from the sample in common\windows\samples directory to the cloned sample. After that is done, a reference to the created NuGet package is added to the cloned sample.  

Update published sample action can be run by adding 'updatesample' into `actions` variable inside userdef.py file.  
Changing the options for this actions can be done inside `updateSampleInfo` variable, that is also contained in userdef.py.  
Option Example:
```
updateSampleInfo = {
                      'package' : 'default',
                      'samples' : [
                        {
                          'name' : 'PeerCC',
                          'url' : 'https://github.com/webrtc-uwp/PeerCC-Sample',
                          'branch': 'webrtc_merge_m66'
                        }
                      ]
                   }
```
`package` variable controls the version of the WebRtc NuGet package that will be used by the sample when it gets updated, if the value is 'default' package used will be most recently created WebRtc NuGet package.  
`samples` variable contains an array of samples where each sample has a `name` that is used to as a name of the cloned sample, in order for the action to work, `name` of the cloned sample should be same as the name of the sample inside common\windows\samples directory that the cloned sample is being compared to. Each sample should also have `url` which is the url of the sample on GitHub and `branch` which determines the branch of that sample.  

## Publish NuGet

Publish NuGet package action can be run in two ways:
1. By running the following command:
>`python run.py -a publishnuget`
2. By inserting 'publishnuget' into `actions` variable inside userdef.py file.
If the publishnuget action is called alongside createnuget action, created NuGet package will be published automatically. In case the publishnuget is run like standalone action, it will be possible to choose the NuGet package to publish from the list of the created packages. List of the created NuGet packages is generated from the packages placed inside a path defined in `nugetFolderPath` variable of the userdef.py file.  
If the key for the NuGet server has not been set, and the publishnuget action is run, package will not be published, and the instruction will be shown on how to set the key for the nuget.org server.  
Key can be set by adding an option `-setnugetkey <key>` when run.py script is called. Example command: `python run.py -a publishnuget -setnugetkey <key>` where `<key>` is the key from acquired the server.
Once the key is set for a particular server, it doesn't need to be set again on the machine where the script is being called from.

When the NuGet package for `winuwp` platform is published, git tag with the same version number as that package is pushed to the github repository.
