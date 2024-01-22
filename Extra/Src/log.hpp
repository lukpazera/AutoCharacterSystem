#pragma once

#include <lxu_log.hpp>

namespace rs {
    class RSLog : public CLxLogMessage
    {
    public:
        RSLog (const char *log = "riggingsys") : CLxLogMessage (log) { }
        
        const char* GetFormat();
        const char* GetVersion();
    };
};
