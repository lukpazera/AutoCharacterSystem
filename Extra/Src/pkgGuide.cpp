// This define is crucial to get M_PI constant on Windows correctly.
// Just including math.h won't cut it.
#define _USE_MATH_DEFINES

#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_matrix.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>

#include "constants.hpp"

namespace {
    const char* GUIDE_PKG_NAME = "rs.pkg.guide";
};


namespace rs {
    namespace guidePackage {
        
        static const char* CHAN_DRAW = "rsgdDraw";
        static const char* CHAN_RADIUS = "rsgdRadius";
        static const char* CHAN_POINT_SIZE = "rsgdPSize";
        static const char* CHAN_THICKNESS = "rsgdThickness";
        static const char* CHAN_OPACITY = "rsgdOpacity";
        
        class CPackage : public CLxPackage
        {
        public:
            
            CPackage ()
            {
            }
            
            ~CPackage ()
            {
            }

        };
        
        
        class CChannels : public CLxChannels
        {
        public:

            void
            init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_DRAW, LXsTYPE_BOOLEAN);
                desc.default_val(true);
                
                desc.add(CHAN_RADIUS, LXsTYPE_DISTANCE);
                desc.default_val(0.015);
                desc.set_min(0.0);
   
                desc.add(CHAN_OPACITY, LXsTYPE_PERCENT);
                desc.default_val(0.8);
                desc.set_min(0.0);
                desc.set_max(1.0);
                
                desc.add(CHAN_POINT_SIZE, LXsTYPE_INTEGER);
                desc.default_val(5);
                desc.set_min(0);
                desc.set_max(32);
                
                desc.add(CHAN_THICKNESS, LXsTYPE_INTEGER);
                desc.default_val(1);
                desc.set_min(1);
                desc.set_max(32);

            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (GUIDE_PKG_NAME);
 
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
            
        // Drawing guide shape
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
				bool draw = chan.IValue(item, CHAN_DRAW);
                if (!draw) { return; }
                
                CLxUser_View view(stroke);
                CChannels socketChannels;
                LXtMatrix rawViewMatrix;
                
                channels_meta->chan_read(chan, item, &socketChannels);
                
                int outlineThickness = chan.IValue(item, CHAN_THICKNESS);
                double opacity = chan.FValue(item, CHAN_OPACITY);
                double radius = chan.FValue(item, CHAN_RADIUS);
                
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
                
                CLxVector fillColor = color;
                // Pick fill color for solid drawing if available
                if (LXe_TRUE == item.PackageTest("glDraw"))
                {
                    fillColor.v[0] = chan.FValue(item, "fillColor.R");
                    fillColor.v[1] = chan.FValue(item, "fillColor.G");
                    fillColor.v[2] = chan.FValue(item, "fillColor.B");
                }
                
                // Calculate all points that will actually be drawn
                std::vector<CLxVector> pointsToDraw;
                for(int i = 0; i < _circlePoints.size(); i++)
                {
                    CLxVector pv = viewMatrix * invOrientation * (_circlePoints[i] * radius * itemScale.v[0]); // using scale X only, good enough for uniform scaling only.
                    pointsToDraw.push_back(pv);
                }
                
                stroke.BeginW (LXiSTROKE_TRIANGLES, fillColor, opacity, 1);
                
                // Draw the solid circle
                for(int i = 0; i < (pointsToDraw.size() - 1); i++)
                {
                    stroke.Vertex3 (0.0, 0.0, 0.0, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex3 (pointsToDraw[i].v[0], pointsToDraw[i].v[1], pointsToDraw[i].v[2], LXiSTROKE_ABSOLUTE);
                    stroke.Vertex3 (pointsToDraw[i + 1].v[0], pointsToDraw[i + 1].v[1], pointsToDraw[i + 1].v[2], LXiSTROKE_ABSOLUTE);
                }
 
                stroke.BeginW (LXiSTROKE_LINES, color, opacity, outlineThickness);
                
                // Draw the outlines of the circle
                for(int i = 0; i < (pointsToDraw.size() - 1); i++)
                {
                    stroke.Vertex3 (pointsToDraw[i].v[0], pointsToDraw[i].v[1], pointsToDraw[i].v[2], LXiSTROKE_ABSOLUTE);
                    stroke.Vertex3 (pointsToDraw[i + 1].v[0], pointsToDraw[i + 1].v[1], pointsToDraw[i + 1].v[2], LXiSTROKE_ABSOLUTE);
                }
                
                unsigned int pointSize = chan.IValue(item, CHAN_POINT_SIZE);
                if (0 < pointSize)
                {
                    CLxVector pointColor = fillColor;
                    pointColor += CLxVector(0.3, 0.3, 0.3);
                	stroke.BeginPoints(pointSize, pointColor, 1.0);
                    stroke.Vertex3 (0.0, 0.0, 0.0, LXiSTROKE_ABSOLUTE);
                }
            }
        };
        
        static CLxMeta_ViewItem3D<CViewItem3D>        v3d_meta;
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.symmetricGuide");
            package_meta.add (&v3d_meta);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
        
            root_meta.initialize();
        } 

    }; // end guidePackage namespace
}; // end rs namespace

