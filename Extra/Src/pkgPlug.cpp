
#include <stdio.h>
#include <lxu_package.hpp>
#include <lxu_modifier.hpp>
#include <lxidef.h>
#include <lx_log.hpp>
#include <math.h>


namespace {
    const char* PLUG_PKG_NAME = "rs.pkg.plug";
};


namespace rs {
    namespace plugPackage {
        
		static const char* CHAN_SOCKET_WPOS = "rspgSocWPos";
		static const char* CHAN_SOCKET_WROT = "rspgSocWRot";
		static const char* CHAN_SOCKET_WSCL = "rspgSocWScl";
		static const char* CHAN_PARENT_POS_OFFSET = "rspgPPosOffset";
		static const char* CHAN_PARENT_ROT_OFFSET = "rspgPRotOffset";

        class CPackage : public CLxPackage
        {
        public:
            
            CPackage ()
            {
            }
            
            ~CPackage ()
            {
            }
            
           
            unsigned int counter = 0;
        };
        
        
        class CChannels : public CLxChannels
        {
        public:
            
            void
            init_chan(CLxAttributeDesc &desc)
            {
				desc.add(CHAN_SOCKET_WPOS, LXsTYPE_MATRIX4);
				desc.set_storage();
				desc.add(CHAN_SOCKET_WROT, LXsTYPE_MATRIX4);
				desc.set_storage();
				desc.add(CHAN_SOCKET_WSCL, LXsTYPE_MATRIX4);
				desc.set_storage();

				LXtVector offset;
				LXx_VSET(offset, 0.0);

				desc.add(CHAN_PARENT_POS_OFFSET, LXsTYPE_DISTANCE);
				desc.vector_type(LXsVECTYPE_XYZ);
				desc.default_val(offset);

				desc.add(CHAN_PARENT_ROT_OFFSET, LXsTYPE_ANGLE);
				desc.vector_type(LXsVECTYPE_XYZ);
				desc.default_val(offset);
            }
        };
        
        static CLxMeta_Channels<CChannels>		 channels_meta;
        static CLxMeta_Package<CPackage>		 package_meta (PLUG_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            package_meta.add_tag(LXsPKG_GRAPHS, "rs.plugs;rs.plugBindLoc");
            
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }; // end plugPackage namespace
}; // end rs namespace

