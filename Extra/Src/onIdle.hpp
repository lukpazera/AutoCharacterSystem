
#ifndef onIdle_hpp
#define onIdle_hpp

#include <string>

#include <lxidef.h>
#include <lxresult.h>

namespace rs {
    
/*
 * OnIdleVisitor is a helper class used to perform On Idle Event.
 * Evaluate() method will be called once the on idle event is registered.
 *
 * TODO: Make visitor process a queue of commands rather then single command.
 * This is in case there are multiple events before idle is called.
 */
class OnIdleVisitor
{
public:

    LxResult Evaluate ();
    
    /*
     * Use this method to set the queue string.
     * It'll be passed as an argument to a queue parsing command.
     */
    void setQueueString (std::string queue);

private:

    std::string _queue;
};

} // end rs namespace

#endif /* onIdle_hpp */
