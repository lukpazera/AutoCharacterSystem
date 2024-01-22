
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>


namespace {
    const char* BINDLOC_PKG_NAME = "rs.pkg.bindLocator";
};


namespace rs {
    namespace bindLocatorPackage {
        
        static const char* CHAN_EXPORT_NAME = "rsblExportName";
		static const char* CHAN_REGION_COLOR = "rsblRegionColor";
		static const char* CHAN_ORIENT_OFFSET = "rsblOrientOffset";
        
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
                desc.add(CHAN_EXPORT_NAME, LXsTYPE_STRING);
                desc.default_val(true);

				desc.add(CHAN_ORIENT_OFFSET, LXsTYPE_ANGLE);
				desc.vector_type(LXsCHANVEC_XYZ);
				LXtVector orient;
				orient[0] = 0.0;
				orient[1] = 0.0;
				orient[2] = 0.0;
				
				desc.default_val(orient);

                desc.add(CHAN_REGION_COLOR, LXsTYPE_COLOR1);
                desc.vector_type(LXsCHANVEC_RGB);
                LXtVector color;
				color[0] = .9;
				color[1] = 0.75;
				color[2] = 0.4;

                desc.default_val(color);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (BINDLOC_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.bindLocShadow;rs.bindLocPlug;rs.bindLocSocket;rs.bindLocCtrls;rs.bindLocBakedParent;rs.bindLocCmdRegion");
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);

            root_meta.initialize();
        }
  
    }; // end bindLocatorPackage namespace
}; // end rs namespace

