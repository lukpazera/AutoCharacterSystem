
#include "mmeshgeo.hpp"

namespace modo {
    namespace meshgeo {
        
        bool MeshMap::ID(LXtID4 type, std::string const& mapName, LXtMeshMapID &id)
        {
            if (LXx_FAIL(this->SelectByName(type, mapName.c_str())))
            {
                return false;
            }
            id = this->CLxUser_MeshMap::ID();
            return true;
        }
    } // end mesh geo namespace
} // end modo namespace
