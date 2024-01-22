
#include "mitem.hpp"

namespace modo {
    namespace item {
        
		std::vector<Group> Item::GetItemGroups()
		{
			CLxUser_Scene scene;
			CLxUser_ItemGraph itemGroupsGraph;
			this->GetContext(scene);
			scene.GraphLookup(LXsGRAPH_ITEMGROUPS, itemGroupsGraph);

			int groupsCount = itemGroupsGraph.Reverse(*this);
			std::vector<Group> itemMembers;
			for (int i = 0; i < groupsCount; i++)
			{
				Group group;
				itemGroupsGraph.Reverse(*this, i, group);
				itemMembers.push_back(group);
			}

			return itemMembers;
		}

        bool Mesh::GetReadOnlyMesh(CLxUser_Mesh &mesh)
        {
            unsigned int index;
            if (LXx_OK(this->ChannelLookup (LXsICHAN_MESH_MESH, &index))) {
                CLxUser_Scene scene;
                CLxUser_ChannelRead chanRead;
                
                if (!this->GetContext (scene))
                {
                    return false;
                }

                scene.GetChannels (chanRead, LXs_ACTIONLAYER_EDIT);

                return chanRead.Object ((*this), index, mesh);
            }
            return false;
        }
        
        std::vector<CLxUser_Item> Group::Items()
        {
            CLxUser_Scene scene;
            CLxUser_ItemGraph itemGroupsGraph;
            this->GetContext(scene);
            scene.GraphLookup(LXsGRAPH_ITEMGROUPS, itemGroupsGraph);
            
            int itemMembersCount = itemGroupsGraph.Forward(*this);
            std::vector<CLxUser_Item> itemMembers;
            for (int i = 0; i < itemMembersCount; i++)
            {
                CLxUser_Item itemMember;
                itemGroupsGraph.Forward(*this, i, itemMember);
                itemMembers.push_back(itemMember);
            }

            return itemMembers;
        }
    } // end item namespace
} // end modo namespace
