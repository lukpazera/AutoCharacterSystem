
// This define is crucial to get M_PI constant on Windows correctly.
// Just including math.h won't cut it.
#define _USE_MATH_DEFINES

#include <stdio.h>
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_vector.hpp>
#include <lxu_matrix.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>

#include "constants.hpp"

namespace {
    const char* DYNAPARENT_PKG_NAME = "rs.pkg.dynaParent";
};


namespace rs {
    namespace dynaParentPackage {
        
        static const char* CHAN_POINT_SIZE = "rsdpPointSize";
        
        class CPackage : public CLxPackage
        {
        public:
            
            CPackage ()
            {
            }
            
            ~CPackage ()
            {
            }
            
            
            unsigned int counter = 0;
        };
        
        
        class CChannels : public CLxChannels
        {
        public:
            
            void
            init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_POINT_SIZE, LXsTYPE_INTEGER);
                desc.default_val(10);
                desc.set_min(0.0);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (DYNAPARENT_PKG_NAME);

        class CViewItem3D : public CLxViewItem3D
        {

        public:
            CViewItem3D()
            {
            }
            
            /*
             * draw() is called to allow the item to draw itself in 3D.
             *
             * We read the channels for this item into a local CChannel (which would
             * be needed if the channels affected the drawing). This falloff just
             * draws a default unit radius box.
             */
            void
            draw (
                  CLxUser_Item &item,
                  CLxUser_ChannelRead &chan,
                  CLxUser_StrokeDraw &stroke,
                  int selFlags,
                  const CLxVector &color) OVERRIDE_MACRO
            {
                CLxUser_View view(stroke);
                CChannels socketChannels;
                
                channels_meta->chan_read(chan, item, &socketChannels);

                double pointSize = (double)chan.IValue(item, CHAN_POINT_SIZE);
     
				// Dyna parent shape will be drawn where the child item is.
				CLxUser_ChannelGraph channelGraph;
				CLxUser_Scene scene(item);
				channelGraph.from(item, LXsGRAPH_CHANLINKS);

				// Get the child item using channels graph and following
				// link from dyna parent output channel
				CLxUser_Item childItem;
				int childChannelIndex = 0;
				channelGraph.FwdByIndex(item, item.ChannelIndex("matrixOutput"), 0, childItem, &childChannelIndex);
				
				CLxUser_Matrix itemWorldMatrixRaw;
				chan.Object(childItem, "worldMatrix", itemWorldMatrixRaw);
				CLxMatrix4 itemWorldMatrix(itemWorldMatrixRaw);
				CLxVector point = itemWorldMatrix.getTranslation();

				CLxVector nonSetupColor(1.0, 0.3, 0.65);
				stroke.BeginPoints(pointSize, nonSetupColor, 1.0);
				stroke.Vertex(point, LXiSTROKE_ABSOLUTE);
            }
        };

        static CLxMeta_ViewItem3D<CViewItem3D>		v3d_meta;
        
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add (&v3d_meta);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
    
            root_meta.initialize();
        }
        
    }; // end dynaParentPackage namespace
}; // end rs namespace

