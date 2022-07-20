import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import DefaultInfoCard from "examples/Cards/InfoCards/DefaultInfoCard";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import Icon from "@mui/material/Icon";

function NetworkTools() {

    return (
        <DashboardLayout>
            <DashboardNavbar />
            <MDBox mb={10}>
                <Grid container spacing={4}>
                    <Grid item sm={1}/>
                    <Grid item>
                        <MDTypography>Please enter a fully qualified hostname or an IP Address to 🕵️ diagnose:</MDTypography>
                    </Grid>
                </Grid>
                <MDBox pt={3}>
                    <Grid container spacing={5}>
                        <Grid item xs={1}/>
                        <Grid item xs={3}>
                            <MDInput label="Search here" size="large" error/>
                        </Grid>
                        <Grid item xs={4}>
                            <MDButton>
                                <Icon>handyman</Icon>
                                Diagnose
                            </MDButton>
                        </Grid>
                    </Grid>
                </MDBox>
                </MDBox>
            <Footer />
        </DashboardLayout>
    );
}

export default NetworkTools