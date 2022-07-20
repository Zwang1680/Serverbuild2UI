import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import DefaultInfoCard from "examples/Cards/InfoCards/DefaultInfoCard";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import SimpleBlogCard from "examples/Cards/BlogCards/SimpleBlogCard";

import clientdash from "assets/images/puppet/clientdashboard.png"
import explorerdash from "assets/images/puppet/explorerdashboard.png"
import servermetrics from "assets/images/puppet/servermetrics.png"

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import Icon from "@mui/material/Icon";

function PuppetTools() {

    return (
        <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={3} mb={3} py={3}>
        <MDBox mb={4}>
        <Grid container spacing={1}>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={clientdash}
              title="PuppetBoard Client Dashboard"
              description='The PuppetBoard Client Dashboard will give you an "at-a-glance" view of the entire LCO Puppet infrastructure, with the ability to drill down into the current and historical information about each Puppet client machine.'
              action={{
                type: "external",
                route: "http://puppetboard.lco.gtn/",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={explorerdash}
              title="Puppet Explorer Dashboard"
              description='The Puppet Explorer Dashboard will help you explore the LCO Puppet infrastructure. You can use it to perform ad-hoc queries against the infrastructure, so that you can learn things (for example: "How many CentOS 5 machines do we have?").'
              action={{
                type: "external",
                route: "http://puppetexplorer.lco.gtn/",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={servermetrics}
              title="PuppetDB Server Metrics Dashboard"
              description="The PuppetDB Server Metrics Dashboard will help you diagnose problems with the PuppetDB Database itself. It will not give you any information about Puppet managed computers."
              action={{
                type: "external",
                route: "http://puppetmaster.lco.gtn:8080/pdb/dashboard/index.html",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
    );
}

export default PuppetTools