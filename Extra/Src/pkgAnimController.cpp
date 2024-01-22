
#include <lxu_package.hpp>
#include <lxidef.h>

namespace {
    const char* ANIM_CONTROLLER_PKG_NAME = "rs.pkg.animController";
};

namespace rs {
    namespace animControllerPackage {
        
        static const char* CHAN_IN_CONTEXT = "rsacInContext";
        static const char* CHAN_IN_DEFAULT_SET = "rsacInDefaultSet";
        static const char* CHAN_ANIMATION_SPACE = "rsacAnimationSpace";
        static const char* CHAN_ACTOR_ITEM = "rsacActorItem";
        static const char* CHAN_ACTOR_CHANNELS = "rsacActorChannels";
        static const char* CHAN_STORE_IN_POSE = "rsacInPose";
		static const char* CHAN_LOCKED = "rsacLocked";
		static const char* CHAN_ALIAS = "rsacAlias";
        
        static LXtTextValueHint animationSpaceHint[] = {
            0, "fixed",
            1, "dynamic",
            -1, NULL
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
                desc.add(CHAN_IN_CONTEXT, LXsTYPE_BOOLEAN);
                desc.default_val(0);
          
                desc.add(CHAN_IN_DEFAULT_SET, LXsTYPE_BOOLEAN);
                desc.default_val(1);
                
                desc.add(CHAN_ANIMATION_SPACE, LXsTYPE_INTEGER);
                desc.hint(animationSpaceHint);
                desc.default_val(0);
                
                desc.add(CHAN_ACTOR_ITEM, LXsTYPE_BOOLEAN);
                desc.default_val(0);

                desc.add(CHAN_ACTOR_CHANNELS, LXsTYPE_BOOLEAN);
                desc.default_val(1);

                desc.add(CHAN_STORE_IN_POSE, LXsTYPE_BOOLEAN);
                desc.default_val(1);

				desc.add(CHAN_LOCKED, LXsTYPE_BOOLEAN);
				desc.default_val(0);

				desc.add(CHAN_ALIAS, LXsTYPE_STRING);
				desc.default_val("");
            }
        };
        
        static CLxMeta_Channels<CChannels> channels_meta;
        static CLxMeta_Package<CPackage> package_meta (ANIM_CONTROLLER_PKG_NAME);
        
        static CLxMetaRoot root_meta;
        
        void initialize ()
        {
            root_meta.add (&channels_meta);
            root_meta.add (&package_meta);
            
            root_meta.initialize();
        }
    }
    
} // end rs namespace

