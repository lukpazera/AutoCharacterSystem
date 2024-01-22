
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <math.h>


namespace {
    const char* ITEM_FIT_SHAPE_PKG_NAME = "rs.pkg.itemFitShape";
};

namespace rs {
    namespace itemFitShapePackage {
        
        static const char* CHAN_RAY_X_PLUS = "rsisRayXPlus";
        static const char* CHAN_RAY_Y_PLUS = "rsisRayYPlus";
    	static const char* CHAN_RAY_Z_PLUS = "rsisRayZPlus";
        static const char* CHAN_RAY_X_MINUS = "rsisRayXMinus";
        static const char* CHAN_RAY_Y_MINUS = "rsisRayYMinus";
        static const char* CHAN_RAY_Z_MINUS = "rsisRayZMinus";

        static const char* CHAN_MARGIN = "rsisMargin";
        
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
                desc.add(CHAN_RAY_X_PLUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);

                desc.add(CHAN_RAY_Y_PLUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);

                desc.add(CHAN_RAY_Z_PLUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);
                
                desc.add(CHAN_RAY_X_MINUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);
                
                desc.add(CHAN_RAY_Y_MINUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);
                
                desc.add(CHAN_RAY_Z_MINUS, LXsTYPE_BOOLEAN);
                desc.default_val(0);

                desc.add(CHAN_MARGIN, LXsTYPE_PERCENT);
                desc.default_val(0.15);
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (ITEM_FIT_SHAPE_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
        
    }; // end colorPackage namespace
}; // end rs namespace

