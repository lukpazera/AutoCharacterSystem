
#ifndef cmd_partitionMeshByWeights_hpp
#define cmd_partitionMeshByWeights_hpp

#include <lxu_command.hpp>
#include "constants.hpp"

namespace partitionMeshByWeights {

    class Command : public CLxBasicCommand
    {
    public:

        Command();
        ~Command();
      
        int basic_CmdFlags() OVERRIDE_MACRO;
        void cmd_Execute(unsigned int flags) OVERRIDE_MACRO;

        static void initialize(const char* commandName);

    private:
        enum {
            ARG_ITEM = 0,
            ARG_MAPSLIST,
            ARG_SUBDIVIDE,
            ARG_DOUBLE_SIDED,
			ARG_SELECTION_SET
        };

        bool SetScene();
        bool SetMeshToPartition(CLxUser_Item &meshToPartition);
        std::vector<std::string> GetWeightMapNames();
        bool _getSubdivide();
        bool _getDoubleSided();
		bool _getSelectionSet();
        
        CLxUser_Scene _scene;
    };

} // end namespace
#endif /* cmdPartitionMeshByWeights_hpp */
