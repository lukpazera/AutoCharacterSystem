
// This define is crucial to get M_PI constant on Windows correctly.
// Just including math.h won't cut it.
#define _USE_MATH_DEFINES

#include <map>

#include <lx_vp.hpp>
#include <lxu_package.hpp>
#include <lxu_attrdesc.hpp>
#include <lxu_matrix.hpp>
#include <lxidef.h>
#include <math.h>

#include "constants.hpp"

#define ITEM_AXIS_SOURCE_GRAPH "rs.itemAxisSource"

namespace {
    const char* ITEM_AXIS_PKG_NAME = "rs.pkg.itemAxis";
};

namespace rs {
    namespace itemAxisPackage {
        
        static const char* CHAN_ENABLE = "rsiaEnable";
        
        static const char* CHAN_POINTER_SHAPE = "rsiaShape";
        static const char* CHAN_DRAW_LINE = "rsiaLine";
        static const char* CHAN_ARROWHEAD_SHAPE = "rsiaArrowhead";
        
        static const char* CHAN_POINTER_X_AXIS = "rsiaXAxis";
        static const char* CHAN_POINTER_Y_AXIS = "rsiaYAxis";
        static const char* CHAN_POINTER_Z_AXIS = "rsiaZAxis";
        
        static const char* CHAN_THICKNESS = "rsiaThickness";
        
        static const char* CHAN_WIDTH = "rsiaWidth"; // width of arrowheads
        static const char* CHAN_HEIGHT = "rsiaHeight"; // height of arrowheads
        
        static const char* CHAN_LENGTH = "rsiaLength"; // length of the line.
        
        static const char* CHAN_OFFSET = "rsiaOffset";
        static const char* CHAN_OFFSET_X = "rsiaOffset.X";
        static const char* CHAN_OFFSET_Y = "rsiaOffset.Y";
        static const char* CHAN_OFFSET_Z = "rsiaOffset.Z";
      
        static const char* CHAN_SHIFT_X = "rsiaShiftX";
        static const char* CHAN_SHIFT_Y = "rsiaShiftY";
        static const char* CHAN_SHIFT_Z = "rsiaShiftZ";
        
		static const char* CHAN_NEGATIVE_AXIS_X = "rsiaNegativeAxisX";
		static const char* CHAN_NEGATIVE_AXIS_Y = "rsiaNegativeAxisY";
		static const char* CHAN_NEGATIVE_AXIS_Z = "rsiaNegativeAxisZ";

        static const char* CHAN_COLOR_SOURCE = "rsiaColorSource";

        static const char* CHAN_CUSTOM_COLOR_X = "rsiaXCustomColor";
        static const char* CHAN_CUSTOM_COLOR_X_R = "rsiaXCustomColor.R";
        static const char* CHAN_CUSTOM_COLOR_X_G = "rsiaXCustomColor.G";
        static const char* CHAN_CUSTOM_COLOR_X_B = "rsiaXCustomColor.B";
        
        static const char* CHAN_CUSTOM_COLOR_Y = "rsiaYCustomColor";
        static const char* CHAN_CUSTOM_COLOR_Y_R = "rsiaYCustomColor.R";
        static const char* CHAN_CUSTOM_COLOR_Y_G = "rsiaYCustomColor.G";
        static const char* CHAN_CUSTOM_COLOR_Y_B = "rsiaYCustomColor.B";
        
        static const char* CHAN_CUSTOM_COLOR_Z = "rsiaZCustomColor";
        static const char* CHAN_CUSTOM_COLOR_Z_R = "rsiaZCustomColor.R";
        static const char* CHAN_CUSTOM_COLOR_Z_G = "rsiaZCustomColor.G";
        static const char* CHAN_CUSTOM_COLOR_Z_B = "rsiaZCustomColor.B";
        
        static const char* CHAN_OPACITY = "rsiaOpacity";

        static LXtTextValueHint arrowheadHints[] = {
            0, "none",
            1, "flat",
            2, "solid",
            -1, NULL
        };

        static LXtTextValueHint colorSourceHints[] = {
            0, "wire",
            1, "fill",
            2, "custom",
            -1, NULL
        };
        
        static const char* axisChannels[] = { CHAN_POINTER_X_AXIS, CHAN_POINTER_Y_AXIS, CHAN_POINTER_Z_AXIS };
        
