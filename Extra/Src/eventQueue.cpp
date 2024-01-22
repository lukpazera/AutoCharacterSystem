
#include "eventQueue.hpp"

namespace rs {
    
    void EventQueue::addEvent(std::string event, bool noRepeat)
    {
        if (noRepeat && !_queue.empty())
        {
            // if the event should not repeat in the queue don't add it twice
            // if the very same event is already there.
            if (_queue.find(event) != std::string::npos) { return; }
        }
        
        if (!_queue.empty()) { _queue += ";"; }
        _queue += event;
        _onIdleVisitor.loc.setQueueString(_queue);
        _armOnIdleEvent();
    }

    void EventQueue::clear()
    {
        _queue.clear();
    }

    void EventQueue::_armOnIdleEvent()
    {
        CLxUser_PlatformService platformService;
        platformService.CancelDoWhenUserIsIdle(_onIdleVisitor, LXfUSERIDLE_MOUSE_BUTTONS_UP | LXfUSERIDLE_CMD_STACK_EMPTY);
        platformService.DoWhenUserIsIdle(_onIdleVisitor, LXfUSERIDLE_MOUSE_BUTTONS_UP | LXfUSERIDLE_CMD_STACK_EMPTY);
    }
}
