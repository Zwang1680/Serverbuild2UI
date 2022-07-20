import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";

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

    return {
        columns: [
          { Header: "Timestamp", accessor: "timestamp", align: "left" },
          { Header: "Site", accessor: "site", align: "left" },
          { Header: "MAC Address", accessor: "mac", align: "center" },
          { Header: "IP Address", accessor: "ip", align: "center" },
          { Header: "Actions", accessor: "actions", align: "center" },
        ],
    
        rows: [
        ],
      };
    }