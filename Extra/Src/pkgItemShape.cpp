
// This define is crucial to get M_PI constant on Windows correctly.
// Just including math.h won't cut it.
#define _USE_MATH_DEFINES

#include <map>

#include <lx_vp.hpp>
#include <lxu_package.hpp>
#include <lxu_attrdesc.hpp>
#include <lxidef.h>
#include <math.h>

#include "constants.hpp"

namespace {
    const char* ITEM_SHAPE_PKG_NAME = "rs.pkg.itemShape";
};

namespace rs {
    namespace itemShapePackage {
        
        static const char* CHAN_ENABLE = "rsisEnable";

        static const char* CHAN_SHAPE = "rsisShape";

        static const char* CHAN_SHAPE_X_AXIS = "rsisXShapeAxis";
        static const char* CHAN_SHAPE_Y_AXIS = "rsisYShapeAxis";
        static const char* CHAN_SHAPE_Z_AXIS = "rsisZShapeAxis";
        static const char* CHAN_SHAPE_THICKNESS = "rsisThickness";
        static const char* CHAN_SHAPE_WIDTH = "rsisWidth";
        static const char* CHAN_COLOR_SOURCE = "rsisColorSource";
        static const char* CHAN_CUSTOM_COLOR = "rsisCustomColor";
        static const char* CHAN_CUSTOM_COLOR_R = "rsisCustomColor.R";
        static const char* CHAN_CUSTOM_COLOR_G = "rsisCustomColor.G";
        static const char* CHAN_CUSTOM_COLOR_B = "rsisCustomColor.B";
        
        static const char* CHAN_RING_X_SEGMENTS = "rsisRingXSegs";
        static const char* CHAN_RING_Y_SEGMENTS = "rsisRingYSegs";
        static const char* CHAN_RING_Z_SEGMENTS = "rsisRingZSegs";

        static const char* CHAN_RING_X_SEGMENT_OFFSET = "rsisRingXSegOffset";
        static const char* CHAN_RING_Y_SEGMENT_OFFSET = "rsisRingYSegOffset";
        static const char* CHAN_RING_Z_SEGMENT_OFFSET = "rsisRingZSegOffset";
		static const char* CHAN_RING_RADIUS = "rsisRingRadius";
        
        static const char* CHAN_RECTANGLE_X_WIDTH = "rsisRectXWidth";
        static const char* CHAN_RECTANGLE_Y_WIDTH = "rsisRectYWidth";
        static const char* CHAN_RECTANGLE_Z_WIDTH = "rsisRectZWidth";

        static const char* CHAN_RECTANGLE_X_HEIGHT = "rsisRectXHeight";
        static const char* CHAN_RECTANGLE_Y_HEIGHT = "rsisRectYHeight";
        static const char* CHAN_RECTANGLE_Z_HEIGHT = "rsisRectZHeight";
        
        static const char* CHAN_OFFSET = "rsisOffset";
        static const char* CHAN_OFFSET_X = "rsisOffset.X";
        static const char* CHAN_OFFSET_Y = "rsisOffset.Y";
        static const char* CHAN_OFFSET_Z = "rsisOffset.Z";
        
        static const char* CHAN_OPACITY = "rsisOpacity";
        
        static LXtTextValueHint shapeHints[] = {
            0, "ring",
            1, "square",
            2, "box",
            -1, NULL
        };

        static LXtTextValueHint colorHints[] = {
            0, "wire",
            1, "fill",
            2, "custom",
            -1, NULL
        };
        
        struct ShapeDrawData {
            int axis;
            int shape;
            double thickness; // 3d thickness, not line thickness
            double width;
            double opacity;
            
            double ringSegmentsCount;
            
            double ringSegmentOffset;
            double ringRadius;
            
            double rectWidth;
            double rectHeight;
            
            CLxVector offset;
            CLxVector wireColor;
            CLxVector fillColor;
        };