        struct PointerDrawData {
            int axis;
			bool negativeAxis;
            int drawLine;
            int arrowheadShape;
            double width;
            double height;
            double length;
            int thickness;
            double opacity;
            CLxVector offset;
            CLxVector shift;
            CLxMatrix4 spaceTransform; // This is used to draw axis of another item in the drawn item space.
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
            CCustomColorEnable(int axis) { _axis = axis; }
            
            bool enabled(CLxUser_Item &item, CLxUser_ChannelRead &read, CLxUser_Message &msg) OVERRIDE_MACRO
            {
                if (read.IValue(item, CHAN_COLOR_SOURCE) != 2) { return false; }// 2 is custom color

                if (read.IValue(item, axisChannels[_axis]) == 1) // true really
                {
                    return true;
                }

                return false;
            }
        
        private:
            int _axis;
        };

        class CAxisEnable : public CLxCustomChannelUI
        {
        public:
            CAxisEnable(int axis) { _axis = axis; }
            
            bool enabled(CLxUser_Item &item, CLxUser_ChannelRead &read, CLxUser_Message &msg) OVERRIDE_MACRO
            {
                if (read.IValue(item, axisChannels[_axis]) == 1) // true really
                {
                    return true;
                }
                return false;
            }
            
        private:
            int _axis;
        };
        
        class CChannels : public CLxChannels
        {
        public:

            void init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_ENABLE, LXsTYPE_BOOLEAN);
                desc.default_val(1);
  
                desc.add(CHAN_DRAW_LINE, LXsTYPE_BOOLEAN);
                desc.default_val(1);
                
                desc.add(CHAN_ARROWHEAD_SHAPE, LXsTYPE_INTEGER);
                desc.set_hint(arrowheadHints);
                desc.default_val(2);
                
