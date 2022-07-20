import React from 'react'
import GoogleMapReact from 'google-map-react'
import Icon from "@mui/material/Icon";

import './Map.css'


const LocationPin = ({ text }) => (
    <div className="pin">
      <Icon>location_on</Icon>
      <p className="pin-text">{text}</p>
    </div>
  )

const Map = ({ location, zoomLevel }) => (
    <div className="map">
  
      <div className="google-map">
        <GoogleMapReact
          bootstrapURLKeys={{ key: 'AIzaSyA62SeG2-exnCnaDucOV9EHpfAOxK0WO3o' }}
          defaultCenter={location}
          defaultZoom={zoomLevel}
        >
          <LocationPin
            lat={location.lat}
            lng={location.lng}
            text={location.address}
          />
        </GoogleMapReact>
      </div>
    </div>
)

export default Map