#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>


namespace {
    const char* PIECE_PKG_NAME = "rs.pkg.piece";
};


namespace rs {
    namespace piecePackage {
  
        static const char* CHAN_CACHE = "rspcCache";
        
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

            void
            init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_CACHE, LXsTYPE_BOOLEAN);
                desc.default_val(false);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (PIECE_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
        
            root_meta.initialize();
        } 

    }; // end piecePackage namespace
}; // end rs namespace

