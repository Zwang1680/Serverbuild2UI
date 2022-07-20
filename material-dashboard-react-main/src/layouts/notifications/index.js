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

import emailgroup from "assets/images/internal/EmailGroup.png"
import inventorytool from "assets/images/internal/InventoryGroup.png"
import knowledgebase from "assets/images/internal/knowledgebase.png"
import telebot from "assets/images/internal/Telebot.png"
import wireguard from "assets/images/internal/wireguardvpn.png"
import grafana from "assets/images/internal/grafana.png"

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function Notifications() {
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
              image={emailgroup}
              title="Email Groups"
              description="the emails of all LCO employees"
              action={{
                type: "external",
                route: "http://emailgroups.lco.gtn/",
                color: "info",
                label: "Go"
              }}
            />
          </Grid>
          <Grid item xs={8} md={4} xl={4}>
            <SimpleBlogCard
              image={inventorytool}
              title="IT Inventory Tool"
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
              image={knowledgebase}
              title="Knowledge Base"
              description="Helpful documentation for all needs"
              action={{
                type: "external",
                route: "https://sites.google.com/lco.global/docs?pli=1",
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
                image={telebot}
                title="Telebot Web Interface"
                description="The telescpe operatios slack bot information"
                action={{
                  type: "external",
                  route: "http://telbot.lco.gtn/",
                  color: "info",
                  label: "Go"
                }}
              />
            </Grid>
            <Grid item xs={8} md={4} xl={4}>
              <SimpleBlogCard
                image={grafana}
                title="Grafana Metrics"
                description="Grafana login"
                action={{
                  type: "external",
                  route: "http://metrics.lco.gtn/login",
                  color: "info",
                  label: "Go"
                }}
              />
            </Grid>
            <Grid item xs={8} md={4} xl={4}>
              <SimpleBlogCard
                image={wireguard}
                title="Wireguard VPN"
                description="The wireguard VPN server"
                action={{
                  type: "external",
                  route: "https://wireguard-vpn-manager.lco.global/login",
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

export default Notifications;