        struct SquareVerts {
            CLxVector out1, out2, out3, out4;
            CLxVector in1, in2, in3, in4;
        };
        
        struct QuadVerts {
            CLxVector a, b, c, d;
        };

        class CPackage : public CLxPackage
        {
        public:
            
        };
        
        /*
         * CLxCustomChannelUI allows for custom enabled/disabled behaviours for channels.
         * Implement enabled() method, look how this interface is set on a given channel from CLxChannels init().
         */
        class CCustomColorEnable : public CLxCustomChannelUI
        {
        public:
            bool enabled(CLxUser_Item &item, CLxUser_ChannelRead &read, CLxUser_Message &msg) OVERRIDE_MACRO
            {
                if (read.IValue(item, CHAN_COLOR_SOURCE) == 2) // 2 is custom color
                {
                    return true;
                }
                return false;
            }
        };

        class CRingSpecificEnable : public CLxCustomChannelUI
        {
        public:
            bool enabled(CLxUser_Item &item, CLxUser_ChannelRead &read, CLxUser_Message &msg) OVERRIDE_MACRO
            {
                if (read.IValue(item, CHAN_SHAPE) == 0) // 0 is ring shape
                {
                    return true;
                }
                return false;
            }
        };

        class CRectangleSpecificEnable : public CLxCustomChannelUI
        {
        public:
            bool enabled(CLxUser_Item &item, CLxUser_ChannelRead &read, CLxUser_Message &msg) OVERRIDE_MACRO
            {
                if (read.IValue(item, CHAN_SHAPE) == 1) // 1 is rectangle shape
                {
                    return true;
                }
                return false;
            }
        };
        
        class CChannels : public CLxChannels
        {
        public:

            void init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_ENABLE, LXsTYPE_BOOLEAN);
                desc.default_val(1);
                
                desc.add(CHAN_SHAPE, LXsTYPE_INTEGER);
                desc.set_hint(shapeHints);
                desc.default_val(0);
                
