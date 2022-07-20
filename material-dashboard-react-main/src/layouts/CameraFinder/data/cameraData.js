import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";


export default function data() {
    return {
        columns: [
          { Header: "Hostname", accessor: "hostname", align: "left" },
          { Header: "Instruments", accessor: "instrument", align: "left" },
        ],
    
        rows: [
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        4ag.coj.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        kb34
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        acc.ljg.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                       fg01
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        ag.2m0a.clma.ogg.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        kb09
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        floyds.coj.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        en12, kb38
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        floyds.ogg.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        en06, kb42
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        fs.coj.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        fs01
                    </MDTypography>
                )
            },
            {
                hostname: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        icc1.0m4a.aqwa.lsc.lco.gtn
                    </MDTypography>
                ),
                instrument: (
                    <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                        kb29
                    </MDTypography>
                )
            },
        ],
      };
    }