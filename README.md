# AutoCharacterSystem
Modular rigging system for MODO.
Head to ACS3 official website for the full product overview:
[AUTO CHARACTER SYSTEM 3](https://www.autocharactersystem.com)

This repository contains all the ACS3 source code and assets and the ACS3 product can be built from that content.


### ACS3 product Installation
If you just want to install and use ACS3 simply go to releases and download *.zip* file of the latest release. Then follow instructions in the *Getting Started.txt* that’s in the main folder of the ACS repository.


### ACS3 repository breakdown.
ACS3 is primarily a python codebase but there’s also a compiled *RiggingSystem.lx* library that contains all the functionality that is either at the core of ACS3 or is computation intensive and would be too slow when implemented in python.

- **Build** folder contains scripts and instructions on how to build the actual product package, a *.zip* file that end user installs in MODO. See the *buildInstructions.txt* file in that folder for more information on how to build ACS3 package.
  
- **Extra** folder contains all the C++ source files that compile to *RiggingSystem.lx* dynamic library that can be found in the *ExtraStartup/Extra* folder inside ACS3 kit.
  
- **Kit** folder containts *AutoCharacterSystem* subfolder which is the kit itself. Here you will find all the python source code, assets, configs as well as a few development tools that can be used during ACS3 development but are not packaged with the end product.
  
