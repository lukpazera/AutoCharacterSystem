
#ifndef mitem_hpp
#define mitem_hpp

#include <vector>

#include <lxidef.h>
#include <lx_item.hpp>
#include <lx_mesh.hpp>
#include <lx_action.hpp>

namespace modo {
    namespace item {
  
		class Group;

		class Item : public CLxUser_Item
		{
		public:
			Item() {}
			Item(ILxUnknownID obj) : CLxUser_Item(obj) {}

			/*
			 * Gets all the item groups that this item belongs to.
			 */
			std::vector<Group> GetItemGroups();
		};

        class Mesh : public CLxUser_Item
        {
        public:
            /* Call parent class constructors */
            Mesh () {}
            Mesh (ILxUnknownID obj) : CLxUser_Item (obj) {}

            bool GetReadOnlyMesh (CLxUser_Mesh &mesh);
        };

		class Group : public CLxUser_Item
		{
		public:
			/* Call parent class constructors */
			Group() {}
			Group(ILxUnknownID obj) : CLxUser_Item(obj) {}

			std::vector<CLxUser_Item> Items();
		};

    } // end selection namespace
} // end modo namespace

#endif /* mitem_hpp */
