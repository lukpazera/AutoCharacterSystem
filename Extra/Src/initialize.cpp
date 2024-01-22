

#include "cmd_partitionMesh.hpp"
#include "cmd_vmapMirror.hpp"
#include "cmd_vmapEmpty.hpp"
#include "weightsMerge.hpp"


namespace rs
{

	/*
	 * Declare root item initialisation function here so there's no need to import
	 * root item source file to know its signature.
	 * This avoids having to split items' source files into .hpp and .cpp.
	 * If items sources are ever split into .hpp and .cpp simply import .hpp
	 * and remove this declaration.
	 */
	namespace rootItem { void initialize(); }
	namespace moduleItem { void initialize(); }
	namespace plugPackage { void initialize(); }
	namespace socketPackage { void initialize(); }
	namespace controllerPackage { void initialize(); }
	namespace animControllerPackage { void initialize(); }
	namespace guideIFPackage { void initialize(); }
	namespace itemShapePackage { void initialize(); }
	namespace itemLinkPackage { void initialize(); }
	namespace transformLinkPackage { void initialize(); }
	namespace bindLocatorPackage { void initialize(); }
	namespace genericPackage { void initialize(); }
	namespace guidePackage { void initialize(); }
	namespace embedGuidePackage { void initialize(); }
	namespace colorPackage { void initialize(); }
	namespace itemFitShapePackage { void initialize(); }
	namespace itemAxisPackage { void initialize(); }
	namespace ikfkIFPackage { void initialize(); }
	namespace matchIFPackage { void initialize(); }
	namespace piecePackage { void initialize(); }
	namespace bindMeshPackage { void initialize(); }
	namespace dynaParentPackage { void initialize(); }

}

void initialize()
{
    rs::rootItem::initialize();
	rs::moduleItem::initialize();
	rs::plugPackage::initialize();
	rs::socketPackage::initialize();
	rs::controllerPackage::initialize();
	rs::animControllerPackage::initialize();
	rs::guideIFPackage::initialize();
	rs::itemShapePackage::initialize();
	rs::itemAxisPackage::initialize();
	rs::itemLinkPackage::initialize();
	rs::transformLinkPackage::initialize();
	rs::bindLocatorPackage::initialize();
	rs::genericPackage::initialize();
	rs::guidePackage::initialize();
	rs::embedGuidePackage::initialize();
	rs::colorPackage::initialize();
	rs::itemFitShapePackage::initialize();
	rs::ikfkIFPackage::initialize();
	rs::matchIFPackage::initialize();
	rs::piecePackage::initialize();
	rs::bindMeshPackage::initialize();
	rs::dynaParentPackage::initialize();
        
    partitionMeshByWeights::Command::initialize("rs.mesh.partitionByWeights");
    vertexMapMirror::Command::initialize("rs.vertMap.mirror");
    weightsmerge::WeightsMerge::initialize("rs.weightMaps.merge");
    vertexMapEmpty::Command::initialize("rs.vertexMap.empty");
}
 

