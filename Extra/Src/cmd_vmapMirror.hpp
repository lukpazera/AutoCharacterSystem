
#ifndef cmd_vmapMirror_hpp
#define cmd_vmapMirror_hpp

#include <lxu_command.hpp>
#include <lxu_attributes.hpp>

#include "vmapMirror.hpp"
#include "constants.hpp"


namespace vertexMapMirror {

    class MeshPopup : public CLxDynamicUIValue
    {
    public:
        unsigned Flags () OVERRIDE_MACRO;
        bool ItemTest (CLxUser_Item &item) OVERRIDE_MACRO;
    };

    static LXtTextValueHint hintFromSide[] =
    {
        { VertexMapMirror::SIDE_RIGHT, "right" },
        { VertexMapMirror::SIDE_LEFT, "left" },
        {  -1, NULL }
    };

    enum {
        VMAPTYPE_WEIGHT = 0,
        VMAPTYPE_MORPH = 1
    };

    static LXtTextValueHint hintVertexMapType[] =
    {
        {  VMAPTYPE_WEIGHT, "weight" },
        {  VMAPTYPE_MORPH, "morph" },
        {  -1, NULL }
    };

    class Command : public CLxBasicCommand
    {
    public:
        
        Command();
        ~Command();
        
        int basic_CmdFlags() OVERRIDE_MACRO;
        void cmd_Execute(unsigned int flags) OVERRIDE_MACRO;
        CLxDynamicUIValue* atrui_UIValue (unsigned int index) OVERRIDE_MACRO;
		const LXtTextValueHint* attr_Hints (unsigned int index)	OVERRIDE_MACRO;

        static void initialize(const char* commandName);
        
    private:
        std::vector<std::string> splitArgument (const std::string &s, char delim);
        
        enum {
            ARGi_TYPE = 0,
            ARGi_FROMSIDE,
            ARGi_MESH,
            ARGi_SOURCE_MAP,
            ARGi_TARGET_MAP
        };
        
        unsigned int _getVertexMapType ();
    };
    
} // end namespace

#endif /* cmd_vmapMirror_hpp */
