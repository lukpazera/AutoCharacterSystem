#include "weightsMerge.hpp"

#include <lx_io.hpp>
#include <lx_stddialog.hpp>
#include <lx_log.hpp>
#include <lx_layer.hpp>
#include <sstream>

// selection utilities for easier selections
#include <lxu_select.hpp>

namespace weightsmerge
{
	// utility function
	std::string
	IntToString( unsigned int number )
	{
		std::stringstream ss;
		ss << number;
		return ss.str();
	}

	std::string
	FloatToString( float number )
	{
		std::stringstream ss;
		ss << number;
		return ss.str();
	}

	WeightsMerge::WeightsMerge() : CLxBasicCommand()
	{
		wmaps = NULL;
	}

	WeightsMerge::~WeightsMerge()
	{
		if (wmaps)
			delete[] wmaps;
	}

	int
	WeightsMerge::basic_CmdFlags()
	{
		return( LXfCMD_MODEL | LXfCMD_UNDO );
	}

	bool
	WeightsMerge::InitWMaps ()
	{
		void			*pkt;

		int selCount = svcSel.Count( selID_vmap );

        LXtID4	temp_type;
		wmapsCount = 0;

        for (int i = 0; i < selCount; i++) 
		{
			pkt = svcSel.ByIndex ( selID_vmap, i);
			if (pkt)
			{
				pkt_vmap.Type( pkt, &temp_type );
				if ( temp_type == LXi_VMAP_WEIGHT )
				{
					wmapsCount++;
				}
			}
		}

		if (wmapsCount > 1)
		{
			wmaps = new WMapData [ wmapsCount ];
			unsigned int tempCount = 0;
			for (int i = 0; i < selCount; i++) 
			{
				pkt = svcSel.ByIndex ( selID_vmap, i);
				if (pkt)
				{
					pkt_vmap.Type( pkt, &temp_type );
					if ( temp_type == LXi_VMAP_WEIGHT )
					{
						pkt_vmap.Type( pkt, &wmaps[ tempCount ].type );
						pkt_vmap.Name( pkt, &wmaps[ tempCount ].name );
						tempCount ++;
					}
				}
			}
			return true;
		}
		else return false;
	}

	void
	WeightsMerge::cmd_Execute( unsigned int flags )
	{
		std::string			itemName;

		CLxUser_LogService	service_log;
		CLxUser_Log log;
		service_log.GetSubSystem( "io-status", log );

		//log.Message( LXe_INFO, "---Weights Merge Log---" );

        selID_vmap = svcSel.LookupType ("vmap");

        svcSel.GetImplementation (selID_vmap, styp);
        pkt_vmap.set (styp);

		if ( InitWMaps() )
		{
			std::string msg;

			//log.Message( LXe_INFO, "Number of weight maps to merge:" );
			//log.Message( LXe_INFO, IntToString( wmapsCount ).c_str() );

			svcMesh.VMapDimension( LXi_VMAP_WEIGHT, &wmap_dimension );
			wmap_change = LXf_MESHEDIT_MAP_OTHER;

			CLxUser_LayerScan	 scan;
	
			unsigned int n = LXf_LAYERSCAN_ACTIVE | LXf_LAYERSCAN_MARKVERTS;
            n |= LXf_LAYERSCAN_WRITEMESH;

			if (!svcLayer.BeginScan (n, scan))
                return;

			n = scan.NumLayers();

			unsigned int pointCount = 0;

			float *mapVal = NULL;
			mapVal = new float [ wmap_dimension ];
			float *mergedMapVal = NULL;
			mergedMapVal = new float [ wmap_dimension ];

			for (unsigned int i = 0; i < n; i++)
			{
				scan.EditMeshByIndex (i, mesh);

				CLxUser_MeshMap mmap( mesh );

				for (unsigned int w = 0; w < wmapsCount; w++ )
				{
					mmap.SelectByName( wmaps[ w ].type, wmaps[ w ].name);
					wmaps[ w ].ID = mmap.ID();
				}

				mesh.PointCount( &pointCount );
				//log.Message( LXe_INFO, "points in layer:" );
				//log.Message( LXe_INFO, std::string( IntToString( pointCount ) ).c_str() );
				
				point.fromMeshObj( mesh );

				for (unsigned int j = 0; j < pointCount; j++ )
				{
					point.SelectByIndex( j );
					mergedMapVal[ 0 ] = 0.0f;

					for (unsigned int w = 0; w < wmapsCount; w++)
					{
						if (LXx_OK (point.MapEvaluate ( wmaps[ w ].ID, mapVal)))
						{
							mergedMapVal[ 0 ] += mapVal[ 0 ];
							if ( mergedMapVal[ 0 ] > 0.99f )	{
								mergedMapVal[ 0 ] = 1.0f;
							}
							else if ( mergedMapVal[ 0 ] < 0.01f )	{
								mergedMapVal[ 0 ] = 0.0f;
							}
						}
					}
					point.SetMapValue( wmaps[ wmapsCount - 1 ].ID, mergedMapVal );
							
					//log.Message( LXe_INFO, std::string( FloatToString( *mergedMapVal ) ).c_str() );
				}

				scan.SetMeshChange (i, LXf_MESHEDIT_POINTS | wmap_change);
			}

			scan.Apply ();

			if ( mapVal )
				delete [] mapVal;
			if ( mergedMapVal )
				delete [] mergedMapVal;
		}
		else
		{
			log.Message( LXe_INFO, "Select at least 2 weight maps to perform merge!" );
		}
	}

	// this is initialize method that is called by the real initialise from main cpp
	void
	WeightsMerge::initialize( const char* command_name)
	{
		CLxGenericPolymorph		*srv;

		srv = new CLxPolymorph<WeightsMerge>;
		srv->AddInterface( new CLxIfc_Command<WeightsMerge> );
		lx::AddServer( command_name, srv );
	}
}
