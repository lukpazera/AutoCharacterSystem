
#include "itemUtils.hpp"
#include "constants.hpp"

namespace rs
{
    namespace itemutils
    {

        /*
         * Gets parent item of a rig.
         */
        bool
        getParentRig (CLxUser_Item &item, CLxUser_Item &rootItem)
        {
            CLxUser_Item parent;
            CLxUser_Item newParent;
            CLxItemType	rootItemType(c::rigItemType::ROOT);
            bool parentFound = false;
            
            item.Parent(parent);
            
            while (parent) {
                if (parent.test() && parent.IsA (rootItemType)) {
                    rootItem.set(parent);
                    parentFound = true;
                    break;
                }
                if (parent.test()) {
                    parent.Parent(newParent);
                    parent.set(newParent);
                }
                else {
                    break;
                }
            }
            return parentFound;
        }
        
    }
}

