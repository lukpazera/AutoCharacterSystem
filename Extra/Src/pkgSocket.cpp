
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
    const char* SOCKET_PKG_NAME = "rs.pkg.socket";
};


namespace rs {
    namespace socketPackage {
        
        static const char* CHAN_DRAW_RADIUS = "rsskDrawRadius";
        static const char* CHAN_DRAW_THICKNESS = "rsskDrawThickness";
        static const char* CHAN_DRAW_OPACITY = "rsskDrawOpacity";
        
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
                desc.add(CHAN_DRAW_RADIUS, LXsTYPE_DISTANCE);
                desc.default_val(0.032);
                desc.set_min(0.0);
                
                desc.add(CHAN_DRAW_THICKNESS, LXsTYPE_INTEGER);
                desc.default_val(4);
                desc.set_min(1);
                desc.set_max(32);
                
                desc.add(CHAN_DRAW_OPACITY, LXsTYPE_PERCENT);
                desc.default_val(1.0);
                desc.set_min(0.0);
                desc.set_max(1.0);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (SOCKET_PKG_NAME);

        class CViewItem3D : public CLxViewItem3D
        {

        private:
            int _numPoints; // number of vertices in a circle shape representing socket in viewport
            std::vector<CLxVector> _circlePoints;
            
            /*
             * Calculates all the points for the circle shape
             * that will represent socket in viewport.
             */
            void
            _calculateCirclePoints()
            {
                _circlePoints.clear();
                double step = M_PI * 2.0 / (double)_numPoints;
                for (int i = 0; i < _numPoints; i++)
                {
                    double angle = (double)i * step;
                    double y = sin(angle);
                    double x = cos(angle);
                    CLxVector circlePoint(x, y, 0.0);
                    _circlePoints.push_back(circlePoint);
                }
                _circlePoints.push_back(CLxVector(1.0, 0.0, 0.0)); // add extra point to make a loop
            }

        public:
            CViewItem3D() :
            _numPoints(36)
            {
                _calculateCirclePoints();
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
                LXtMatrix rawViewMatrix;
                
                channels_meta->chan_read(chan, item, &socketChannels);

                int lineThickness = chan.IValue(item, CHAN_DRAW_THICKNESS);
                double opacity = chan.FValue(item, CHAN_DRAW_OPACITY);
                double radius = chan.FValue(item, CHAN_DRAW_RADIUS);
     
                // Get inverted world rotation of the item
                CLxUser_Matrix itemWorldMatrixRaw;
                chan.Object(item, "worldMatrix", itemWorldMatrixRaw);
                CLxMatrix4 itemWorldMatrix(itemWorldMatrixRaw);
                CLxVector itemScale = itemWorldMatrix.getScale();
                itemWorldMatrix.setTranslation(CLxVector()); // clear translation part
                CLxMatrix4 invOrientation = itemWorldMatrix.inverse();
                
                view.Matrix(rawViewMatrix);

                // For some reason the raw view matrix has to be transposed
                // to work correctly. It looks like it gets transposed
                // when CLxMatrix4 is created although SDK code claims automatic
                // transposition is in there (and it is).
                // The issue might be coming from the fact that Matrix3 and Matrix4
                // have different order in MODO (columns versus rows).
                CLxMatrix4 viewMatrixTransposed(rawViewMatrix);
                CLxMatrix4 viewMatrix = viewMatrixTransposed.transpose();

				CLxUser_Scene scene;
				item.Context(scene);
				bool setupMode = (scene.SetupMode() == LXe_TRUE);
				
				// Socket is going to have a different shape in and out of setup mode.
				// Sockets can be used for dynamic parenting in animation so they draw
				// as purple points in animate (out of setup).
				if (setupMode)
				{
					stroke.BeginW(LXiSTROKE_LINES, color, opacity, lineThickness);

					// Calculate all points that will actually be drawn
					std::vector<CLxVector> pointsToDraw;
					for (int i = 0; i < _circlePoints.size(); i++)
					{
						CLxVector pv = viewMatrix * invOrientation * (_circlePoints[i] * radius * itemScale.v[0]); // using scale X only, good enough for uniform scaling only.
						pointsToDraw.push_back(pv);
					}

					// Draw lines that will form the circle
					for (int i = 0; i < (pointsToDraw.size() - 1); i++)
					{
						stroke.Vertex3(pointsToDraw[i].v[0], pointsToDraw[i].v[1], pointsToDraw[i].v[2], LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(pointsToDraw[i + 1].v[0], pointsToDraw[i + 1].v[1], pointsToDraw[i + 1].v[2], LXiSTROKE_ABSOLUTE);
					}
				}
				else
				{
					CLxVector point = viewMatrix * CLxVector(0.0, 0.0, 0.0);
					double pointSize = radius * 50.0; // Convert from mm to units but we want points to be half of the radius
					stroke.BeginPoints(10.0, color, 1.0);
					stroke.Vertex(point, LXiSTROKE_ABSOLUTE);

					CLxVector textColor = color + CLxVector(0.2, 0.2, 0.2);
					std::string label;
					chan.GetString(item, "rsName", label); // We assume generic package is on socket item.
					stroke.Begin(LXiSTROKE_TEXT, textColor, 1.0);

					stroke.Text(label.c_str(), LXiTEXT_LEFT);
					stroke.Vertex(point, LXiSTROKE_ABSOLUTE);
				}
            }
        };

        static CLxMeta_ViewItem3D<CViewItem3D>		v3d_meta;
        
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.sockets;rs.socketBindLoc"); // Needed?
            package_meta.add (&v3d_meta);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
    
            root_meta.initialize();
        }
        
    }; // end socketPackage namespace
}; // end rs namespace

