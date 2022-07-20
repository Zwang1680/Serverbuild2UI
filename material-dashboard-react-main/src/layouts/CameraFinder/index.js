import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import DefaultInfoCard from "examples/Cards/InfoCards/DefaultInfoCard";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

import cameraData from "layouts/CameraFinder/data/cameraData"

function CameraFinder() {
    const { columns, rows } = cameraData();
    return (
        <DashboardLayout>
            <DashboardNavbar />
            <MDBox mb={10}>
                <MDBox pt={3}>
                    <Grid container spacing={5}>
                        <Grid item xs={1}/>
                            <MDBox pt={5}>
                                <MDInput label="Search here" size="large"/>
                            </MDBox>
                    </Grid>
                </MDBox>
                <MDBox pt={3}>
                    <DataTable
                    table={{ columns, rows }}
                    isSorted={false}
                    entriesPerPage={5}
                    showTotalEntries={false}
                    noEndBorder
                    />
              </MDBox>
            </MDBox>
            <Footer />
        </DashboardLayout>
    );
}

export default CameraFinder;