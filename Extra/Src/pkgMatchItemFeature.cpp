
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_schematic.hpp>
#include <lxu_log.hpp>
#include <lx_log.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* MATCH_IF_PKG_NAME = "rs.pkg.matchItemXfrmIF";
};

namespace rs {
    namespace matchIFPackage {
        
        static const char* CHAN_MATCH_POS = "rsmxMatchPos";
        static const char* CHAN_MATCH_ROT = "rsmxMatchRot";
		static const char* CHAN_MATCH_POS_LOCAL = "rsmxMatchPosLocal";
		static const char* CHAN_MATCH_ROT_LOCAL = "rsmxMatchRotLocal";
        
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
                desc.add(CHAN_MATCH_POS, LXsTYPE_BOOLEAN);
                desc.default_val(false);
                
                desc.add(CHAN_MATCH_ROT, LXsTYPE_BOOLEAN);
                desc.default_val(true);

				desc.add(CHAN_MATCH_POS_LOCAL, LXsTYPE_BOOLEAN);
				desc.default_val(false);

				desc.add(CHAN_MATCH_ROT_LOCAL, LXsTYPE_BOOLEAN);
				desc.default_val(false);
            }
        };
        

        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (MATCH_IF_PKG_NAME);

        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.chainMatchX;rs.itemMatchX");

            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);

            root_meta.initialize();
        }
        
    }; // end matchIFPackage namespace
}; // end rs namespace

