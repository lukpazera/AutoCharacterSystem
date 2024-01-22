
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_schematic.hpp>
#include <lxu_log.hpp>
#include <lx_log.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* GUIDEIF_PKG_NAME = "rs.pkg.guideIF";
};

namespace rs {
    namespace guideIFPackage {
        
        static const char* CHAN_GUIDE_MODE = "rsgdMode";
        static const char* CHAN_ZERO_TRANSFORMS = "rsgdZeroTransforms";
    
        static LXtTextValueHint modeHints[] = {
            0, "reference",
            1, "buffer",
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
        };
        
        class CChannels : public CLxChannels
        {
        public:

            void init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_ZERO_TRANSFORMS, LXsTYPE_BOOLEAN);
                desc.default_val(false);
                
                desc.add(CHAN_GUIDE_MODE, LXsTYPE_INTEGER);
                desc.set_hint(modeHints);
                desc.default_val(0);
            }
        };
        

        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (GUIDEIF_PKG_NAME);

        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.guideItem");

            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);

            root_meta.initialize();
        }
        
    }; // end guideIFPackage namespace
}; // end rs namespace

