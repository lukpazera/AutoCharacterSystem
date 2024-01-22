#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>

#include "constants.hpp"

namespace rs {
    namespace moduleItem {
        
        static const char* CHAN_NAME = "rsName";
        static const char* CHAN_IDENTIFIER = "rsIdentifier";
        static const char* CHAN_SIDE = "rsSide";
        static const char* CHAN_DROP_ACTION = "rsDropAction";
        static const char* CHAN_FILENAME = "rsFilename";
        
        static const char* CHAN_SIDE_INV = "rsSideInv";
        static const char* CHAN_SIDE_MIRROR_ANGLE_OFFSET = "rsMAngleOffset";
        static const char* CHAN_SIDE_IS_RIGHT = "rsIsRight";
        static const char* CHAN_SIDE_IS_LEFT = "rsIsLeft";
        static const char* CHAN_SIDE_RIGHT_NEG_FACTOR = "rsRNegFactor";
        static const char* CHAN_SIDE_LEFT_NEG_FACTOR = "rsLNegFactor";
		static const char* CHAN_IS_MIRRORED = "rsIsMirror";
		static const char* CHAN_FIRST_SIDE = "rsFirstSide";
        
		static const char* CHAN_DEFAULT_THUMBNAIL = "rsDefaultThumb";

        static LXtTextValueHint sideHint[] = {
        	0, "center",
            1, "left",
            -1, "right",
            2, NULL
        };

        static LXtTextValueHint dropHint[] = {
            0, "none",
            1, "mouse",
            2, "ground",
            3, "both",
            -1, NULL
        };
        
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
                desc.add(CHAN_NAME, LXsTYPE_STRING);
                desc.default_val("Module");

                desc.add(CHAN_IDENTIFIER, LXsTYPE_STRING);
                desc.default_val("");
                
                desc.add(CHAN_SIDE, LXsTYPE_INTEGER);
                desc.hint(sideHint);
                desc.default_val(0);
                
                desc.add(CHAN_DROP_ACTION, LXsTYPE_INTEGER);
                desc.hint(dropHint);
                desc.default_val(1);
                
                // Side helper channels
                desc.add(CHAN_SIDE_INV, LXsTYPE_INTEGER);
                desc.default_val(0);
                
                desc.add(CHAN_SIDE_MIRROR_ANGLE_OFFSET, LXsTYPE_ANGLE);
                desc.default_val(0.0);

                desc.add(CHAN_SIDE_IS_RIGHT, LXsTYPE_BOOLEAN);
                desc.default_val(0);
                
                desc.add(CHAN_SIDE_IS_LEFT, LXsTYPE_BOOLEAN);
                desc.default_val(0);
                
                desc.add(CHAN_SIDE_RIGHT_NEG_FACTOR, LXsTYPE_INTEGER);
                desc.default_val(1);

                desc.add(CHAN_SIDE_LEFT_NEG_FACTOR, LXsTYPE_INTEGER);
                desc.default_val(1);
                
                desc.add(CHAN_FILENAME, LXsTYPE_STRING);
                desc.default_val("");

				desc.add(CHAN_IS_MIRRORED, LXsTYPE_BOOLEAN);
				desc.default_val(0);

				desc.add(CHAN_FIRST_SIDE, LXsTYPE_INTEGER);
				desc.hint(sideHint);
				desc.default_val(0);

				desc.add(CHAN_DEFAULT_THUMBNAIL, LXsTYPE_STRING);
				desc.default_val("");
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (c::rigItemType::MODULE);
        
        static CLxMetaRoot root_meta;
        
        void initialize	()
        {
            package_meta.set_supertype (LXsITYPE_GROUPLOCATOR);
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.modules;rs.editModule;rs.modulesMap;rs.symmetricModule;rs.submodules");
            package_meta.add_tag(LXsPKG_CREATECMD, LXs_PKG_NODIRECTCREATE);
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
        
    }; // end moduleItem namespace
}; // end rs namespace

