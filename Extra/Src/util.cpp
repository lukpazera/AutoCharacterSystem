
#include <stdio.h>
#include <lx_mesh.hpp>
#include <lxidef.h>
#include <lx_select.hpp>
#include <lx_seltypes.hpp>

#include "util.hpp"

namespace util {

    void ClearAllPolygons ()
    {
        CLxUser_SelectionService sel_svc;
        LXtID4 selectionType;
        selectionType = sel_svc.LookupType (LXsSELTYP_POLYGON);

        sel_svc.Clear(selectionType);
    }

    void ClearPolygon(LXtPolygonID id, CLxUser_Mesh &mesh)
    {
        LXtID4 selectionType;
        CLxUser_PolygonPacketTranslation polyPkt;
        CLxUser_SelectionService sel_svc;
        
        selectionType = sel_svc.LookupType (LXsSELTYP_POLYGON);
        polyPkt.autoInit ();
        
        sel_svc.Deselect (selectionType, polyPkt.Packet (id, mesh));
    }

    void SelectPolygon(LXtPolygonID id, CLxUser_Mesh &mesh)
    {
        LXtID4				selectionType;
        CLxUser_PolygonPacketTranslation polyPkt;
        CLxUser_SelectionService sel_svc;
        
        selectionType = sel_svc.LookupType (LXsSELTYP_POLYGON);
        polyPkt.autoInit ();
        
        sel_svc.Select (selectionType, polyPkt.Packet (id, mesh));
    }

} // end namespace
