
#include "lxu_vector.hpp"

#include "vmapMirror.hpp"

VertexMapMirror::VertexMapMirror ()
{
}

VertexMapMirror::~VertexMapMirror ()
{
}

/*
 * Initialises layer scan object.
 */
bool VertexMapMirror::_setLayerScan(CLxUser_Item &meshItem, CLxUser_LayerScan &layerScan)
{
    CLxUser_LayerService layerService;
   
    // Active layer is the same as the foreground layer in layer service.
    // Active layer is the last selected mesh layer (or layers if it was
    // multiple selection.
    unsigned int n = LXf_LAYERSCAN_ACTIVE;
    n |= LXf_LAYERSCAN_MARKVERTS;
    n |= LXf_LAYERSCAN_WRITEMESH;
    
	if (LXx_FAIL(layerService.ScanAllocateItem(meshItem, n, layerScan)))
	{
		return false;
	}

    unsigned int layerCount = layerScan.NumLayers();
    if (layerCount <= 0)
    {
        return false;
    }
    
    return true;
}

/*
 * Initialises mesh object and all accessors.
 */
bool VertexMapMirror::_setMesh(CLxUser_LayerScan &layerScan)
{
    if (layerScan.NumLayers() < 1)
    {
        return false;
    }
    
    if (!layerScan.EditMeshByIndex(0, _mesh))
    {
        return false;
    }
    
    layerScan.MeshItem(0, _meshItem);
    _mesh.MeshMapAccessor(_meshMap);
    _mesh.PointAccessor(_point);
    _mesh.PolygonAccessor(_polygon);
    _symmap.build(_mesh);
    return true;
}

/*
  Mirrors multiple maps in one go.
 
  Parameters
  ----------
 
  sourceMapNames :
      List of maps to mirror from.
 
  targetMapNames :
      List of maps to mirror to. If this list is empty or shorter then
      source maps list mirroring to the other side is done (mirroring within
      the source map) instead of mirroring from source to target.
 
  fromSide :
      enum SIDE_LEFT, SIDE_RIGHT
 */
bool VertexMapMirror::BatchMirror (
	CLxUser_Item &meshItem,
    LXtID4 type,
	std::vector<std::string> const& sourceMapNames,
    std::vector<std::string> const& targetMapNames,
    int fromSide)
{
    CLxUser_LayerScan layerScan;
    if (!_setLayerScan(meshItem, layerScan) || !_setMesh(layerScan))
    {
        return false;
    }
    
	auto mapsCount = sourceMapNames.size();
	int ticksPerMap = 100;
	int ticks = ticksPerMap * mapsCount;
	std::string title("Mirror Weights");
	modo::ui::Monitor monitor(ticks, title);

    for (int i = 0; i < sourceMapNames.size(); i++)
    {
        if (i < targetMapNames.size())
        {
            SourceToTarget(type, sourceMapNames.at(i), targetMapNames.at(i), monitor, ticksPerMap);
        }
        else
        {
            ToTheOtherSide(type, sourceMapNames.at(i), fromSide, monitor, ticksPerMap);
        }
    }

    unsigned int vmapEditFlags = _setEditFlags(type);
    layerScan.SetMeshChange (0, vmapEditFlags);
    layerScan.Apply();
    
	monitor.release();

    return true;
}

/*
 * Mirrors a map onto another one.
 */
	bool
VertexMapMirror::SourceToTarget(
	LXtID4 type,
    std::string const& sourceMapName,
    std::string const& targetMapName,
	modo::ui::Monitor &monitor,
	float ticks)
{
    LXtMeshMapID sourceMapID;
    LXtMeshMapID targetMapID;
    if (!_meshMap.ID(type, sourceMapName, sourceMapID) ||
        !_meshMap.ID(type, targetMapName, targetMapID))
    {
        return false;
    }

    unsigned int pointCount;
    _mesh.PointCount(&pointCount);

    unsigned int mapDimension;
    _meshService.VMapDimension(type, &mapDimension);
    float* mapValue = new float[mapDimension]; // It has to be new, it won't compile on Windows otherwise.
	
    // Clear target map so we only copy over points that have value.
    _meshMap.Select(targetMapID);
    
	float step = ticks / float(pointCount);

    for(unsigned int i = 0; i < pointCount; i++)
    {
		monitor.tick(step);

        _point.SelectByIndex(i);
        
        if (_point.OnSymmetryCenter() == LXe_TRUE)
        {
            _mirrorCopy(sourceMapID, targetMapID, mapValue);
        }
        else
        {
            unsigned int symmetricIndex = -1;
            if (_symmap.getSymmetricPointIndex(i, &symmetricIndex))
            {
            	CLxUser_Point pointSymmetric;
            	_point.Spawn(pointSymmetric);
            	pointSymmetric.SelectByIndex(symmetricIndex);

				bool sourcePointHasValue = (_point.MapValue(sourceMapID, mapValue) == LXe_TRUE);
				if (sourcePointHasValue)
				{
					_mirrorX(type, mapValue);
					pointSymmetric.SetMapValue(targetMapID, mapValue);
				}
				else
				{
					pointSymmetric.ClearMapValue(targetMapID);
				}
            }
			// Clear map values for all non-symmetric points
			else
			{
				_point.ClearMapValue(targetMapID);
			}
        }
    }

    delete [] mapValue; // be sure to delete

    return true;
}

	bool
