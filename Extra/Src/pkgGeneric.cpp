
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* GENERIC_PKG = "rs.pkg.generic";
};

namespace rs {
    namespace genericPackage {
        
        static const char* CHAN_NAME = "rsName";
        static const char* CHAN_SIDE = "rsSide";
        static const char* CHAN_SIDE_FROM_MODULE = "rsSideFromModule";
		static const char* CHAN_HIDDEN = "rsHidden";

        static LXtTextValueHint sideHint[] = {
            0, "center",
            1, "left",
            -1, "right",
            2, NULL
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
                desc.add(CHAN_NAME, LXsTYPE_STRING);
                desc.default_val("Item");

                desc.add(CHAN_SIDE, LXsTYPE_INTEGER);
                desc.hint(sideHint);
                desc.default_val(0);
                
                desc.add(CHAN_SIDE_FROM_MODULE, LXsTYPE_BOOLEAN);
                desc.default_val(true);

				desc.add(CHAN_HIDDEN, LXsTYPE_BOOLEAN);
				desc.default_val(false);
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (GENERIC_PKG);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
        
    }; // end genericPackage namespace
}; // end rs namespace

