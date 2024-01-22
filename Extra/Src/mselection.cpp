
#include "mselection.hpp"

namespace modo {
    namespace selection {

        void Item::Select(std::vector<CLxUser_Item> &items)
        {
            typename std::vector<CLxUser_Item>::iterator it = items.begin();
            for ( ; it != items.end(); ++it)
            {
                CLxItemSelection::Select(*it);
            }
        }

        bool Item::GetLast(CLxUser_Item &item)
        {
            LXtScanInfoID	scan;
            void			*pkt;
            
            scan = 0;
            int count = srv_sel.Count(sel_ID);
            if (count == 0) { return false; }
            
            count--;
            while (count >= 0)
            {
                pkt = srv_sel.ByIndex(sel_ID, count);
                pkt_trans.GetItem (pkt, item);
                if (Include (item))
                    return true;
            }
            
            return false;
        }
        
        VertexMap::VertexMap () :
        _useFiltering(false)
        {
        }

        VertexMap::VertexMap (LXtID4 type) :
        _useFiltering(true)
        {
            _type = type;
        }

        bool VertexMap::Include(LXtID4 type)
        {
            if (!_useFiltering)
            {
                return true;
            }

            return type == _type ? true : false;
        }

        bool WeightMap::Include (LXtID4 type)
        {
            return type == LXi_VMAP_WEIGHT ? true : false;
        }

        bool MorphMap::Include (LXtID4 type)
        {
            return type == LXi_VMAP_MORPH ? true : false;
        }
        
    } // end selection namespace
} // end modo namespace
