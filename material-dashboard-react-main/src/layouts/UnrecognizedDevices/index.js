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

import unrecognizedDataTable from "layouts/UnrecognizedDevices/data/unrecogizedDataTable"

function UnrecognizedDevices() {
    const { columns, rows } = unrecognizedDataTable();

    return (
        <DashboardLayout>
            <DashboardNavbar />
            <MDBox mb={10}>
                <Grid container spacing={5}>
                    <Grid item xs={6}>
                        <DefaultInfoCard
                            icon="info"
                            title="Explanation"
                            description="The table below contains a list of all computers which tried to network boot but were not found in the LCO IT Portal database. You can use this workflow to add them to the database quickly and easily. You can use URL query parameters to customize this display."
                        />
                    </Grid>
                    <Grid item xs={6}>
                        <DefaultInfoCard
                            icon="info"
                            title="Backend Data Filtering Parameters (Query Parameters)"
                            description="(site = unset) and
                            (since = 2021-06-28T17:05:18.417Z)"
                        />
                    </Grid>
                </Grid>
                <MDBox pt={3}>
                    <Grid container spacing={5}>
                        <Grid item xs={1}/>
                        <Grid item xs={7}>
                            <MDInput label="Search here" size="large"/>
                        </Grid>
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

export default UnrecognizedDevices;