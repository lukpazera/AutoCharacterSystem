
#ifndef eventQueue_hpp
#define eventQueue_hpp

#include <stdio.h>
#include <string>

#include "lx_visitor.hpp"
#include "lx_scripts.hpp"

#include "onIdle.hpp"

namespace rs {
    
    /*
     * The queue of events that should be parsed by python code.
     * OnIdleEvent is used to fire the python command that will
     * process the queue.
     * Once the queue is processed it has be cleared on C++ side.
     */
    class EventQueue
    {
    public:
        
        EventQueue() :
        _onIdleVisitor()
        {}
        
        /*
         * Adds new event to the queue.
         * Event is simply a string that is added to queue.
         * This has to be a string in a form that can be parsed
         * on python side.
         * EventCode:argument1,argument2,etc.
         */
        void addEvent(std::string event, bool noRepeat=true);

        /*
         * Clears the queue.
         */
        void clear();
        
    private:
        void _armOnIdleEvent();
        
        std::string _queue;
        CLxInst_OneVisitor<OnIdleVisitor> _onIdleVisitor;
    };

} // end namespace

#endif /* eventQueue_hpp */
