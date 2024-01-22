
/*
 * This command tests whether a vertex map is empty.
 * For weight map it means that there are no values greater then
* a given threshold in the map.
 */

#ifndef cmd_vmapEmpty_hpp
#define cmd_vmapEmpty_hpp

#include <lxu_command.hpp>
#include "constants.hpp"

namespace vertexMapEmpty {

    class Command : public CLxBasicCommand
    {
    public:

        Command();
        ~Command();
      
        int basic_CmdFlags() OVERRIDE_MACRO;
        void cmd_Execute(unsigned int flags) OVERRIDE_MACRO;
        LxResult cmd_Query (unsigned int index, ILxUnknownID vaQuery) OVERRIDE_MACRO;

        static void initialize(const char* commandName);

    private:
        enum {
            ARG_IS_EMPTY = 0,
            ARG_TYPE,
            ARG_NAME,
        };
        
        bool _isWeightMapEmpty();
        
        CLxUser_Scene _scene;
    };

} // end namespace
#endif
