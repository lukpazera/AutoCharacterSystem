
#include <stdio.h>

#include <lx_scripts.hpp>
#include <lx_undo.hpp>

#include "mselection.hpp"
#include "listener.hpp"
#include "itemUtils.hpp"

namespace rs {

    void CListener::sil_ItemParent(ILxUnknownID item)
    {
        if (!_listeningEnabled()) { return; }
        
        CLxUser_Item parentedItem(item);
        CLxUser_Item rootItem;
        
        if (itemutils::getParentRig(parentedItem, rootItem))
        {
            std::string event = "itemParent:" + parentedItem.GetIdentity() + "," + rootItem.GetIdentity();
            _eventQueue.addEvent(event);
        }
    }

    void CListener::sil_ItemPackage (ILxUnknownID item)
    {
    }

    /**
     * Only react if newly added item was added somewhere in the rig hierarchy.
     */
    void CListener::sil_ItemAdd(ILxUnknownID item)
    {
        if (!_listeningEnabled()) { return; }

        CLxUser_Item addedItem(item);
        CLxUser_Item rootItem;
        
        if (itemutils::getParentRig(addedItem, rootItem))
        {
            std::string event = "itemAdd:" + addedItem.GetIdentity() + "," + rootItem.GetIdentity();
        	_eventQueue.addEvent(event);
        }
    }
    
    void CListener::sil_ItemRemove(ILxUnknownID item)
    {
    }

    /*
     * Look for channel value changes.
     * Channel value changes are excessive. They happen not only when user is editing.
     * - If user edited channel and changed time, channel value will happen
     * - When action is switched, lots of channel values happen, looks like it'll happen
     *   for every channel in actor/changed channel and for many actions: setup/scene, action that was chosen, edit.
     */
    void CListener::sil_ChannelValue(const char *action, ILxUnknownID item, unsigned int index)
    {
        if (!_listeningEnabled()) { return; }
        
        CLxUser_Item changedItem(item);
        
        // Apparently, it's possible that the action will be bad pointer
        // when creating new action.
        if (!action)
        {
            return;
        }
        
        // All the code here is for seamless IK/FK switching.
        // This needs to be moved into a nice, separate block sometime.
        
        // This block basically tries to avoid reacting to 2 types of changes.
        // First if is for skipping changes in setup - we do not match chains in setup.
        
        // Now if we have edit action we check if other action was in previous call.
        // If it was this means the action change is in progress and we get channel value
        // events as part of action changing (or creating new action).
        // If that's the case we want to bail out early.
        // Don't forget to set the action sequence flag to false.
        
        // If we have action other then setup or edit we assume this is action change/new action
        // sequence so we set the flag to true and bail out.
        if (strcmp(action, "setup") == 0)
        {
            return;
        }
        else if (strcmp(action, "edit") == 0)
        {
            if (_chanValSequence)
            {
                _chanValSequence = false;
                return;
            }
        }
        else
        {
            _chanValSequence = true;
            return;
        }
               
        // This is the code that prepares the chain match event.
        
        // Check if locator that is part of match chain was changed.
        CLxUser_ItemGraph xfrmGraph, matchItemGraph, matchLinkGraph;
        CLxUser_Scene scene;

        changedItem.Context(scene);
        scene.GraphLookup("xfrmCore", xfrmGraph);
        unsigned int connectedCount = xfrmGraph.Forward(changedItem);
        
        if (connectedCount > 0)
        {
            modo::item::Item locator;
            xfrmGraph.Forward(changedItem, 0, locator); // grab the locator item
            
			// We only care about reacting to edits to items that are part of the item group
			// that is linked to ik/fk switcher on the rs.ikfkChain graph in either direction.
			// forward direction from the edited item is IK chain, FK chain on reverse direction.
			// FK -> item -> IK

			// Get changed item's groups first
			std::vector<modo::item::Group> groups = locator.GetItemGroups();

			// We look for a group that is the ik or fk chain items holder.
			for (auto& group : groups) {

				scene.GraphLookup("rs.ikfkChain", matchLinkGraph);
				unsigned int fLinkedCount = matchLinkGraph.Forward(group);
				unsigned int rLinkedCount = matchLinkGraph.Reverse(group);
				if (fLinkedCount > 0 || rLinkedCount > 0)
				{
					
					std::string targetChain;
					CLxUser_Item switcherItem;
					if (fLinkedCount > 0)
					{
						matchLinkGraph.Forward(group, 0, switcherItem);
						targetChain = "ik"; // this is the chain that we want to be matched!
					}
					else if (rLinkedCount > 0)
					{
						matchLinkGraph.Reverse(group, 0, switcherItem);
						targetChain = "fk"; // this is the chaing that we want to be matched!
					}

					std::string event = "matchChain:" + switcherItem.GetIdentity() + "," + targetChain;
					_eventQueue.addEvent(event);
					break;
				}

			}
        }
    }

