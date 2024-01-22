

#ifndef itemUtils_hpp
#define itemUtils_hpp

#include <vector>

#include "lx_command.hpp"
#include "lx_item.hpp"
#include <lx_scripts.hpp>
#include <lxu_queries.hpp>

namespace rs
{
    namespace itemutils
    {
        
    	bool getParentRig (CLxUser_Item &item, CLxUser_Item &rootItem);

    } // end namespace itemUtils
} // end namespace rs

#endif
