import { useState } from "react";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAlert from "components/MDAlert";
import MDButton from "components/MDButton";
import MDSnackbar from "components/MDSnackbar";
import SimpleBlogCard from "examples/Cards/BlogCards/SimpleBlogCard";

import github from "assets/images/github.png"
import wrike from "assets/images/wrike.png"
import fmx from "assets/images/FMX.png"
import redmine from "assets/images/Redmine.png"
import aws from "assets/images/AWS.png"

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function ExternalTools() {
  const [successSB, setSuccessSB] = useState(false);
  const [infoSB, setInfoSB] = useState(false);
  const [warningSB, setWarningSB] = useState(false);
  const [errorSB, setErrorSB] = useState(false);

  const openSuccessSB = () => setSuccessSB(true);
  const closeSuccessSB = () => setSuccessSB(false);
  const openInfoSB = () => setInfoSB(true);
  const closeInfoSB = () => setInfoSB(false);
  const openWarningSB = () => setWarningSB(true);
  const closeWarningSB = () => setWarningSB(false);
  const openErrorSB = () => setErrorSB(true);
  const closeErrorSB = () => setErrorSB(false);

  const alertContent = (name) => (
    <MDTypography variant="body2" color="white">
      A simple {name} alert with{" "}
      <MDTypography component="a" href="#" variant="body2" fontWeight="medium" color="white">
        an example link
      </MDTypography>
      . Give it a click if you like.
    </MDTypography>
  );

  const renderSuccessSB = (
    <MDSnackbar
      color="success"
      icon="check"
      title="Material Dashboard"
      content="Hello, world! This is a notification message"
      dateTime="11 mins ago"
      open={successSB}
      onClose={closeSuccessSB}
      close={closeSuccessSB}
      bgWhite
    />
  );

  const renderInfoSB = (
    <MDSnackbar
      icon="notifications"
      title="Material Dashboard"
      content="Hello, world! This is a notification message"
      dateTime="11 mins ago"
      open={infoSB}
      onClose={closeInfoSB}
      close={closeInfoSB}
    />
  );

  const renderWarningSB = (
    <MDSnackbar
      color="warning"
      icon="star"
      title="Material Dashboard"
      content="Hello, world! This is a notification message"
      dateTime="11 mins ago"
      open={warningSB}
      onClose={closeWarningSB}
      close={closeWarningSB}
      bgWhite
    />
  );

  const renderErrorSB = (
    <MDSnackbar
      color="error"
      icon="warning"
      title="Material Dashboard"
      content="Hello, world! This is a notification message"
      dateTime="11 mins ago"
      open={errorSB}
      onClose={closeErrorSB}
      close={closeErrorSB}
      bgWhite
    />
  );

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={3} mb={3} py={3}>
        <MDBox mb={4}>
        <Grid container spacing={1}>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={aws}
              title="AWS console"
              description="a link to the AWS console"
              action={{
                type: "external",
                route: "https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fus-west-2.console.aws.amazon.com%2Fconsole%2Fhome%3FhashArgs%3D%2523%26isauthcode%3Dtrue%26region%3Dus-west-2%26state%3DhashArgsFromTB_us-west-2_f08c6840b7cfeb6f&client_id=arn%3Aaws%3Asignin%3A%3A%3Aconsole%2Fcanvas&forceMobileApp=0&code_challenge=hCeHndvinX68nTVRjc_2EnU6KQpRBLTD6a09IWJUPew&code_challenge_method=SHA-256",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={redmine}
              title="RedmineUp issues"
              description="inventory information at LCO servers"
              action={{
                type: "external",
                route: "http://itinventory.lco.gtn/",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={fmx}
              title="FMX"
              description="The FMX login"
              action={{
                type: "external",
                route: "https://lco-global.gofmx.com/login",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          </Grid>
        </MDBox>
        <MDBox  mb={4}>
          <Grid container spacing={1}>
            <Grid item xs={8} md={4} xl={4}>
              <SimpleBlogCard
                image={wrike}
                title="Wrike"
                description="wrike start page"
                action={{
                  type: "external",
                  route: "https://www.wrike.com/",
                  color: "info",
                  label: "Go"
                }}
              />
            </Grid>
            <Grid item xs={8} md={4} xl={4}>
              <SimpleBlogCard
                image={github}
                title="Github"
                description="LCO github repos"
                action={{
                  type: "external",
                  route: "https://github.com/LCOGT/",
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

export default ExternalTools;
