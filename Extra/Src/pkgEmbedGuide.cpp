#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>


namespace {
    const char* EMBED_GUIDE_PKG_NAME = "rs.pkg.embedGuide";
};


namespace rs {
    namespace embedGuidePackage {
        
        static const char* CHAN_POSITION_SOURCE = "rsegPosSource";
 
        static LXtTextValueHint posSourceHint[] = {
            0, "xaxis",
            1, "yaxis",
            2, "zaxis",
            3, "closest",
            -1, NULL,
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
            
            void
            init_chan(CLxAttributeDesc &desc)
            {
                desc.add(CHAN_POSITION_SOURCE, LXsTYPE_INTEGER);
                desc.set_hint(posSourceHint);
                desc.default_val(0);
            }
        };
        
        static CLxMeta_Channels<CChannels>         channels_meta;
        static CLxMeta_Package<CPackage>           package_meta (EMBED_GUIDE_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.egAxesSource;rs.egOrientUp;rs.egOrientFwd");
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }; // end embed guide package namespace
}; // end rs namespace

