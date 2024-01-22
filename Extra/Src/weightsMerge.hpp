#ifndef WEIGHTS_MERGE_CMD_H
#define WEIGHTS_MERGE_CMD_H

#include <lxu_command.hpp>
#include <lx_select.hpp>
#include <lx_seltypes.hpp>
#include <lx_item.hpp>
#include <lx_mesh.hpp>
#include <lx_layer.hpp>

#include "constants.hpp"


namespace weightsmerge
{

	struct WMapData
	{
        const char			*name;
        LXtID4				type;
		unsigned int		dimension;
        LXtMeshMapID		ID;
	};

    /* Merges multiple weight maps into single map.
     * All selected maps are merged to the first selected one.
     */
	class WeightsMerge : public CLxBasicCommand
	{
	public:
		WeightsMerge();
		~WeightsMerge();

		CLxUser_SelectionService		svcSel;
		CLxUser_MeshService				svcMesh;
		CLxUser_LayerService			svcLayer;
        CLxUser_SelectionType			styp;


		LXtID4							selID_vmap;
		CLxUser_VMapPacketTranslation	 pkt_vmap;

		CLxUser_Mesh					mesh;
		CLxUser_Point					point;

		WMapData						*wmaps;
		unsigned int					wmapsCount;
		unsigned int					targetWMapIx;
				
		unsigned int					wmap_change;
		unsigned int					wmap_dimension;

		bool InitWMaps();

		static void initialize( const char* command_name);

		int basic_CmdFlags()	OVERRIDE_MACRO;

		void cmd_Execute( unsigned int flags) OVERRIDE_MACRO;
	};

}	// namespace end

#endif
