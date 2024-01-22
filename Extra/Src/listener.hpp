
#ifndef listener_hpp
#define listener_hpp

#include <lxu_command.hpp>
#include <lxu_package.hpp>
#include <lxu_select.hpp>
#include <lx_wrap.hpp>
#include <lx_listener.hpp>
#include <lx_scripts.hpp>
#include <lx_action.hpp>
#include <lxu_queries.hpp>

#include "modo.hpp"
#include "constants.hpp"
#include "onIdle.hpp"
#include "eventQueue.hpp"
#include "log.hpp"

namespace rs {

    class CListener :
        public CLxImpl_SceneItemListener,
    	public CLxImpl_SelectionListener,
    	public CLxImpl_CmdSysListener,
        public CLxSingletonPolymorph
    {
    public:
        LXxSINGLETON_METHOD
        
        CListener() :
        	_lastCommandWasUndo(false),
        	_suspendListenOnUndo(false),
        	_chanValSequence(false)
        {
            AddInterface(new CLxIfc_SceneItemListener<CListener>);
            AddInterface(new CLxIfc_SelectionListener<CListener>);
            AddInterface(new CLxIfc_CmdSysListener<CListener>);
            
            _rootType = _sceneService.ItemType(c::rigItemType::ROOT);
            _moduleType = _sceneService.ItemType(c::rigItemType::MODULE);
        }
        
        // Scene item listener
        void sil_ItemParent(ILxUnknownID item) OVERRIDE_MACRO;
        void sil_ItemPackage (ILxUnknownID item) OVERRIDE_MACRO;
        void sil_ItemAdd (ILxUnknownID item) OVERRIDE_MACRO;
        void sil_ItemRemove (ILxUnknownID item) OVERRIDE_MACRO;
        void sil_ChannelValue (const char *action, ILxUnknownID item, unsigned index) OVERRIDE_MACRO;
         
        // Selection listener
        void selevent_Add (LXtID4 type, unsigned int subtType) OVERRIDE_MACRO;
        void selevent_Time (double time) OVERRIDE_MACRO;
        
        // Command listener
        void cmdsysevent_ExecutePre (ILxUnknownID cmd, int type, int isSandboxed, int isPostCmd) OVERRIDE_MACRO;
        void cmdsysevent_ExecuteResult (ILxUnknownID cmd, int type, int isSandboxed, int isPostCmd, int wasSuccessful) OVERRIDE_MACRO;
        void cmdsysevent_ExecutePost (ILxUnknownID cmd, int isSandboxed, int isPostCmd) OVERRIDE_MACRO;

		//bool listen;

    private:
        /*
         * Gets whether listener should listen to events or not.
         */
        bool _getListenToScene();
        bool _listeningEnabled();
        
        EventQueue _eventQueue;
        CLxUser_SceneService _sceneService;
        CLxUser_SelectionService _selectionService;
        
        bool _lastCommandWasUndo;
        bool _suspendListenOnUndo;
        
        // Cache item types
        LXtItemType _rootType;
        LXtItemType _moduleType;
        
        bool _chanValSequence;
    };

    // This is the listener static object
	static CLxSingletonListener<CListener> listener;

} // end rs namespace

#endif // listener_hpp
