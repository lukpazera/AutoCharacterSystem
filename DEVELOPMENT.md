# Development

ACS3 is primarily a python codebase but there’s also a compiled *RiggingSystem.lx* library that contains all the functionality that is either at the core of ACS3 or is computation intensive and would be too slow when implemented in python.

In practice, you will work with python codebase most of the time and you do not need to touch the C++ part. The compiled .lx files are included in the repository for both Windows and OSX and for both MODO 17+ and older MODO. You only need to set up C++ plugin development environment if you intend to change it or recompile it for newer MODO version (in case backwards compatibility is broken in future).

Compiled .lx libraries can be found in *Kit\AutoCharacterSystem\ExtraStartup*. There are subfolders with all the various versions of the library that are needed depending on which version of MODO you are running and under with OS.

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
- Pick a path where your project will reside and name project RiggingSystem.
- Set aplication type to .dll, check Empty Project on and the rest of options off.

- Now we are going to set up a static library that is MODO SDK.
- Choose File > Add > New Project
- Choose Windows Desktop Wizard again.
- Call the project *common* and set the path to be within the main project.
- Set application type to Static Library (.lib) this time. Empty Project on again, everything else off.

- From that point on make sure that you are applying settings to both Debug and Release configurations!
  
- Now that we have both components initialized we're going to set proper platform for the entire solution.
- Open Configuration Manager by clicking on the Platform drop down.
- Switch solution platform to x64, then pick Edit and in the window that shows up remove x86 (or win32).
  
- We're ready to get the common library building.
- Right click Source folder under the Common project (in the solution tree) then choose Add > Existing Item and navigate to the SDK common folder. Select and add all the files from that folder.
- Now we need to configure required project properties. Right click on Common project in the solution tree and choose properties.