                desc.add(CHAN_POINTER_X_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(false);
 
                desc.add(CHAN_POINTER_Y_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(true);
                
                desc.add(CHAN_POINTER_Z_AXIS, LXsTYPE_BOOLEAN);
                desc.default_val(false);
                
				desc.add(CHAN_NEGATIVE_AXIS_X, LXsTYPE_BOOLEAN);
				desc.default_val(false);
				desc.chan_set_custom(new CAxisEnable(0));
				desc.chan_add_dependency(CHAN_POINTER_X_AXIS);

				desc.add(CHAN_NEGATIVE_AXIS_Y, LXsTYPE_BOOLEAN);
				desc.default_val(false);
				desc.chan_set_custom(new CAxisEnable(1));
				desc.chan_add_dependency(CHAN_POINTER_Y_AXIS);

				desc.add(CHAN_NEGATIVE_AXIS_Z, LXsTYPE_BOOLEAN);
				desc.default_val(false);
				desc.chan_set_custom(new CAxisEnable(2));
				desc.chan_add_dependency(CHAN_POINTER_Z_AXIS);

                desc.add(CHAN_WIDTH, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.01);
 
                desc.add(CHAN_HEIGHT, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.01);
                
                desc.add(CHAN_LENGTH, LXsTYPE_DISTANCE);
                desc.set_min(0.0);
                desc.default_val(0.1);

                desc.add(CHAN_THICKNESS, LXsTYPE_INTEGER);
                desc.set_min(0);
                desc.default_val(2);

                desc.add(CHAN_OFFSET, LXsTYPE_DISTANCE);
                desc.vector_type(LXsVECTYPE_XYZ);
                LXtVector offset;
                LXx_VSET(offset, 0.0);
                desc.default_val(offset);

				desc.default_val(offset);
                desc.add(CHAN_SHIFT_X, LXsTYPE_DISTANCE);
                desc.default_val(0.0);
                desc.chan_set_custom(new CAxisEnable(0));
                desc.chan_add_dependency(CHAN_POINTER_X_AXIS);
 
                desc.add(CHAN_SHIFT_Y, LXsTYPE_DISTANCE);
                desc.default_val(0.0);
                desc.chan_set_custom(new CAxisEnable(1));
                desc.chan_add_dependency(CHAN_POINTER_Y_AXIS);
                
                desc.add(CHAN_SHIFT_Z, LXsTYPE_DISTANCE);
                desc.default_val(0.0);
                desc.chan_set_custom(new CAxisEnable(2));
                desc.chan_add_dependency(CHAN_POINTER_Z_AXIS);
                
                desc.add(CHAN_COLOR_SOURCE, LXsTYPE_INTEGER);
                desc.set_hint(colorSourceHints);
                desc.default_val(1);
  
                LXtVector color;
                
                desc.add(CHAN_CUSTOM_COLOR_X, LXsTYPE_COLOR1);
                desc.vector_type(LXsVECTYPE_RGB);
                LXx_VSET3(color, 1.0, 0.0, 0.0);
                desc.default_val(color);
                desc.chan_set_custom(new CCustomColorEnable(0));
                desc.chan_add_dependency(CHAN_COLOR_SOURCE);
                desc.chan_add_dependency(CHAN_POINTER_X_AXIS);
   
                desc.add(CHAN_CUSTOM_COLOR_Y, LXsTYPE_COLOR1);
                desc.vector_type(LXsVECTYPE_RGB);
                LXx_VSET3(color, 0.0, 1.0, 0.0);
                desc.default_val(color);
                desc.chan_set_custom(new CCustomColorEnable(1));
                desc.chan_add_dependency(CHAN_COLOR_SOURCE);
                desc.chan_add_dependency(CHAN_POINTER_Y_AXIS);
                
                desc.add(CHAN_CUSTOM_COLOR_Z, LXsTYPE_COLOR1);
                desc.vector_type(LXsVECTYPE_RGB);
                LXx_VSET3(color, 0.0, 0.0, 1.0);
                desc.default_val(color);
                desc.chan_set_custom(new CCustomColorEnable(2));
                desc.chan_add_dependency(CHAN_COLOR_SOURCE);
                desc.chan_add_dependency(CHAN_POINTER_Z_AXIS);
                
                desc.add(CHAN_OPACITY, LXsTYPE_PERCENT);
                desc.set_min(0.0);
                desc.set_max(1.0);
                desc.default_val(1.0);
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (ITEM_AXIS_PKG_NAME);

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
                CChannels channels;
                channels_meta->chan_read (chan, item, &channels);
   
                int enable = chan.IValue(item, CHAN_ENABLE);
                if (enable == 0) {
                    return;
                }
                
                // Need to determine where the orientiation for drawing axes
                // weill be coming from.
                // By default it comes from the item itself but if there's
                // a link on the source item graph then we use the custom
                // item orientation instead.
                
                // For custom item we have to create a transform matrix that
                // will be used to shift drawing from item space to
                // the custom item space.
                CLxUser_ItemGraph itemLinkGraph;
                CLxUser_Scene scene;
                CLxMatrix4 spaceTransform;
                item.Context(scene);
                scene.GraphLookup(ITEM_AXIS_SOURCE_GRAPH, itemLinkGraph);
                unsigned links = itemLinkGraph.Forward(item);
                if (0 < links)
                {
                    CLxUser_Item sourceItem;
                    itemLinkGraph.Forward(item, 0, sourceItem);
                    
                    CLxUser_Matrix itemXfrmRaw, sourceXfrmRaw;
                    chan.Object(item, "wrotMatrix", itemXfrmRaw);
                    chan.Object(sourceItem, "wrotMatrix",sourceXfrmRaw);
                    
                    CLxMatrix4 itemWRotMtx(itemXfrmRaw);
                    CLxMatrix4 sourceWRotMtx(sourceXfrmRaw);
                    CLxMatrix4 itemInverseWRotMtx(itemWRotMtx.inverse());
                    spaceTransform = sourceWRotMtx;
                    spaceTransform *= itemInverseWRotMtx;
                }
                
                CLxVector color(wireColor);
                
                PointerDrawData pointerDraw;
                pointerDraw.drawLine = chan.IValue(item, CHAN_DRAW_LINE);
                pointerDraw.arrowheadShape = chan.IValue(item, CHAN_ARROWHEAD_SHAPE);
                pointerDraw.length = chan.FValue(item, CHAN_LENGTH);
                pointerDraw.width = chan.FValue(item, CHAN_WIDTH);
                pointerDraw.height = chan.FValue(item, CHAN_HEIGHT);
                pointerDraw.thickness = chan.IValue(item, CHAN_THICKNESS);
                pointerDraw.opacity = chan.FValue(item, CHAN_OPACITY);

                pointerDraw.offset.v[0] = chan.FValue(item, CHAN_OFFSET_X);
                pointerDraw.offset.v[1] = chan.FValue(item, CHAN_OFFSET_Y);
                pointerDraw.offset.v[2] = chan.FValue(item, CHAN_OFFSET_Z);
 
                pointerDraw.shift.v[0] = chan.FValue(item, CHAN_SHIFT_X);
                pointerDraw.shift.v[1] = chan.FValue(item, CHAN_SHIFT_Y);
                pointerDraw.shift.v[2] = chan.FValue(item, CHAN_SHIFT_Z);
                
                pointerDraw.spaceTransform = spaceTransform;
                
                if (chan.IValue(item, CHAN_POINTER_X_AXIS))
                {
                    pointerDraw.axis = 0;
					pointerDraw.negativeAxis = chan.IValue(item, CHAN_NEGATIVE_AXIS_X);
                	_drawPointer(pointerDraw, item, chan, stroke, selFlags, color);
                }
                
                if (chan.IValue(item, CHAN_POINTER_Y_AXIS))
                {
                    pointerDraw.axis = 1;
					pointerDraw.negativeAxis = chan.IValue(item, CHAN_NEGATIVE_AXIS_Y);
                    _drawPointer(pointerDraw, item, chan, stroke, selFlags, color);
                }
                
                if (chan.IValue(item, CHAN_POINTER_Z_AXIS))
                {
                    pointerDraw.axis = 2;
					pointerDraw.negativeAxis = chan.IValue(item, CHAN_NEGATIVE_AXIS_Z);
                    _drawPointer(pointerDraw, item, chan, stroke, selFlags, color);
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
            
            /*
             * Draws a pointer.
             */
            void _drawPointer(
            	PointerDrawData &drawData,
          		CLxUser_Item &item,
          		CLxUser_ChannelRead &chan,
          		CLxUser_StrokeDraw &stroke,
          		int selFlags,
          		const CLxVector &wireColor)
            {

                // Axes
                int up, side, in;
                
                switch (drawData.axis) {
                    case 0: // x
                        up = 0; // x is up
                        side = 2; // y is side
                        in = 1; // z is in
                        break;
                        
                    case 1: // y
                    {
                        up = 1; // y is up
                        side = 0; // x is side
                        in = 2; // z is in
                        
                        break;
                    }
                        
                    case 2: // z
                    {
                        up = 2; // x is up
                        side = 0; // y is side
                        in = 1; // z is in
                        break;
                    }
                        
                    default:
                        // same as X
                        up = 0;
                        side = 2;
                        in = 1;
                        break;
                }
                
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
                        if (drawData.axis == 0) {
                            color.v[0] = chan.FValue(item, CHAN_CUSTOM_COLOR_X_R);
                            color.v[1] = chan.FValue(item, CHAN_CUSTOM_COLOR_X_G);
                            color.v[2] = chan.FValue(item, CHAN_CUSTOM_COLOR_X_B);
                        }
                        else if (drawData.axis == 1) {
                            color.v[0] = chan.FValue(item, CHAN_CUSTOM_COLOR_Y_R);
                            color.v[1] = chan.FValue(item, CHAN_CUSTOM_COLOR_Y_G);
                            color.v[2] = chan.FValue(item, CHAN_CUSTOM_COLOR_Y_B);
                        }
                        else {
                            color.v[0] = chan.FValue(item, CHAN_CUSTOM_COLOR_Z_R);
                            color.v[1] = chan.FValue(item, CHAN_CUSTOM_COLOR_Z_G);
                            color.v[2] = chan.FValue(item, CHAN_CUSTOM_COLOR_Z_B);
                        }
                        break;
                    }
                    default:
                        break;
                }
				// End color
                
                // Draw the line
                if (drawData.drawLine)
                {
                    CLxVector origin(drawData.offset);
                    CLxVector vec(0.0, 0.0, 0.0);
                    vec[drawData.axis] = drawData.length;

                    vec += drawData.offset;
                    
                    origin[up] += drawData.shift[up];
                    vec[up] += drawData.shift[up];

                    // Transform space if custom item is used for orientation
                    origin *= drawData.spaceTransform;
                    vec *= drawData.spaceTransform;
                    
					if (drawData.negativeAxis)
					{
						origin *= -1.0;
						vec *= -1.0;
					}

                    stroke.BeginWD (LXiSTROKE_LINES, color, drawData.opacity, drawData.thickness, 0);
                    stroke.Vertex (origin.v, LXiSTROKE_ABSOLUTE);
                    stroke.Vertex (vec.v, LXiSTROKE_ABSOLUTE);
                }
                
                switch (drawData.arrowheadShape) {

                    case 1: // Flat arrowhead
                    {
                        CLxVector pointSide1, pointSide2, pointTip;
                        
                        pointTip[up] = drawData.length + drawData.height + drawData.shift[up];
                        pointSide1[side] = 0.5 * drawData.width;
                        pointSide1[up] = drawData.length + drawData.shift[up];
                        pointSide2[side] = -0.5 * drawData.width;
                        pointSide2[up] = drawData.length + drawData.shift[up];
                        
                        // Offset applied in local space
                        pointTip += drawData.offset;
                        pointSide1 += drawData.offset;
                        pointSide2 += drawData.offset;
                        
						// Flip vectors for negative axis drawing
						if (drawData.negativeAxis)
						{
							pointTip *= -1.0;
							pointSide1 *= -1.0;
							pointSide2 *= -1.0;
						}

                        // Transform space if custom item is used for orientation.
                        pointTip *= drawData.spaceTransform;
                        pointSide1 *= drawData.spaceTransform;
                        pointSide2 *= drawData.spaceTransform;
                        
                        stroke.BeginWD (LXiSTROKE_TRIANGLES, color, drawData.opacity, drawData.thickness, 0);
                        stroke.Vertex (pointSide1.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (pointSide2.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (pointTip.v, LXiSTROKE_ABSOLUTE);
                        break;
                    }
                    case 2: // Solid arrowhead
                    {
                        // Draw Arrow Triangles
                        CLxVector vert1, vert2, vert3;
                        CLxVector vert1b, vert2b, vert3b;
                        
                        // Min max coordinates for triangle points.
                        // min h - horizontal
                        // min v - vertical
                        double minH = drawData.width * -0.5;
                        double maxH = drawData.width * 0.5;
                        double minV = drawData.length; // - arrowLength;
                        double maxV = drawData.length + drawData.height;

                        // Arrow top vertex
                        vert2[up] = maxV + drawData.shift[up];
                        vert2[side] = 0.0;
                        vert2[in] = 0.0;
                        
                        // Left
                        vert1[up] = minV + drawData.shift[up];
                        vert1[side] = minH;
                        vert1[in] = 0.0;
                        
                        // Right
                        vert3[up] = minV + drawData.shift[up];
                        vert3[side] = maxH;
                        vert3[in] = 0.0;
                        
                        // Back
                        vert1b[up] = minV + drawData.shift[up];
                        vert1b[in] = minH;
                        vert1b[side] = 0.0;
                        
                        // Front
                        vert3b[up] = minV + drawData.shift[up];
                        vert3b[in] = maxH;
                        vert3b[side] = 0.0;
                        
                        vert2 += drawData.offset;
                        vert1 += drawData.offset;
                        vert3 += drawData.offset;
                        vert1b += drawData.offset;
                        vert3b += drawData.offset;
                        
						//
						if (drawData.negativeAxis)
						{
							vert1 *= -1.0;
							vert2 *= -1.0;
							vert3 *= -1.0;
							vert1b *= -1.0;
							vert3b *= -1.0;
						}

                        // Transform space if custom item is used for orientation.
                        vert1 *= drawData.spaceTransform;
                        vert2 *= drawData.spaceTransform;
                        vert3 *= drawData.spaceTransform;
                        vert1b *= drawData.spaceTransform;
                        vert3b *= drawData.spaceTransform;
                        
                        stroke.BeginWD (LXiSTROKE_TRIANGLES, color, drawData.opacity, drawData.thickness, 0);
                        
                        stroke.Vertex (vert1.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert2.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert3b.v, LXiSTROKE_ABSOLUTE);
                        
                        stroke.Vertex (vert3b.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert2.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert3.v, LXiSTROKE_ABSOLUTE);

                        stroke.Vertex (vert3.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert2.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert1b.v, LXiSTROKE_ABSOLUTE);

                        stroke.Vertex (vert1b.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert2.v, LXiSTROKE_ABSOLUTE);
                        stroke.Vertex (vert1.v, LXiSTROKE_ABSOLUTE);
                        
                        break;
                    }
                        
                    default:
                        break;
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
            package_meta.add_tag(LXsPKG_GRAPHS, ITEM_AXIS_SOURCE_GRAPH);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }
    
} // end rs namespace
