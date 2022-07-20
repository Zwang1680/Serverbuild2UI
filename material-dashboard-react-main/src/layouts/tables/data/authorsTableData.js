/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
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

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import MDBadge from "components/MDBadge";

// Images
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/team-4.jpg";

export default function data() {
  const Author = ({ image, name, email }) => (
    <MDBox display="flex" alignItems="center" lineHeight={1}>
      <MDAvatar src={image} name={name} size="sm" />
      <MDBox ml={2} lineHeight={1}>
        <MDTypography display="block" variant="button" fontWeight="medium">
          {name}
        </MDTypography>
        <MDTypography variant="caption">{email}</MDTypography>
      </MDBox>
    </MDBox>
  );

  const Job = ({ title, description }) => (
    <MDBox lineHeight={1} textAlign="left">
      <MDTypography display="block" variant="caption" color="text" fontWeight="medium">
        {title}
      </MDTypography>
      <MDTypography variant="caption">{description}</MDTypography>
    </MDBox>
  );

  return {
    columns: [
      { Header: "Site Code", accessor: "sitecode", align: "left" },
      { Header: "Short Description", accessor: "description", align: "left" },
      { Header: "Device Count", accessor: "count", align: "center" },
      { Header: "action", accessor: "action", align: "center" },
    ],

    rows: [
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            BPL
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            SBA Back Parking Lot
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            11
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            COJ
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Siding Spring Observatory, New South Wales, Australia
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            27
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            CPT
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            South African Astronomical Observatory, South Africa
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            26
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            ELP
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            MacDonald Observatory, Fort Davis, TX, USA
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            24
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            LJG
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Lijiang, Yunnan, China
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            2
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            LSC
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Cerro-Tololo International Observatory, La Serena, Chile
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            32
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            MFG
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            SBA Manufacturing Test Site
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            2
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            OGG
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Haleakala, Maui, Hawaii, USA
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            29
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
      {
        sitecode: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            SBA
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            LCO Global Headquarters, Goleta, CA
          </MDTypography>
        ),
        count: (
          <MDBox ml={-1}>
            123
          </MDBox>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Add Device
          </MDTypography>
        ),
      },
    ],
  };
}
