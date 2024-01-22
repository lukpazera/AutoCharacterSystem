
#include <stdio.h>
#include <chrono>
#include <sstream>

#include <lxu_select.hpp>
#include <lxidef.h>
#include <lx_log.hpp>

#include "modo.hpp"

#include "log.hpp"
#include "cmd_vmapMirror.hpp"

namespace vertexMapMirror {

    unsigned MeshPopup::Flags ()
    {
        return LXfVALHINT_ITEMS;
    }
    
    bool MeshPopup::ItemTest (CLxUser_Item &item)
    {
        if(item.IsA(LXi_CIT_MESH))
        {
            return true;
        }
        
        return false;
    }

    Command::Command()
    {
        dyna_Add ("type",		LXsTYPE_INTEGER);
        dyna_Add ("fromSide",	LXsTYPE_INTEGER);
        dyna_Add ("mesh",		"&item");
        dyna_Add ("sourceMap",  LXsTYPE_STRING);
        dyna_Add ("targetMap",  LXsTYPE_STRING);

        basic_SetFlags (ARGi_FROMSIDE,  LXfCMDARG_OPTIONAL);
        basic_SetFlags (ARGi_MESH, LXfCMDARG_OPTIONAL | LXfCMDARG_HIDDEN);
        basic_SetFlags (ARGi_SOURCE_MAP, LXfCMDARG_OPTIONAL | LXfCMDARG_HIDDEN);
        basic_SetFlags (ARGi_TARGET_MAP, LXfCMDARG_OPTIONAL | LXfCMDARG_HIDDEN);
    }
    
    Command::~Command()
    {
        
    }
    
    int Command::basic_CmdFlags()
    {
        return LXfCMD_UNDO;
    }
    
    void Command::cmd_Execute(unsigned int flags)
    {
        CLxUser_LogService logService;
        CLxUser_Log log;
        logService.GetSubSystem("riggingsys", log);
        
        auto startTime = std::chrono::steady_clock::now();
        
        unsigned int vmapType = _getVertexMapType();

        std::string sourceMapName;
        std::string targetMapName;
        // Take from arguments
        if (dyna_IsSet(ARGi_SOURCE_MAP))
        {
            dyna_String(ARGi_SOURCE_MAP, sourceMapName);

            if (dyna_IsSet(ARGi_TARGET_MAP))
            {
                dyna_String(ARGi_TARGET_MAP, targetMapName);
            }
        }
        else
        {
            return;
        }
        
		if (sourceMapName.empty() || targetMapName.empty())
		{
			return;
		}

        int fromSide = VertexMapMirror::SIDE_RIGHT;
        if (dyna_IsSet(ARGi_FROMSIDE))
        {
        	fromSide = dyna_Int(ARGi_FROMSIDE);
        }

        std::vector<std::string> sourceMaps = splitArgument(sourceMapName, ';');
        std::vector<std::string> targetMaps = splitArgument(targetMapName, ';');
        
		// Grab mesh
		// For now it's fixed mesh from argument.
		std::string meshIdent;
		dyna_String(ARGi_MESH, meshIdent, "");
		if (meshIdent.empty())
		{
			return;
		}

		CLxUser_Scene scene;
		CLxUser_Item meshItem;
		modo::selection::Scene().Get(scene);
		if (LXx_FAIL (scene.ItemLookup(meshIdent.c_str(), meshItem)))
		{
			return;
		}
		 
        VertexMapMirror mirror;
        mirror.BatchMirror(meshItem, vmapType, sourceMaps, targetMaps, fromSide);
        
        /*
        // Take from selection
        else
        {
            modo::selection::VertexMap vmapSelection(vmapType);
            modo::selection::VertexMap::MapList vmapList;
            vmapSelection.GetList(vmapList);
            if (vmapList.empty())
            {
                return;
            }
            sourceMapName = vmapList.at(0).name;
            if (vmapList.size() > 1)
            {
                targetMapName = vmapList.at(1).name;
            }
        }


        VertexMapMirror mirror;
        if (targetMapName.empty())
        {
			int fromSide = VertexMapMirror::SIDE_RIGHT;
            if (dyna_IsSet(ARGi_FROMSIDE))
            {
                fromSide = dyna_Int(ARGi_FROMSIDE);
            }
            mirror.ToTheOtherSide(vmapType, sourceMapName, fromSide);
        }
        else
        {
        	mirror.SourceToTarget(vmapType, sourceMapName, targetMapName);
        }
        */
        auto endTime = std::chrono::steady_clock::now();
        auto elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();
		float elapsedTimeF = (float)(elapsedTime) / 1000.0;

        std::stringstream ss;
        ss << elapsedTimeF;
        std::string elapsedTimeStr = ss.str();
        
        std::string msg = "Map mirrored in: " + elapsedTimeStr;
        log.Message(LXe_INFO, msg.c_str());
    }

    CLxDynamicUIValue *Command::atrui_UIValue (unsigned int index)
    {
        if (index == ARGi_MESH)
        {
        	return new MeshPopup;
        }
        /*
        else if (index == ARGi_TYPE)
        {
            return new VertexMapTypePopup;
        }
        */
        return nullptr;
    }

    const LXtTextValueHint* Command::attr_Hints (unsigned int index)
    {
        if (index == ARGi_TYPE)
        {
            return hintVertexMapType;
        }
        else if (index == ARGi_FROMSIDE)
        {
            return hintFromSide;
        }
        return nullptr;
    }

    unsigned int Command::_getVertexMapType()
    {
        unsigned int vertMapTypeChoice = dyna_Int(ARGi_TYPE);
        if (vertMapTypeChoice == VMAPTYPE_MORPH) {
            return LXi_VMAP_MORPH;
        }
        else
        {
            return LXi_VMAP_WEIGHT;
        }
    }

    std::vector<std::string> Command::splitArgument (const std::string &s, char delim)
    {
        std::vector<std::string> result;
        std::stringstream ss (s);
        std::string item;
        
        while (getline (ss, item, delim)) {
            result.push_back (item);
        }
        
        return result;
    }
    
    void Command::initialize( const char* commandName)
    {
        CLxGenericPolymorph	*srv;
        
        srv = new CLxPolymorph<Command>;
        srv->AddInterface( new CLxIfc_Command<Command> );
        srv->AddInterface( new CLxIfc_Attributes<Command> );
        srv->AddInterface( new CLxIfc_AttributesUI<Command> );
        lx::AddServer( commandName, srv );
    }
    
} // end namespace