    void CListener::selevent_Add(LXtID4 type, unsigned int subtType)
    {
        if (!_listeningEnabled()) { return; }
        
        LXtID4 itemSelectType = _selectionService.LookupType("item");

        if (type == itemSelectType)
        {
            modo::selection::Item itemSel;
            CLxUser_Item lastSelectedItem;
            if (!itemSel.GetLast(lastSelectedItem)) { return; }
            
            if (subtType == _rootType)
            {
                std::string event = "rootSel:" + lastSelectedItem.GetIdentity();
                _eventQueue.addEvent(event);
            }
            else if (subtType == _moduleType)
            {
                std::string event = "moduleSel:" + lastSelectedItem.GetIdentity();
                _eventQueue.addEvent(event);
            }
        }
    }
    
    void CListener::selevent_Time(double time)
    {
    }
    
    void CListener::cmdsysevent_ExecutePre (ILxUnknownID cmd, int type, int isSandboxed, int isPostCmd)
    {
        CLxUser_Command command(cmd);
        const char* name;
        command.Name(&name);
        std::string cmdName(name);
  
        // When user does undo we want to stop listening.
        // We do not want undone actions to trigger listeners,
        // trying to react to undo will most likely cause crash.
        if (cmdName == "app.undo")
        {
            _lastCommandWasUndo = true;
            _suspendListenOnUndo = true;
        }
        // When the command is something else then undo we need
        // to resume listening if it was suspended.
        // (Not sure why this is not in ExecutePost).
        else
        {
            if (_lastCommandWasUndo) {
                _lastCommandWasUndo = false;
                _suspendListenOnUndo = false;
            }
        }
    }
    
    void CListener::cmdsysevent_ExecuteResult (ILxUnknownID cmd, int type, int isSandboxed, int isPostCmd, int wasSuccessful)
    {
        
    }

    void CListener::cmdsysevent_ExecutePost (ILxUnknownID cmd, int isSandboxed, int isPostCmd)
    {
        CLxUser_Command command(cmd);
        const char* name;
        command.Name(&name);
        std::string cmdName(name);
   

        if (cmdName == "rs.sys.clearEventQueue")
        {
            _eventQueue.clear();
        }

    }
 
    /*
     * User value is used to pass the state of listening to scene flag.
     */
    bool CListener::_getListenToScene()
    {
		CLxUser_CommandService cmdSrv;
		CLxUser_Command userValCmd;
		int value = 0;

		if (cmdSrv.NewCommand(userValCmd, "user.value")) {
			CLxUser_Attributes cmdAttr;
			CLxLoc_ValueArray valArray;
			cmdAttr.set(userValCmd);
			cmdAttr.SetString(0, "rs.listenToScene");
			int valueArgIndex = cmdAttr.FindIndex("value");
			if (cmdSrv.QueryIndex(userValCmd, valueArgIndex, valArray)) {
				if (valArray.Count() > 0) {
					valArray.GetInt(0, &value);
				}
			}
		}

        return (bool) value;
    }

    bool CListener::_listeningEnabled()
    {
		if ((_suspendListenOnUndo) | !_getListenToScene()) { return false; }
		return true;
    }
}
