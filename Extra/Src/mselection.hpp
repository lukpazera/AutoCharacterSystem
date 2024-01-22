
#ifndef mselection_hpp
#define mselection_hpp

#include <lxu_select.hpp>

namespace modo {
    namespace selection {
        
		class Scene : public CLxSceneSelection
		{
		public:
		};

        // -------- Item Selection
        class Item : public CLxItemSelection
        {
        public:
            /*
             * Allows for selecting list of items.
             */
            void Select (std::vector<CLxUser_Item> &items);
            
            /*
             * Gets last selected item. Returns false if no items are selected.
             */
            bool GetLast (CLxUser_Item &);
        };

        // -------- Same as Item but allows for getting selection only for items of a given type.
        typedef CLxItemSelectionType ItemOfType;

        // -------- Vertex Map Selection
        class VertexMap : public CLxVertexMapSelection
        {
        public:
            VertexMap ();
            VertexMap (LXtID4 type);

			bool Include(LXtID4 type) override;
        private:
            bool _useFiltering;
            LXtID4 _type;
        };

        // -------- Weight Map Selection
        class WeightMap : public CLxVertexMapSelection
        {
        public:
			bool Include(LXtID4 type) override;
        };

        // -------- Morph Map Selection
        class MorphMap : public CLxVertexMapSelection
        {
        public:
			bool Include(LXtID4 type) override;
        };

    } // end selection namespace
} // end modo namespace

#endif /* mselection_hpp */
