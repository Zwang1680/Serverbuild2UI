/**
=========================================================
* Material Dashboard 2 React - v2.1.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2022 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import DefaultInfoCard from "examples/Cards/InfoCards/DefaultInfoCard";

// Data
import reportsBarChartData from "layouts/dashboard/data/reportsBarChartData";
import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";
import Map from "examples/map/Map"

// Dashboard components
import Projects from "layouts/dashboard/components/Projects";
import OrdersOverview from "layouts/dashboard/components/OrdersOverview";
import { LiquorOutlined } from "@mui/icons-material";

function Dashboard() {
  const { sales, tasks } = reportsLineChartData;
  const location = {
    address: '6740 Cortona Dr, Goleta, CA 93117',
    lat: 34.432800,
    lng: -119.863260,
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs>
            <MDBox mb={1.5}>
              <DefaultInfoCard
                color="primary"
                icon="storage"
                title="Unrecognized Devices"
                value="0"
              />
            </MDBox>
          </Grid>
          <Grid item xs>
            <MDBox mb={1.5}>
              <DefaultInfoCard
                color="success"
                icon="start"
                title="Today's Users"
                value="2,300"
              />
            </MDBox>
          </Grid>
          <Grid item xs>
            <MDBox mb={1.5}>
              <DefaultInfoCard
                color="info"
                icon="restart_alt"
                title="Rebuild Boot"
                value="34k"
              />
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>
      <MDBox>
        <Map location={location} zoomLevel={17}/>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