VertexMapMirror::ToTheOtherSide(
	LXtID4 type,
    std::string mapName,
    unsigned int fromSide,
	modo::ui::Monitor &monitor,
	float ticks)
{
    LXtMeshMapID sourceMapID;
    if (!_meshMap.ID(type, mapName, sourceMapID))
    {
        return false;
    }
    
    unsigned int pointCount;
    _mesh.PointCount(&pointCount);

    unsigned int mapDimension;
    _meshService.VMapDimension(type, &mapDimension);
    float* mapValue = new float[mapDimension]; // It has to be new, it won't compile on Windows otherwise.
    
	float step = ticks / float(pointCount);

    for(unsigned int i = 0; i < pointCount; i++)
    {
		monitor.tick(step);

        _point.SelectByIndex(i);

        if (_point.OnSymmetryCenter() == LXe_TRUE)
        {
            continue;
        }

        CLxFVector pointLocalPos;
        _point.Pos(pointLocalPos);

        // We want to change the mirroring so it pulls weights onto the mirrored side.
        // Pushing is not going to work correctly if not all vertices from target side
        // are mapped to source side ones in the map.
        // Mirror pull is going to make sure that we proces all verts on the target side.
        // So here symmetric vertex is the source of the map value!
        if (fromSide == SIDE_RIGHT && pointLocalPos.x() < 0.0)
        {
            continue;
        }
        else if (fromSide == SIDE_LEFT && pointLocalPos.x() > 0.0)
        {
            continue;
        }

        unsigned int symmetricIndex = -1;
        if (!_symmap.getSymmetricPointIndex(i, &symmetricIndex))
        {
            continue;
        }

        CLxUser_Point pointSymmetric;
        _point.Spawn(pointSymmetric);
        pointSymmetric.SelectByIndex(symmetricIndex);
        
        // If the point we pull from doesn't have map value
        // we clear the value on that target map as well.
        if (pointSymmetric.MapValue(sourceMapID, mapValue) == LXe_FALSE)
        {
        	_point.ClearMapValue(sourceMapID);
        	continue;
        }

        pointSymmetric.MapEvaluate(sourceMapID, mapValue);
        _mirrorX(type, mapValue);
        _point.SetMapValue(sourceMapID, mapValue);
    }
    
    delete [] mapValue; // Be sure to delete mapValue!!!

    return true;
}

	unsigned int
VertexMapMirror::_setEditFlags(
    LXtID4 type)
{
    unsigned int vmapEditFlags = LXf_MESHEDIT_POINTS;

    if (type == LXi_VMAP_MORPH )
    {
        vmapEditFlags |= LXf_MESHEDIT_MAP_MORPH;
    }
    else
    {
        vmapEditFlags |= LXf_MESHEDIT_MAP_OTHER;
    }
    return vmapEditFlags;
}

bool VertexMapMirror::_findClosestSymmetricPoint(LXtPointID &symmetricPointID)
{
    CLxFVector posLocal;
    
    LXtVector hitPos, hitNorm;
    double hitDist;
    
    _point.Pos(posLocal);
    posLocal.v[0] *= -1.0;
    
    CLxVector dPosLocal(posLocal);
    
    if (LXx_OK(_polygon.Closest(0.0, dPosLocal, hitPos, hitNorm, &hitDist)))
    {
        double shortestDistance = 1000000.0;
        
        CLxUser_Point pointSymmetric;
        _point.Spawn(pointSymmetric);
        
        unsigned int vertexCount;
        _polygon.VertexCount(&vertexCount);
        for (unsigned int v = 0; v < vertexCount; v++)
        {
            LXtPointID pID;
            unsigned int pIndex;
            
            _polygon.VertexByIndex(v, &pID);
            pointSymmetric.Select(pID);
            pointSymmetric.Index(&pIndex);
            
            CLxFVector closestVertPos;
            pointSymmetric.Pos(closestVertPos);
            
            CLxVector distanceVector(posLocal);
            
            distanceVector -= closestVertPos;
            double distance = distanceVector.length();
            
            if (distance < shortestDistance)
            {
                shortestDistance = distance;
                symmetricPointID = pID;
            }
        }
    }
    else
    {
        return false;
    }

    return true;
}
void VertexMapMirror::_mirrorCopy(LXtMeshMapID sourceMapID, LXtMeshMapID targetMapID, float *valueBuffer)
{
    _point.MapEvaluate(sourceMapID, valueBuffer);
    _point.SetMapValue(targetMapID, valueBuffer);
}

void VertexMapMirror::_mirrorX (LXtID4 type, float *valueBuffer)
{
    if (type == LXi_VMAP_MORPH)
    {
        valueBuffer[0] *= -1.0;
    }
}
