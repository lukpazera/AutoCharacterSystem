
#ifndef vmapMirror_hpp
#define vmapMirror_hpp

#include <string>

#include <lx_item.hpp>
#include <lx_mesh.hpp>
#include <lx_layer.hpp>

#include "modo.hpp"
#include "log.hpp"
#include "pointSymmetryMap.hpp"

class VertexMapMirror
{
public:
    
    VertexMapMirror();
    ~VertexMapMirror();

	enum {
        SIDE_RIGHT = 0,
        SIDE_LEFT
    };

    bool BatchMirror (CLxUser_Item &meshItem, LXtID4 type, std::vector<std::string> const& sourceMapNames, std::vector<std::string> const& targetMapNames, int fromSide);
    bool SourceToTarget (LXtID4 type, std::string const& sourceMapName, std::string const& targetMapName, modo::ui::Monitor &monitor, float ticks);
	bool ToTheOtherSide(LXtID4 type, std::string mapName, unsigned int fromSide,modo::ui::Monitor &monitor, float ticks);

private:
    bool _setLayerScan (CLxUser_Item &meshItem, CLxUser_LayerScan &layerScan);
    bool _setMesh (CLxUser_LayerScan &layerScan);
    unsigned int _setEditFlags (LXtID4 type);
    void _mirrorCopy (LXtMeshMapID sourceMapID, LXtMeshMapID targetMapID, float *valueBuffer);
    void _mirrorX (LXtID4 type, float *valueBuffer);
    bool _findClosestSymmetricPoint (LXtPointID &symmetricPointID);
    
    CLxUser_MeshService _meshService;
    CLxUser_Item _meshItem;
    CLxUser_Mesh _mesh;
    CLxUser_Point _point;
    CLxUser_Polygon _polygon;
    modo::meshgeo::MeshMap _meshMap;
    PointSymmetryMap _symmap;
};

#endif /* vmapMirror_hpp */
