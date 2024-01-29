# Development

ACS3 is primarily a python codebase but there’s also a compiled *RiggingSystem.lx* library that contains all the functionality that is either at the core of ACS3 or is computation intensive and would be too slow when implemented in python.

In practice, you will work with python codebase most of the time and you do not need to touch the C++ part. The compiled .lx files are included in the repository for both Windows and OSX and for both MODO 17+ and older MODO. You only need to set up C++ plugin development environment if you intend to change it or recompile it for newer MODO version (in case backwards compatibility is broken in future).

Compiled .lx libraries can be found in *Kit\AutoCharacterSystem\ExtraStartup*. There are subfolders with all the various versions of the library that are needed depending on which version of MODO you are running and under which OS.

## C++ RiggingSystem.lx plugin setup

The C++ part of ACS3 is a standard MODO’s .lx plugin (dynamic library in fact). In general, the setup process for the *RiggingSystem.lx* library is the same as standard procedure outlined on MODO’s SDK Build Plugins page but for convenience, the exact steps are described below.

[Building Plug-ins — Modo SDK](https://learn.foundry.com/modo/developers/latest/sdk/pages/starting/Building%20Plug-ins.html)

There are 2 components to MODO plugin: a static library that is part of MODO SDK and dynamic library that is the plugin itself. The project needs to be set up to include both of these. 

### Windows

- Ensure you have C++ installed with your Visual Studio. It may not be enabled by default.
- Download MODO SDK and extract it to any location.
- Grab *common* and *include* folders and copy/paste them into *Extra/Sdk* folder within your local *AutoCharacterSystem* repository. You can actually have these folders placed anywhere but this particular location is already added to *.gitignore* so SDK files will not be tracked by git even if they're inside repository.
- Open Visual Studio and create new project.
- Choose creating via Windows Desktop Wizard.
![VS_NewProject](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/cb9346ec-373b-4723-9d79-2ee188b9bf98)
- Pick a path where your project will reside and name project RiggingSystem.
  ![VS_NewProjectPage2](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/06095ecd-2e0e-4572-931f-b76469edb362)
- Set aplication type to .dll, check Empty Project on and the rest of options off.
![VS_NewProjectPage3_DLL](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/aa737872-ac63-4d43-b858-689ba8dec221)

- Now we are going to set up a static library that is MODO SDK.
- Choose *File > Add > New Project*
- Choose Windows Desktop Wizard again.
- Call the project *Common* and set the path to be within the main project.
  ![VS_NewProjectPage4_NewCommon](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/f55e300b-b2b9-477a-9183-5323143dcb4d)
- Set application type to Static Library (.lib) this time. Empty Project on again, everything else off.
![VS_NewProjectPage5_CommonStaticLib](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/7fb4b704-27aa-41bd-99a5-d2e28a500268)

- **From that point on make sure that you are applying settings to both Debug and Release configurations!**
  
- Now that we have both components initialized we're going to set proper platform for the entire solution.
- Open Configuration Manager by clicking on the Platform drop down.
  ![VS_OpenConfManager](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/f4a7a5ed-3489-433d-8330-24eb1964e6a9)
- Switch solution platform to *x64*, then pick *Edit* and in the window that shows up remove *x86* (or *win32*).
  ![VS_ConfManager](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/6ba7dceb-bc86-4147-9ddc-a6dfca480e13)
![VS_RemoveX86](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/b847154a-0af9-4cd3-90d5-2435277d7170)

- We're ready to get the common library building.
- Right click *Source* folder under the *Common* project (in the solution tree) then choose *Add > Existing Item* and navigate to the SDK *common* folder. Select and add all the files from that folder.
- Now we need to configure a few properties. Right click on *Common* project in the solution tree and choose *Properties*.
- Under *C/C++* *General* set *Additional Include Directories* to the path where SDK's include folder is. Change warning level to *W1*.
![VS_CommonIncludeWarning](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/57077bab-efb3-4254-985f-101d4e333eab)
- Add following preprocessor definition: *_CRT_SECURE_NO_DEPRECATE* and if you are compiling for MODO 17+ add *_CRT_NONSTDC_NO_DEPRECATE* as well.
  ![VS_CommonPreprocessor](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/79335cab-85a8-4f7b-8093-92fba01349fc)
- If you are compiling against MODO 17+ SDK you have to set *C++ Language Standard* to *C++ 17* as well.
![VS_LanguageStandard](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/b224fe3b-114c-4fc9-8d47-03adac044498)
- At this point you should be able to successfully build both *Debug* and *Release* configurations of the *Common* library.

- It’s time to set up the actual plugin project.
- Right click *Source* folder under the *RiggingSystem* project (in the solution tree) then choose *Add > Existing Item* and navigate to the *Extra\Src* folder. Select and add all the files from that folder.
- Right click *RiggingSystem* project and choose *Build Dependencies/Project Dependencies*. Make sure *Rigging System* is dependent on *Common*.  
![VS_RS_Dependencies](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/2b0862a5-2dc4-47a2-b26c-e7d9f669c943)
- Open project properties for *RiggingSystem*.
- Add the preprocessing definition _CRT_SECURE_NO_DEPRECATE just like you did for *Common* lib. 
- If you are compiling against *MODO 17* or later SDK you have to add *MODO_17* definition as well.
![VS_RS_Preprocessor](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/20d58f8d-ef7b-4a8e-b42c-0b542480309b)
- In *Linker > General*, add the path to where *common.lib* builds to under *Additional Library Directories*. By default it'll be inside *x64/ConfigurationName* folder.
  ![VS_RS_LibDirectories](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/1b7724e0-95b1-4141-b003-5b0648b738fe)
- Under *Linker > Input*, add *common.lib* to the end of *Additional Dependencies*.
![VS_RS_Dependencies](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/6afb4aa0-35ba-40b8-934f-5acaaf319c3f)
- Finally, add SDK include directories. Keep in mind you have to add both *include* and *include/lxsdk* for MODO 17.
![VS_RS_Includes](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/43349145-2ecd-4c4f-8ff4-97543d9a42fd)
- Now you should be able to successfully build the *RiggingSystem.lx* library.

- Last thing you can do is to add a post build step that will automatically copy compiled *RiggingSystem.lx* to the kit location after each build.
- Still in project properties, under *Build Events > Post-Build Event* add command according to this template (for MODO 17+):
*copy /Y "$(TargetDir)$(TargetName).dll" "PATH_TO_LOCAL_REPO\Kit\AutoCharacterSystem\ExtraStartup\Extra\win64\$(TargetName).lx"*
![VS_RS_PostBuild](https://github.com/lukpazera/AutoCharacterSystem/assets/618099/3ebaa6c3-e69c-421d-9672-2a478a8020c4)


