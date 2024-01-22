
// This define is crucial to get M_PI constant on Windows correctly.
// Just including math.h won't cut it.
#define _USE_MATH_DEFINES

#include <stdio.h>
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_vector.hpp>
#include <lxu_matrix.hpp>
#include <lx_handles.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <lxvmath.h>
#include <math.h>
#include "mitem.hpp"


#include "constants.hpp"


namespace {
    const char* BINDMESH_PKG_NAME = "rs.pkg.bindMesh";
};


namespace rs {
    namespace bindMeshPackage {
      
		static const char* CHAN_DRAW = "rsbmDraw";

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
				desc.add(CHAN_DRAW, LXsTYPE_BOOLEAN);
				desc.default_val(false);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (BINDMESH_PKG_NAME);

        class CViewItem3D : public CLxViewItem3D
        {

        private:
			void drawBoundingBox (CLxVector min, CLxVector max, CLxUser_StrokeDraw &stroke, CLxVector color)
            {
                CLxVector cornerMinX1(min.x(), min.y(), min.z());
                CLxVector cornerMinX2(min.x(), min.y(), max.z());
                CLxVector cornerMinX3(min.x(), max.y(), min.z());
                CLxVector cornerMinX4(min.x(), max.y(), max.z());
                
                CLxVector cornerMaxX1(max.x(), min.y(), min.z());
                CLxVector cornerMaxX2(max.x(), min.y(), max.z());
                CLxVector cornerMaxX3(max.x(), max.y(), min.z());
                CLxVector cornerMaxX4(max.x(), max.y(), max.z());
             
                float width = abs(max.x() - min.x());
                float l = width * 0.15;
                
                stroke.BeginW (LXiSTROKE_LINES, color, 0.75, 2);
                
                // Corner 1
                stroke.Vertex (cornerMinX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX1.x() + l, cornerMinX1.y(), cornerMinX1.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX1.x(), cornerMinX1.y() + l, cornerMinX1.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX1.x(), cornerMinX1.y(), cornerMinX1.z() + l, LXiSTROKE_ABSOLUTE);
 
                // Corner 2
                stroke.Vertex (cornerMinX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX2.x() + l, cornerMinX2.y(), cornerMinX2.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX2.x(), cornerMinX2.y() + l, cornerMinX2.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX2.x(), cornerMinX2.y(), cornerMinX2.z() - l, LXiSTROKE_ABSOLUTE);
 
                // Corner 3
                stroke.Vertex (cornerMinX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX3.x() + l, cornerMinX3.y(), cornerMinX3.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX3.x(), cornerMinX3.y() - l, cornerMinX3.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX3.x(), cornerMinX3.y(), cornerMinX3.z() + l, LXiSTROKE_ABSOLUTE);
 
                // Corner 4
                stroke.Vertex (cornerMinX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX4.x() + l, cornerMinX4.y(), cornerMinX4.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX4.x(), cornerMinX4.y() - l, cornerMinX4.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMinX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMinX4.x(), cornerMinX4.y(), cornerMinX4.z() - l, LXiSTROKE_ABSOLUTE);
  
                // Corner 5
                stroke.Vertex (cornerMaxX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX1.x() - l, cornerMaxX1.y(), cornerMaxX1.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX1.x(), cornerMaxX1.y() + l, cornerMaxX1.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX1, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX1.x(), cornerMaxX1.y(), cornerMaxX1.z() + l, LXiSTROKE_ABSOLUTE);
                
                // Corner 6
                stroke.Vertex (cornerMaxX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX2.x() - l, cornerMaxX2.y(), cornerMaxX2.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX2.x(), cornerMaxX2.y() + l, cornerMaxX2.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX2, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX2.x(), cornerMaxX2.y(), cornerMaxX2.z() - l, LXiSTROKE_ABSOLUTE);
                
                // Corner 7
                stroke.Vertex (cornerMaxX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX3.x() - l, cornerMaxX3.y(), cornerMaxX3.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX3.x(), cornerMaxX3.y() - l, cornerMaxX3.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX3, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX3.x(), cornerMaxX3.y(), cornerMaxX3.z() + l, LXiSTROKE_ABSOLUTE);
                
                // Corner 8
                stroke.Vertex (cornerMaxX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX4.x() - l, cornerMaxX4.y(), cornerMaxX4.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX4.x(), cornerMaxX4.y() - l, cornerMaxX4.z(), LXiSTROKE_ABSOLUTE);
                stroke.Vertex (cornerMaxX4, LXiSTROKE_ABSOLUTE);
                stroke.Vertex3 (cornerMaxX4.x(), cornerMaxX4.y(), cornerMaxX4.z() - l, LXiSTROKE_ABSOLUTE);
            }
            
        public:
            CViewItem3D()
            {
            }
            
            void
            draw (
                  CLxUser_Item &item,
                  CLxUser_ChannelRead &chan,
                  CLxUser_StrokeDraw &stroke,
                  int selFlags,
                  const CLxVector &color) OVERRIDE_MACRO
            {
				bool draw = chan.IValue(item, CHAN_DRAW);
				if (!draw) { return; }

                CLxUser_View view(stroke);
                CChannels bindMeshChannels;
                //LXtMatrix rawViewMatrix;
                
                channels_meta->chan_read(chan, item, &bindMeshChannels);

                CLxUser_Mesh mesh;
                modo::item::Mesh(item).GetReadOnlyMesh(mesh);
     
                LXtBBox bbox;
                mesh.BoundingBox(LXiMARK_ANY, &bbox);
                
                // Determine color
                CLxVector drawColor = color;
                CLxUser_ItemGraph deformersGraph;
                CLxUser_Scene scene;
                item.Context(scene);
                scene.GraphLookup("rs.boundMeshes", deformersGraph);
                unsigned links = deformersGraph.Forward(item);
                if (0 < links)
                {
                    drawColor = CLxVector(0.0, 1.0, 0.0);
                }
                else
                {
                    drawColor = CLxVector(1.0, 0.0, 0.0);
                }
                
                CLxVector min(bbox.min);
                CLxVector max(bbox.max);
                drawBoundingBox(min, max, stroke, drawColor);
            }
        };

        static CLxMeta_ViewItem3D<CViewItem3D>		v3d_meta;
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
			package_meta.add_tag(LXsPKG_GRAPHS, "rs.boundMeshes");
            package_meta.add (&v3d_meta);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
    
            root_meta.initialize();
        }
        
    }; // end bindMeshPackage namespace
}; // end rs namespace

