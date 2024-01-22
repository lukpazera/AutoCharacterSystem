
#include <lxu_package.hpp>
#include <lxidef.h>

namespace {
    const char* CONTROLLER_PKG_NAME = "rs.pkg.controller";
};

namespace rs {
    namespace controllerPackage {
        
        static const char* CHAN_CONTROLLED_CHANNELS = "rsctControlledChannels";

        static LXtTextValueHint controlledChansHint[] = {
            0, "xfrm",
            1, "user",
			2, "item",
            -1, NULL
        };
        
        class CPackage : public CLxPackage
        {
        public:
            
        };
        
        class CChannels : public CLxChannels
        {
        public:
            
            void init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_CONTROLLED_CHANNELS, LXsTYPE_INTEGER);
                desc.hint(controlledChansHint);
                desc.default_val(0);
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (CONTROLLER_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.channelSet");
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }
    
} // end rs namespace

