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

/** 
  All of the routes for the Material Dashboard 2 React are added here,
  You can add a new route, customize the routes and delete the routes here.

  Once you add a new route on this file it will be visible automatically on
  the Sidenav.

  For adding a new route you can follow the existing routes in the routes array.
  1. The `type` key with the `collapse` value is used for a route.
  2. The `type` key with the `title` value is used for a title inside the Sidenav. 
  3. The `type` key with the `divider` value is used for a divider between Sidenav items.
  4. The `name` key is used for the name of the route on the Sidenav.
  5. The `key` key is used for the key of the route (It will help you with the key prop inside a loop).
  6. The `icon` key is used for the icon of the route on the Sidenav, you have to add a node.
  7. The `collapse` key is used for making a collapsible item on the Sidenav that has other routes
  inside (nested routes), you need to pass the nested routes inside an array as a value for the `collapse` key.
  8. The `route` key is used to store the route location which is used for the react router.
  9. The `href` key is used to store the external links location.
  10. The `title` key is only for the item with the type of `title` and its used for the title text on the Sidenav.
  10. The `component` key is used to store the component of its route.
*/

// Material Dashboard 2 React layouts
import Dashboard from "layouts/dashboard";
import Tables from "layouts/tables";
import Billing from "layouts/billing";
import RTL from "layouts/rtl";
import Notifications from "layouts/notifications";
import Profile from "layouts/profile";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import UnrecognizedDevices from "layouts/UnrecognizedDevices";
import CameraFinder from "layouts/CameraFinder";
import NetworkTools from "layouts/NetworkTools";
import PuppetTools from "layouts/PuppetTools";
import ExternalTools from "layouts/ExternalTools";
// @mui icons
import Icon from "@mui/material/Icon";

const routes = [
  {
    type: "collapse",
    name: "Home",
    key: "home",
    icon: <Icon fontSize="small">home</Icon>,
    route: "/home",
    component: <Dashboard />,
  },
  {
    type: "collapse",
    name: "Site Management",
    key: "sitemanagement",
    icon: <Icon fontSize="small">account_tree</Icon>,
    route: "/sitemanagement",
    component: <Tables />,
  },
  {
    type: "collapse",
    name: "Unrecognized Devices",
    key: "unrecognized",
    icon: <Icon fontSize="small">dns</Icon>,
    route: "/unrecogizedevices",
    component: <UnrecognizedDevices />,
  },
  {
    type: "collapse",
    name: "Camera Finder",
    key: "camera",
    icon: <Icon fontSize="small">camera_alt</Icon>,
    route: "/camerafinder",
    component: <CameraFinder />,
  },
  {
    type: "collapse",
    name: "Network Tools",
    key: "networktools",
    icon: <Icon fontSize="small">plumbing</Icon>,
    route: "/networktools",
    component: <NetworkTools />,
  },
  {
    type: "collapse",
    name: "Puppet Tools",
    key: "puppet",
    icon: <Icon fontSize="small">smart_toy</Icon>,
    route: "/puppet",
    component: <PuppetTools />,
  },
  {
    type: "collapse",
    name: "RQ Worker Dashboard",
    key: "RQ",
    icon: <Icon fontSize="small">engineering</Icon>,
    route: "/rq",
    component: <SignIn />,
  },
  {
    type: "collapse",
    name: "Internal Tools",
    key: "internaltools",
    icon: <Icon fontSize="small">extension</Icon>,
    route: "/internaltools",
    component: <Notifications />,
  },
  {
    type: "collapse",
    name: "External Tools",
    key: "externaltools",
    icon: <Icon fontSize="small">web_asset</Icon>,
    route: "/externaltools",
    component: <ExternalTools />,
  },
];

export default routes;
