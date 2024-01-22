
#include <stdio.h>
#include <lxu_select.hpp>
#include <lxidef.h>
#include <lx_log.hpp>

#include "modo.hpp"

#include "cmd_partitionMesh.hpp"
#include "meshPartitioner.hpp"

namespace partitionMeshByWeights {

    Command::Command()
    {
        dyna_Add ("item", LXsTYPE_STRING);
        dyna_Add ("weightMaps",	LXsTYPE_STRING);
        dyna_Add ("subdivide", LXsTYPE_BOOLEAN);
        dyna_Add ("doubleSided", LXsTYPE_BOOLEAN);
		dyna_Add ("selectionSet", LXsTYPE_BOOLEAN);
        
        basic_SetFlags (ARG_ITEM, LXfCMDARG_OPTIONAL);
        basic_SetFlags (ARG_MAPSLIST, LXfCMDARG_OPTIONAL);
        basic_SetFlags (ARG_SUBDIVIDE, LXfCMDARG_OPTIONAL);
        basic_SetFlags (ARG_DOUBLE_SIDED, LXfCMDARG_OPTIONAL);
		basic_SetFlags (ARG_SELECTION_SET, LXfCMDARG_OPTIONAL);
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
        if (!SetScene())        {
            return;
        }

        CLxUser_Item meshItem;
		if (!SetMeshToPartition(meshItem))
        {
            return;
        }
   
        std::vector<std::string> weightMapNames = GetWeightMapNames();
        if (weightMapNames.empty())
        {
            printf("No weight maps selected.");
            return;
        }

        bool subdivide = _getSubdivide();
        bool doubleSided = _getDoubleSided();
		bool selectionSet = _getSelectionSet();

        std::vector<CLxUser_Item> splitMeshes;
        MeshPartitioner meshPartitioner(meshItem);
        meshPartitioner.SetSubdivide(subdivide);
        meshPartitioner.SetDoubleSided(doubleSided);
        
		if (selectionSet)
		{
			//CLxUser_LogService logService;
			//CLxUser_Log log;
			//logService.GetSubSystem("riggingsys", log);
			//log.Message(LXe_INFO, "Partition mesh into selection sets");
			meshPartitioner.PartitionIntoSelectionSets(weightMapNames);
		}
		else
		{
			splitMeshes = meshPartitioner.ByWeights(weightMapNames);

			modo::selection::Item itemSelection;
			itemSelection.Clear();
			itemSelection.Select(splitMeshes);
		}
    }

    bool Command::SetScene()
    {
    	CLxSceneSelection sceneSelection;
    
        if (!sceneSelection.Get(_scene))
        {
            return false;
        }

        return true;
    }

    bool Command::SetMeshToPartition(CLxUser_Item &meshToPartition)
    {
        if (dyna_IsSet(ARG_ITEM))
        {
            std::string itemIdent;
            dyna_String(ARG_ITEM, itemIdent);
            if (!_scene.ItemLookup(itemIdent.c_str(), meshToPartition))
            {
                return false;
            }

            if (!meshToPartition.IsA(LXi_CIT_MESH))
            {
                return false;
            }
            
            return true;
        }
        
        modo::selection::ItemOfType meshSelection(LXsITYPE_MESH);
        if (!meshSelection.GetFirst(meshToPartition))
        {
                return false;
        }
        
        return true;
    }

    std::vector<std::string> Command::GetWeightMapNames()
    {
        modo::selection::WeightMap weightMapSelection;
        modo::selection::WeightMap::MapList selectedMapsList;
        weightMapSelection.GetList(selectedMapsList);
        
        std::vector<std::string> weightMapNames;

        typename modo::selection::WeightMap::MapList_Itr it = selectedMapsList.begin();
        for (; it != selectedMapsList.end(); ++it)
        {
            weightMapNames.push_back(it->name);
            printf("Weightmap to split: %s \n", it->name.c_str());
        }

        return weightMapNames;
    }

    bool Command::_getSubdivide()
    {
        if (dyna_IsSet(ARG_SUBDIVIDE))
        {
            return (bool)dyna_Int(ARG_SUBDIVIDE);
        }
        return false; // subdivide is false by default
    }
    
    bool Command::_getDoubleSided()
    {
        if (dyna_IsSet(ARG_DOUBLE_SIDED))
        {
            return (bool)dyna_Int(ARG_DOUBLE_SIDED);
        }
        return true;
    }
    
	bool Command::_getSelectionSet()
	{
		if (dyna_IsSet(ARG_SELECTION_SET))
		{
			return (bool)dyna_Int(ARG_SELECTION_SET);
		}
		return false;
	}

    void
    Command::initialize( const char* commandName)
    {
        CLxGenericPolymorph	*srv;
        
        srv = new CLxPolymorph<Command>;
        srv->AddInterface( new CLxIfc_Command<Command> );
        srv->AddInterface( new CLxIfc_Attributes<Command> );
        srv->AddInterface( new CLxIfc_AttributesUI<Command> );
        lx::AddServer( commandName, srv );
    }

} // end namespace
