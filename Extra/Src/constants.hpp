#pragma once

#ifdef MODO_17
#define OVERRIDE_MACRO override
#else
#define OVERRIDE_MACRO LXx_OVERRIDE
#endif

namespace rs {
    namespace c {
        namespace rigItemType {
    		static const char* ROOT = "rs.root";
        	static const char* MODULE = "rs.module";
        }
    }
}
