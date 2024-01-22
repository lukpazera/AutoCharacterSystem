
#include <lxu_meta.hpp>
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>
#include <lxu_vector.hpp>
#include <lxu_matrix.hpp>

#include "constants.hpp"
#include "mitem.hpp"
#include "listener.hpp"

static LXtID4 TAG_ID_METAGROUP = LXxID4('R','S','M','G');


namespace rs {
    namespace rootItem {
        
        static const char* CHAN_NAME = "rsName";
        static const char* CHAN_NAMING_SCHEME = "rsNamingScheme";
        static const char* CHAN_COLOR_SCHEME = "rsColorScheme";
        static const char* CHAN_META_RIG_TEMPLATE = "rsMetaRigTemplate"; // This needs to go, no meta rig templates.
		static const char* CHAN_SELECTED = "rsSelected";
        static const char* CHAN_DRAW_SELECTED = "rsDrawSelected";
        static const char* CHAN_ACCESS = "rsAccessLevel";
        static const char* CHAN_POSES_FOLDER = "rsPosesFolder";
        static const char* CHAN_ACTIONS_FOLDER = "rsActionsFolder";
		static const char* CHAN_REFERENCE_SIZE = "rsRefSize";
		static const char* CHAN_REFERENCE_SIZE_ALIGNMENT = "rsAlignRefSize";
		static const char* CHAN_DRAW_REFERENCE_SIZE = "rsDrawRefSize";
		static const char* CHAN_GAME_EXPORT_FOLDER = "rsGameExportFolder";
		static const char* CHAN_GAME_EXPORT_SET = "rsGameExportSet";

        static const char* GRAPHS = "rs.metaRig;rs.rigSetup;rs.deformStack;rs.bindMeshes;rs.editRig;rs.attach;rs.identifier";
		static const char* LOG_SYSTEM = "riggingsys";
        
        static LXtTextValueHint accessLevelHint[] = {
            0, "dev",
            1, "edit",
            2, "anim",
            -1, NULL
        };

		static LXtTextValueHint refSizeAlignHint[]{
			0, "vert",
			1, "horiz",
			-1, NULL
		};

        class CPackage : public CLxPackage
        {
        public:
            
            CPackage ()
            {
                listener.acquire();
            }

            ~CPackage ()
            {
                listener.release();
            }

            unsigned int counter = 0;
        };
        

        class CChannels : public CLxChannels
        {
        public:
            	void
            init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_NAME, LXsTYPE_STRING);
                desc.default_val("");

                desc.add(CHAN_NAMING_SCHEME, LXsTYPE_STRING);
                desc.default_val("");

                desc.add(CHAN_COLOR_SCHEME, LXsTYPE_STRING);
                desc.default_val("");

                desc.add(CHAN_META_RIG_TEMPLATE, LXsTYPE_STRING);
                desc.default_val("");

                desc.add(CHAN_SELECTED, LXsTYPE_BOOLEAN);
                desc.default_val(false);

                desc.add(CHAN_DRAW_SELECTED, LXsTYPE_BOOLEAN);
                desc.default_val(false);
                
                desc.add(CHAN_ACCESS, LXsTYPE_INTEGER);
                desc.hint(accessLevelHint);
                desc.default_val(0);

                desc.add(CHAN_POSES_FOLDER, LXsTYPE_STRING);
                desc.add(CHAN_ACTIONS_FOLDER, LXsTYPE_STRING);

				desc.add(CHAN_REFERENCE_SIZE, LXsTYPE_DISTANCE);
				desc.default_val(2.0);

				desc.add(CHAN_REFERENCE_SIZE_ALIGNMENT, LXsTYPE_INTEGER);
				desc.hint(refSizeAlignHint);
				desc.default_val(0);

				desc.add(CHAN_DRAW_REFERENCE_SIZE, LXsTYPE_BOOLEAN);
				desc.default_val(true);

				desc.add(CHAN_GAME_EXPORT_FOLDER, LXsTYPE_STRING);

				desc.add(CHAN_GAME_EXPORT_SET, LXsTYPE_STRING);
				desc.default_val("unity");
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (c::rigItemType::ROOT);

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
                //CLxUser_View view(stroke);
                CChannels rootChannels;
                
                channels_meta->chan_read(chan, item, &rootChannels);
                
                bool selected = (bool)chan.IValue(item, CHAN_SELECTED);
                bool drawSelected = (bool)chan.IValue(item, CHAN_DRAW_SELECTED);
				bool drawRefSize = (bool)chan.IValue(item, CHAN_DRAW_REFERENCE_SIZE);

				CLxUser_Scene scene;
				item.GetContext(scene);
				bool setupModeOn = (scene.SetupMode() == LXe_OK);

