
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* COLOR_PKG_NAME = "rs.pkg.color";
};

namespace rs {
    namespace colorPackage {
        
        static const char* CHAN_COLOR_IDENT = "rsclIdent";
        
        class CPackage : public CLxPackage
        {
		public:
            
            unsigned int counter = 0;
        };
        
        class CChannels : public CLxChannels
        {
        public:

            void init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_COLOR_IDENT, LXsTYPE_STRING);
                desc.default_val("");
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (COLOR_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
        
    }; // end colorPackage namespace
}; // end rs namespace

