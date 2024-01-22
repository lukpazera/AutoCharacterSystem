
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxu_schematic.hpp>
#include <lxu_log.hpp>
#include <lx_log.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* IKFK_IF_PKG_NAME = "rs.pkg.ikfkIF";
};

namespace rs {
    namespace ikfkIFPackage {
 
		static const char* CHAN_ENABLE = "rsikEnable";
        static const char* CHAN_BLEND = "rsikBlendChanName";
		
		static const char* CHAN_IK_COLOR = "rsikIKColor";
		static const char* CHAN_IK_COLOR_R = "rsikIKColor.R";
		static const char* CHAN_IK_COLOR_G = "rsikIKColor.G";
		static const char* CHAN_IK_COLOR_B = "rsikIKColor.B";

		static const char* CHAN_FK_COLOR = "rsikFKColor";
		static const char* CHAN_FK_COLOR_R = "rsikFKColor.R";
		static const char* CHAN_FK_COLOR_G = "rsikFKColor.G";
		static const char* CHAN_FK_COLOR_B = "rsikFKColor.B";

		static const char* CHAN_MATCH_IK = "rsikMatchIK";
		static const char* CHAN_MATCH_FK = "rsikMatchFK";

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
				desc.add(CHAN_ENABLE, LXsTYPE_BOOLEAN);
				desc.default_val(0);

                desc.add(CHAN_BLEND, LXsTYPE_STRING);
				desc.default_val("IKFKBlend");

				desc.add(CHAN_IK_COLOR, LXsTYPE_COLOR1);
				desc.vector_type(LXsVECTYPE_RGB);
				LXtVector ikColor;
				LXx_VSET3(ikColor, 1.0, 0.13, 0.2);
				desc.default_val(ikColor);

				desc.add(CHAN_FK_COLOR, LXsTYPE_COLOR1);
				desc.vector_type(LXsVECTYPE_RGB);
				LXtVector fkColor;
				LXx_VSET3(fkColor, 0.27, 1.0, 0.27);
				desc.default_val(fkColor);

				desc.add(CHAN_MATCH_IK, LXsTYPE_BOOLEAN);
				desc.default_val(1);

				desc.add(CHAN_MATCH_FK, LXsTYPE_BOOLEAN);
				desc.default_val(1);

            }
        };
        

        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (IKFK_IF_PKG_NAME);

        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.ikfkChain;rs.fkikChain;rs.matchDrivers;rs.ikfkBlend;rs.ikMatchTarget;rs.ikMatchTgtRef;rs.ikMatchGoalRef");

            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);

            root_meta.initialize();
        }
        
    }; // end ikfkIFPackage namespace
}; // end rs namespace

