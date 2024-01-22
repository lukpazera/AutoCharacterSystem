
#include <stdio.h>
#include <lxu_select.hpp>
#include <lxidef.h>

#include "modo.hpp"

#include "cmd_vmapEmpty.hpp"

namespace vertexMapEmpty {

    Command::Command()
    {
        dyna_Add ("isEmpty", LXsTYPE_BOOLEAN);
        dyna_Add ("type", LXsTYPE_STRING);
        dyna_Add ("name", LXsTYPE_STRING);

        basic_SetFlags (ARG_IS_EMPTY, LXfCMDARG_QUERY);
        basic_SetFlags (ARG_TYPE, LXfCMDARG_OPTIONAL);
        basic_SetFlags (ARG_NAME, LXfCMDARG_OPTIONAL);
    }

    Command::~Command()
    {
    }

    /*
     * This command is only for querying.
     */
    LxResult Command::cmd_Query(unsigned int index, ILxUnknownID vaQuery)
    {
        CLxUser_ValueArray va(vaQuery);
        
        if (index == ARG_IS_EMPTY)
        {
            va.Add(_isWeightMapEmpty());
        }
        return LXe_OK;
    }
    
    int Command::basic_CmdFlags()
    {
        return LXfCMD_UI;
    }
        
    void Command::cmd_Execute(unsigned int flags)
    {
    }

    /*
     * Tests whether a first selected map on a first selected mesh
     * is empty. Hard coded for weight map types for now.
     */
    bool Command::_isWeightMapEmpty()
    {
        // Grab mesh item
        modo::selection::ItemOfType meshSelection(LXsTYPE_MESH);
        modo::item::Mesh meshItem;
        if (!meshSelection.GetFirst(meshItem)) { return false; }
        
        // Grab weight map name
        modo::selection::VertexMap vmapSelection(LXi_VMAP_WEIGHT);
        modo::selection::VertexMap::MapList vmapList;
        std::string mapName;
        
        // Bail out if no map selected
        if (!vmapSelection.First(mapName)) { return false; }
    
        // Get mesh interface.
        CLxUser_MeshService meshService;
        CLxUser_Mesh mesh;
        meshItem.GetReadOnlyMesh(mesh);
        
        CLxUser_MeshMap meshMap;
        CLxUser_Point point;
        mesh.GetPoints(point);
        mesh.GetMaps(meshMap);
        
        meshMap.SelectByName(LXi_VMAP_WEIGHT, mapName.c_str());
        LXtMeshMapID mapID = meshMap.ID();
        
        unsigned int pointCount;
        mesh.PointCount(&pointCount);
        
        unsigned int mapDimension;
        meshService.VMapDimension(LXi_VMAP_WEIGHT, &mapDimension);
        float* mapValue = new float[mapDimension]; // It has to be new, it won't compile on Windows otherwise.
        
        bool empty = true;
        
        // Iterate through all points.
        // First point with map value higher then threshold encountenred stops
        // the enumeration - the map is not empty.
        for (unsigned int i = 0; i < pointCount; i++)
        {
            point.SelectByIndex(i);
            point.MapEvaluate(mapID, mapValue);
            
            if (mapValue[0] > 0.02)
            {
                empty = false;
                break;
            }
            
        }
        
        delete [] mapValue; // Be sure to delete mapValue!!!

        return empty;
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
