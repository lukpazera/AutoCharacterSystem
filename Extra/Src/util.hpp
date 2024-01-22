
#pragma once

#include <stdio.h>
#include <lx_mesh.hpp>
#include <lxidef.h>
#include <lx_select.hpp>
#include <lx_seltypes.hpp>

namespace util {

    void ClearAllPolygons ();

    void ClearPolygon(LXtPolygonID id, CLxUser_Mesh &mesh);

    void SelectPolygon(LXtPolygonID id, CLxUser_Mesh &mesh);

} // end namespace