				if (drawRefSize && setupModeOn)
				{
					double refSize = chan.FValue(item, CHAN_REFERENCE_SIZE);
					double align = chan.IValue(item, CHAN_REFERENCE_SIZE_ALIGNMENT);
					CLxVector refColor(.8, .2, .9);
					double endPointWidth = 0.015;

					stroke.Begin(LXiSTROKE_LINES, refColor, 0.7);

					if (align == 0) // Vertical alignment
					{
						// main line
						stroke.Vertex3(0.0, 0.0, 0.0, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, refSize, 0.0, LXiSTROKE_ABSOLUTE);

						// end lines across X
						stroke.Vertex3(-endPointWidth * refSize, 0.0, 0.0, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(endPointWidth * refSize, 0.0, 0.0, LXiSTROKE_ABSOLUTE);

						stroke.Vertex3(-endPointWidth * refSize, refSize, 0.0, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(endPointWidth * refSize, refSize, 0.0, LXiSTROKE_ABSOLUTE);

						// end lines across Z
						stroke.Vertex3(0.0, 0.0, -endPointWidth * refSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, 0.0,  endPointWidth * refSize, LXiSTROKE_ABSOLUTE);

						stroke.Vertex3(0.0, refSize, -endPointWidth * refSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, refSize, endPointWidth * refSize, LXiSTROKE_ABSOLUTE);
					}
					else if (align == 1)
					{
						double y = refSize * 0.5;
						double halfSize = y;

						// main line
						stroke.Vertex3(0.0, y, -halfSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, y, halfSize, LXiSTROKE_ABSOLUTE);

						// end lines Y
						stroke.Vertex3(0.0, -endPointWidth * refSize + y, -halfSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, endPointWidth * refSize + y, -halfSize, LXiSTROKE_ABSOLUTE);

						stroke.Vertex3(0.0, -endPointWidth * refSize + y, halfSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(0.0, endPointWidth * refSize + y, halfSize, LXiSTROKE_ABSOLUTE);

						// end lines X
						stroke.Vertex3(-endPointWidth * refSize, y, -halfSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(endPointWidth * refSize, y, -halfSize, LXiSTROKE_ABSOLUTE);

						stroke.Vertex3(-endPointWidth * refSize, y, halfSize, LXiSTROKE_ABSOLUTE);
						stroke.Vertex3(endPointWidth * refSize, y, halfSize, LXiSTROKE_ABSOLUTE);
					}

				}

				if (drawSelected && selected)
				{
					// Need to get bind skeleton joints
					CLxUser_ItemGraph itemLinkGraph;
					CLxUser_Scene scene;
					CLxUser_Item metaGroupItem;
					item.Context(scene);
					scene.GraphLookup("rs.metaRig", itemLinkGraph);
					unsigned links = itemLinkGraph.Reverse(item);

					bool bindLocatorsGroupFound = false;

					if (0 < links)
					{
						// Find bind locators group.
						for (int i = 0; i < links; i++)
						{
							itemLinkGraph.Reverse(item, i, metaGroupItem);
							CLxUser_StringTag tag(metaGroupItem);

							if (tag.Match(TAG_ID_METAGROUP, "bindloc")) {
								bindLocatorsGroupFound = true;
								break;
							}
						}
					}
					else
					{
						return;
					}

					if (!bindLocatorsGroupFound) { return; }

					CLxVector minPos(1000000.0, 1000000.0, 1000000.0);
					CLxVector maxPos(-1000000.0, -1000000.0, -1000000.0);

					modo::item::Group metaGroup(metaGroupItem);
					std::vector<CLxUser_Item> bindLocators = metaGroup.Items();

					for (auto it = bindLocators.begin(); it != bindLocators.end(); it++)
					{
						CLxUser_Matrix blocWorldMatrixRaw;
						chan.Object(*it, "worldMatrix", blocWorldMatrixRaw);
						CLxMatrix4 blocWorldMatrix(blocWorldMatrixRaw);
						CLxVector wpos = blocWorldMatrix.getTranslation();

						if (wpos.x() < minPos.x()) { minPos[0] = wpos.x(); }
						if (wpos.x() > maxPos.x()) { maxPos[0] = wpos.x(); }

						if (wpos.y() < minPos.y()) { minPos[1] = wpos.y(); }
						if (wpos.y() > maxPos.y()) { maxPos[1] = wpos.y(); }

						if (wpos.z() < minPos.z()) { minPos[2] = wpos.z(); }
						if (wpos.z() > maxPos.z()) { maxPos[2] = wpos.z(); }

					}

					//minPos *= 0.8;
					//maxPos *= 0.8;

					//stroke.BeginW (LXiSTROKE_QUADS, color, 0.5, 1.0);
					//stroke.Vertex3 (minPos[0], minPos[1], minPos[2], LXiSTROKE_ABSOLUTE);
					//stroke.Vertex3 (maxPos[0], minPos[1], minPos[2], LXiSTROKE_ABSOLUTE);
					//stroke.Vertex3 (maxPos[0], minPos[1], maxPos[2], LXiSTROKE_ABSOLUTE);
					//stroke.Vertex3 (minPos[0], minPos[1], maxPos[2], LXiSTROKE_ABSOLUTE);

					double width = abs(maxPos.x() - minPos.x());
					double depth = abs(maxPos.z() - minPos.z());

					double cornerSize = width * 0.25;

					stroke.BeginW(LXiSTROKE_LINE_STRIP, color, 1.0, 2);

					stroke.Vertex3(minPos.x(), 0.0, minPos.z() - cornerSize, LXiSTROKE_ABSOLUTE);
					stroke.Vertex3(minPos.x() - cornerSize, 0.0, minPos.z() - cornerSize, LXiSTROKE_ABSOLUTE);
					stroke.Vertex3(minPos.x() - cornerSize, 0.0, minPos.z(), LXiSTROKE_ABSOLUTE);
				}
            }
            
        private:
            
        };
        
        static CLxMeta_ViewItem3D<CViewItem3D>        v3d_meta;

        static CLxMetaRoot root_meta;

        void initialize ()
        {
            package_meta.set_supertype (LXsITYPE_LOCATOR);
            package_meta.add_tag(LXsPKG_GRAPHS, GRAPHS);
            package_meta.add_tag(LXsPKG_CREATECMD, LXs_PKG_NODIRECTCREATE);
            package_meta.add_tag(LXsSRV_LOGSUBSYSTEM, LOG_SYSTEM);
            package_meta.add (&v3d_meta);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }; // end coreITEM namespace
}; // end rs namespace

