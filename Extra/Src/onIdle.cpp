
#include "onIdle.hpp"

#include <lx_command.hpp>

namespace rs {

    LxResult OnIdleVisitor::Evaluate()
    {
        CLxUser_CommandService cmdService;
        std::string cmdString = "rs.sys.parseEventQueue {" + _queue + "}";
        cmdService.ExecuteArgString (0, LXiCTAG_NULL, cmdString.c_str());

    	return LXe_OK;
    }

	void OnIdleVisitor::setQueueString(std::string queue)
    {
        _queue = queue;
    }

} // end rs namespace