                desc.add(CHAN_SHAPE_X_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(false);

                desc.add(CHAN_SHAPE_Y_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(true);
                
                desc.add(CHAN_SHAPE_Z_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(false);
                
                desc.add(CHAN_SHAPE_WIDTH, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.025);
                
                desc.add(CHAN_SHAPE_THICKNESS, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.0);

                desc.add(CHAN_COLOR_SOURCE, LXsTYPE_INTEGER);
                desc.set_hint(colorHints);
                desc.default_val(0);
                
                desc.add(CHAN_CUSTOM_COLOR, LXsTYPE_COLOR1);
                desc.vector_type(LXsVECTYPE_RGB);
                LXtVector color;
                LXx_VSET(color, 0.6);
                desc.default_val(color);
                desc.chan_set_custom(new CCustomColorEnable);
                desc.chan_add_dependency(CHAN_COLOR_SOURCE);
                
                desc.add(CHAN_RING_X_SEGMENTS, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(32);
                desc.default_val(32);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_Y_SEGMENTS, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(32);
                desc.default_val(32);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_Z_SEGMENTS, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(32);
                desc.default_val(32);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_X_SEGMENT_OFFSET, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(31);
                desc.default_val(0);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_Y_SEGMENT_OFFSET, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(31);
                desc.default_val(0);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_Z_SEGMENT_OFFSET, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.set_max(31);
                desc.default_val(0);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RING_RADIUS, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.5);
                desc.chan_set_custom(new CRingSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_X_WIDTH, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_X_HEIGHT, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_Y_WIDTH, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_Y_HEIGHT, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_Z_WIDTH, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_RECTANGLE_Z_HEIGHT, LXsTYPE_DISTANCE);
                desc.default_val(1.0);
                desc.chan_set_custom(new CRectangleSpecificEnable);
                desc.chan_add_dependency(CHAN_SHAPE);
                
                desc.add(CHAN_OFFSET, LXsTYPE_DISTANCE);
                desc.vector_type(LXsVECTYPE_XYZ);
                LXtVector offset;
                LXx_VSET(offset, 0.0);
                desc.default_val(offset);
                
                desc.add(CHAN_OPACITY, LXsTYPE_PERCENT);
                desc.default_val(1.0);
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (ITEM_SHAPE_PKG_NAME);

        class CViewItem3D :
        public CLxViewItem3D
        {
        public:
            CViewItem3D() :
            _numPoints(32)
            {
                _calculateCirclePoints();
                _setSquareVertices();
            }

            /*
             * draw() is called to allow the item to draw itself in 3D.
             *
             * We read the channels for this item into a local CChannel (which would
             * be needed if the channels affected the drawing).
             */
            void
            draw (
                  CLxUser_Item &item,
                  CLxUser_ChannelRead &chan,
                  CLxUser_StrokeDraw &stroke,
                  int selFlags,
                  const CLxVector &wireColor) OVERRIDE_MACRO
            {
                //CLxUser_View3DportService viewService;
                //CLxUser_View3D view(stroke);
                CChannels channels;
                channels_meta->chan_read (chan, item, &channels);
   
                int enable = chan.IValue(item, CHAN_ENABLE);
                if (enable == 0) {
                    return;
                }

                //int mx, my;
                //viewService.Mouse(&mx, &my);
                //void** hitList;
                //int hitCount = view.HitElement(LXi_VPHIT_ITEM, mx, my, hitList);
                
                // Color
                int colorType = chan.IValue(item, CHAN_COLOR_SOURCE);
                CLxVector color(0.6, 0.6, 0.6);
                
                bool useWire = (selFlags & LXiSELECTION_SELECTED) ? true : false;
                if (useWire) { colorType = 0; }
                
                switch (colorType) {
                    case 0: // wire
                    {
                        color = wireColor;
                        break;
                    }
                    case 1: // fill
                    {
                        if (LXe_TRUE == item.PackageTest("glDraw"))
                        {
                            color.v[0] = chan.FValue(item, "fillColor.R");
                            color.v[1] = chan.FValue(item, "fillColor.G");
                            color.v[2] = chan.FValue(item, "fillColor.B");
                        }
                        else
                        {
                            color = wireColor;
                        }
                        break;
                    }
                    case 2: // custom
                    {
                        color.v[0] = chan.FValue(item, CHAN_CUSTOM_COLOR_R);
                        color.v[1] = chan.FValue(item, CHAN_CUSTOM_COLOR_G);
                        color.v[2] = chan.FValue(item, CHAN_CUSTOM_COLOR_B);
                        break;
                    }
                    default:
                        break;
                }

                ShapeDrawData shapeDraw;
                shapeDraw.shape = chan.IValue(item, CHAN_SHAPE);
                shapeDraw.width = chan.FValue(item, CHAN_SHAPE_WIDTH);
                shapeDraw.ringRadius = chan.FValue(item, CHAN_RING_RADIUS);
                shapeDraw.thickness = chan.FValue(item, CHAN_SHAPE_THICKNESS);
                shapeDraw.opacity = chan.FValue(item, CHAN_OPACITY);
                shapeDraw.wireColor = color;
                shapeDraw.fillColor = color;
                shapeDraw.offset = CLxVector(0.0, 0.0, 0.0);
                shapeDraw.offset.v[0] = chan.FValue(item, CHAN_OFFSET_X);
                shapeDraw.offset.v[1] = chan.FValue(item, CHAN_OFFSET_Y);
                shapeDraw.offset.v[2] = chan.FValue(item, CHAN_OFFSET_Z);
                
                bool drawX = (bool)chan.IValue(item, CHAN_SHAPE_X_AXIS);
                if (drawX) {
                    shapeDraw.axis = 0; //
                    shapeDraw.ringSegmentsCount = chan.IValue(item, CHAN_RING_X_SEGMENTS);
                    shapeDraw.ringSegmentOffset = chan.IValue(item, CHAN_RING_X_SEGMENT_OFFSET);
                    shapeDraw.rectWidth = chan.FValue(item, CHAN_RECTANGLE_X_WIDTH);
                    shapeDraw.rectHeight = chan.FValue(item, CHAN_RECTANGLE_X_HEIGHT);
                    _drawShape(shapeDraw, item, chan, stroke, selFlags);
                }
                
                bool drawY = (bool)chan.IValue(item, CHAN_SHAPE_Y_AXIS);
                if (drawY) {
                    shapeDraw.axis = 1; //
                    shapeDraw.ringSegmentsCount = chan.IValue(item, CHAN_RING_Y_SEGMENTS);
                    shapeDraw.ringSegmentOffset = chan.IValue(item, CHAN_RING_Y_SEGMENT_OFFSET);
                    shapeDraw.rectWidth = chan.FValue(item, CHAN_RECTANGLE_Y_WIDTH);
                    shapeDraw.rectHeight = chan.FValue(item, CHAN_RECTANGLE_Y_HEIGHT);
                    _drawShape(shapeDraw, item, chan, stroke, selFlags);
                }
                
                bool drawZ = (bool)chan.IValue(item, CHAN_SHAPE_Z_AXIS);
                if (drawZ) {
                    shapeDraw.axis = 2; //
                    shapeDraw.ringSegmentsCount = chan.IValue(item, CHAN_RING_Z_SEGMENTS);
                    shapeDraw.ringSegmentOffset = chan.IValue(item, CHAN_RING_Z_SEGMENT_OFFSET);
                    shapeDraw.rectWidth = chan.FValue(item, CHAN_RECTANGLE_Z_WIDTH);
                    shapeDraw.rectHeight = chan.FValue(item, CHAN_RECTANGLE_Z_HEIGHT);
                    _drawShape(shapeDraw, item, chan, stroke, selFlags);
                }
            }
        
        private:
            int _numPoints; // number of vertices in a circle shape representing socket in viewport
            std::vector<CLxVector> _circlePoints;
            SquareVerts _squareVerts;
            
            /*
             * Calculates all the points for the circle shape
             * that will represent socket in viewport.
             * The circle is defined in XZ plane.
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
                    CLxVector circlePoint(x, 0.0, y);
                    _circlePoints.push_back(circlePoint);
                }
                _circlePoints.push_back(CLxVector(1.0, 0.0, 0.0)); // add extra point to make a loop
            }

            /*
             * Fill in default points for a square.
             * We define the square in XZ plane.
             */
            void _setSquareVertices()
            {
                _squareVerts.out1 = CLxVector(-0.5, 0.0, 0.5);
                _squareVerts.in1 = _squareVerts.out1;
                _squareVerts.out2 = CLxVector(0.5, 0.0, 0.5);
                _squareVerts.in2 = _squareVerts.out2;
                _squareVerts.out3 = CLxVector(0.5, 0.0, -0.5);
                _squareVerts.in3 = _squareVerts.out3;
                _squareVerts.out4 = CLxVector(-0.5, 0.0, -0.5);
                _squareVerts.in4 = _squareVerts.out4;
            }
            
            void _drawShape(
            	ShapeDrawData &drawData,
                CLxUser_Item &item,
                CLxUser_ChannelRead &chan,
                CLxUser_StrokeDraw &stroke,
                int selFlags)
            {
                switch (drawData.shape) {
                    case 0: // ring
                    {
                        _drawRing(drawData, stroke);
                        break;
                    }
                    case 1: // square
                    {
                        _drawSquare(drawData, stroke);
                        break;
                    }
                    default:
                        break;
                }
            }
            
            /*
             * Draws a ring shape.
             */
            void _drawRing(
            	ShapeDrawData &drawData,
                CLxUser_StrokeDraw &stroke)
            {
                
                // Calculate all points that will actually be drawn
                std::vector<CLxVector> pointsToDrawInner;
                std::vector<CLxVector> pointsToDrawOuter;
                
                std::vector<CLxVector> pointsToDrawInner2;
                std::vector<CLxVector> pointsToDrawOuter2;
                
                double thickMax = drawData.thickness * 0.5;
                double thickMin = drawData.thickness * -0.5;
                
                for(int i = 0; i < _circlePoints.size(); i++)
                {
                    CLxVector pv = _circlePoints[i] * drawData.ringRadius;
                    CLxVector pvi = pv - (_circlePoints[i] * drawData.width);
                    
                    pv.v[1] = thickMax;
                    pointsToDrawOuter.push_back(pv);
                    
                    pvi.v[1] = thickMax;
                    pointsToDrawInner.push_back(pvi);
                    
                    pv.v[1] = thickMin;
                    pointsToDrawOuter2.push_back(pv);
                    
                    pvi.v[1] = thickMin;
                    pointsToDrawInner2.push_back(pvi);
                }

                int offset = drawData.ringSegmentOffset;
                int segmentCount = drawData.ringSegmentsCount;
                int x = offset;
                
                std::vector<int> circlePointIndexes;
                for (int i = 0; i < segmentCount; i++)
                {
                    circlePointIndexes.push_back(x);
                    x++;
                    if (x > 31) { x = 0; }
                }
                
                stroke.Begin(LXiSTROKE_QUADS, drawData.fillColor, drawData.opacity);
                
                int a = 0, b = 1, c = 2;
                switch (drawData.axis) {
                    case 0: // x
                    {
                        a = 1;
                        b = 0;
                        c = 2;
                        break;
                    }
                    case 1: // y
                    {
                        a = 0;
                        b = 1;
                        c = 2;
                        break;
                    }
                    case 2: // z
                    {
                        a = 0;
                        b = 2;
                        c = 1;
                        break;
                    }
                    default:
                        break;
                }
                
                for(int x = 0; x < circlePointIndexes.size(); x++)
                {
                    int i = circlePointIndexes[x];
                    CLxVector v1 = CLxVector(pointsToDrawInner[i].v[a], pointsToDrawInner[i].v[b], pointsToDrawInner[i].v[c]) + drawData.offset;
                    CLxVector v2 = CLxVector(pointsToDrawOuter[i].v[a], pointsToDrawOuter[i].v[b], pointsToDrawOuter[i].v[c]) + drawData.offset;
                    CLxVector v3 = CLxVector(pointsToDrawOuter[i+1].v[a], pointsToDrawOuter[i+1].v[b], pointsToDrawOuter[i+1].v[c]) + drawData.offset;
                	CLxVector v4 = CLxVector(pointsToDrawInner[i+1].v[a], pointsToDrawInner[i+1].v[b], pointsToDrawInner[i+1].v[c]) + drawData.offset;

                    stroke.Vertex (v1, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (v2, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (v3, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (v4, LXiSTROKE_ABSOLUTE);
                }

                if (drawData.thickness > 0.001)
                {
                    for(int x = 0; x < circlePointIndexes.size(); x++)
                    {
                        int i = circlePointIndexes[x];
                        CLxVector v1 = CLxVector(pointsToDrawInner2[i].v[a], pointsToDrawInner2[i].v[b], pointsToDrawInner2[i].v[c]) + drawData.offset;
                        CLxVector v2 = CLxVector(pointsToDrawOuter2[i].v[a], pointsToDrawOuter2[i].v[b], pointsToDrawOuter2[i].v[c]) + drawData.offset;
                        CLxVector v3 = CLxVector(pointsToDrawOuter2[i+1].v[a], pointsToDrawOuter2[i+1].v[b], pointsToDrawOuter2[i+1].v[c]) + drawData.offset;
                        CLxVector v4 = CLxVector(pointsToDrawInner2[i+1].v[a], pointsToDrawInner2[i+1].v[b], pointsToDrawInner2[i+1].v[c]) + drawData.offset;
                        
                        stroke.Vertex (v1, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v2, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v3, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v4, LXiSTROKE_ABSOLUTE);
                    }
                    
                    for(int x = 0; x < circlePointIndexes.size(); x++)
                    {
                        int i = circlePointIndexes[x];
                        CLxVector v1 = CLxVector(pointsToDrawOuter[i].v[a], pointsToDrawOuter[i].v[b], pointsToDrawOuter[i].v[c]) + drawData.offset;
                        CLxVector v2 = CLxVector(pointsToDrawOuter2[i].v[a], pointsToDrawOuter2[i].v[b], pointsToDrawOuter2[i].v[c]) + drawData.offset;
                        CLxVector v3 = CLxVector(pointsToDrawOuter2[i+1].v[a], pointsToDrawOuter2[i+1].v[b], pointsToDrawOuter2[i+1].v[c]) + drawData.offset;
                        CLxVector v4 = CLxVector(pointsToDrawOuter[i+1].v[a], pointsToDrawOuter[i+1].v[b], pointsToDrawOuter[i+1].v[c]) + drawData.offset;

                        stroke.Vertex (v1, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v2, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v3, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (v4, LXiSTROKE_ABSOLUTE);
                    }
                }

            }
            
            /*
             * Draws a square shape.
             */
            void _drawSquare(
            	ShapeDrawData &drawData,
                CLxUser_StrokeDraw &stroke)
            {

                // Set indexes for axes.
                int a = 0, b = 1, c = 2;
                switch (drawData.axis) {
                    case 0: // x
                    {
                        a = 1;
                        b = 0;
                        c = 2;
                        break;
                    }
                    case 1: // y
                    {
                        a = 0;
                        b = 1;
                        c = 2;
                        break;
                    }
                    case 2: // z
                    {
                        a = 0;
                        b = 2;
                        c = 1;
                        break;
                    }
                    default:
                        break;
                }
                
                double outerWidth = drawData.rectWidth;
                double innerWidth = outerWidth - (drawData.width * 2.0);
          
                double outerHeight = drawData.rectHeight;
                double innerHeight = outerHeight - (drawData.width * 2.0);
                
                SquareVerts square;
                square.out1 = _squareVerts.out1;
                square.out1[0] *= outerWidth;
                square.out1[2] *= outerHeight;
                
                square.out2 = _squareVerts.out2;
                square.out2[0] *= outerWidth;
                square.out2[2] *= outerHeight;
                
                square.out3 = _squareVerts.out3;
                square.out3[0] *= outerWidth;
                square.out3[2] *= outerHeight;
                
                square.out4 = _squareVerts.out4;
                square.out4[0] *= outerWidth;
                square.out4[2] *= outerHeight;
                
                square.in1 = _squareVerts.in1;
                square.in1[0] *= innerWidth;
                square.in1[2] *= innerHeight;
                
                square.in2 = _squareVerts.in2;
                square.in2[0] *= innerWidth;
                square.in2[2] *= innerHeight;
                
                square.in3 = _squareVerts.in3;
                square.in3[0] *= innerWidth;
                square.in3[2] *= innerHeight;
                
                square.in4 = _squareVerts.in4;
                square.in4[0] *= innerWidth;
                square.in4[2] *= innerHeight;
                
                // thickness
                double thicknessOffset = drawData.thickness * 0.5;
                square.out1.v[1] = thicknessOffset;
                square.out2.v[1] = thicknessOffset;
                square.out3.v[1] = thicknessOffset;
                square.out4.v[1] = thicknessOffset;

                square.in1.v[1] = thicknessOffset;
                square.in2.v[1] = thicknessOffset;
                square.in3.v[1] = thicknessOffset;
                square.in4.v[1] = thicknessOffset;
                
                // Initially prepare 2nd square.
                // It will be used only when thickness is > 0.
                SquareVerts square2 = square;
                
                // thickness
                square2.out1.v[1] *= -1.0;
                square2.out2.v[1] *= -1.0;
                square2.out3.v[1] *= -1.0;
                square2.out4.v[1] *= -1.0;
                
                square2.in1.v[1] *= -1.0;
                square2.in2.v[1] *= -1.0;
                square2.in3.v[1] *= -1.0;
                square2.in4.v[1] *= -1.0;
                
                // Prepare quads
                std::vector<QuadVerts> quads;
                QuadVerts q;
                q.a = square.in1;
                q.b = square.out1;
                q.c = square.out2;
                q.d = square.in2;
                quads.push_back(q);
                q.a = square.in2;
                q.b = square.out2;
                q.c = square.out3;
                q.d = square.in3;
                quads.push_back(q);
                q.a = square.in3;
                q.b = square.out3;
                q.c = square.out4;
                q.d = square.in4;
                quads.push_back(q);
                q.a = square.in4;
                q.b = square.out4;
                q.c = square.out1;
                q.d = square.in1;
                quads.push_back(q);
                
                // Add more quads when thickness is set.
                if (drawData.thickness > 0.0001)
                {
                    q.a = square2.in1;
                    q.b = square2.out1;
                    q.c = square2.out2;
                    q.d = square2.in2;
                    quads.push_back(q);
                    q.a = square2.in2;
                    q.b = square2.out2;
                    q.c = square2.out3;
                    q.d = square2.in3;
                    quads.push_back(q);
                    q.a = square2.in3;
                    q.b = square2.out3;
                    q.c = square2.out4;
                    q.d = square2.in4;
                    quads.push_back(q);
                    q.a = square2.in4;
                    q.b = square2.out4;
                    q.c = square2.out1;
                    q.d = square2.in1;
                    quads.push_back(q);
                    
                    // Outer quads
                    q.a = square.out1;
                    q.b = square2.out1;
                    q.c = square2.out2;
                    q.d = square.out2;
                    quads.push_back(q);
                    
                    q.a = square.out2;
                    q.b = square2.out2;
                    q.c = square2.out3;
                    q.d = square.out3;
                    quads.push_back(q);
                    
                    q.a = square.out3;
                    q.b = square2.out3;
                    q.c = square2.out4;
                    q.d = square.out4;
                    quads.push_back(q);
                    
                    q.a = square.out4;
                    q.b = square2.out4;
                    q.c = square2.out1;
                    q.d = square.out1;
                    quads.push_back(q);
                }
                
                stroke.Begin(LXiSTROKE_QUADS, drawData.fillColor, drawData.opacity);

                for (int i = 0; i < quads.size(); i++)
                {                    
                    CLxVector q1(quads[i].a.v[a], quads[i].a.v[b], quads[i].a.v[c]);
                    q1 += drawData.offset;
  
                    CLxVector q2(quads[i].b.v[a], quads[i].b.v[b], quads[i].b.v[c]);
                    q2 += drawData.offset;
                    
                    CLxVector q3(quads[i].c.v[a], quads[i].c.v[b], quads[i].c.v[c]);
                    q3 += drawData.offset;
                    
                    CLxVector q4(quads[i].d.v[a], quads[i].d.v[b], quads[i].d.v[c]);
                    q4 += drawData.offset;
                    
                    stroke.Vertex (q1.v, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (q2.v, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (q3.v, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (q4.v, LXiSTROKE_ABSOLUTE);
                }
            }

            void _invertMatrix(CLxUser_Matrix mat, CLxUser_Value &val, CLxUser_Matrix &invMat)
            {
                CLxUser_ValueService _valService;
                // Invert mesh world transform matrix.
                LXtMatrix4 mat4;
                mat.Get4(mat4);
                _valService.NewValue(val, LXsTYPE_MATRIX4);
                
                invMat.set(val);
                invMat.Set4 (mat4);
                invMat.Invert();
            }
            
            CLxUser_ValueService _valService;
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
    }
    
} // end rs namespace
