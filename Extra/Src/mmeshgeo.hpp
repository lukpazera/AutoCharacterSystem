
#ifndef mmeshgeo_hpp
#define mmeshgeo_hpp

#include <string>

#include <lx_mesh.hpp>

namespace modo {
    namespace meshgeo {
        
        class MeshMap : public CLxUser_MeshMap
        {
        public:
            /* Call parent class constructors */
            MeshMap () {}
            MeshMap (ILxUnknownID obj) : CLxUser_MeshMap (obj) {}
            
            bool ID (LXtID4 type, std::string const& mapName, LXtMeshMapID &id);
        };
        
    } // end selection namespace
} // end modo namespace

#endif /* mmeshgeo_hpp */
