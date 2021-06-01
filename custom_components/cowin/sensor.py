"""Support for CoWIN Vaccination Tracker

configuration.yaml

sensor:
  - platform: cowin
    pincode: 600042
    scan_interval: 3600
"""
from datetime import timedelta,datetime
from cowin_api import CoWinAPI
import logging,codecs,time
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

from homeassistant.const import (
    CONF_RESOURCES
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=3600)

SENSOR_PREFIX = 'COWIN '
SENSOR_TYPES = {
    'center_id': ['Center ID', '', 'mdi:numeric']
}

CONF_PINCODE = "pincode"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PINCODE): cv.string,
        vol.Required(CONF_RESOURCES, default=[]):
            vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)])
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the CoWIN Vaccination sensor."""
    pin_code = config.get(CONF_PINCODE)
    date = datetime.today().strftime('%d-%m-%Y')

    cowin = CoWinAPI()
    data = cowin.get_availability_by_pincode(pin_code)

    entities = []
    for center_data in data['centers']:
        for entity_config in SENSOR_TYPES.keys():
            entities.append(CoWINSensor(center_data, entity_config, center_data['center_id']))

    add_entities(entities)

class CoWINSensor(Entity):
    """Representation of a CoWIN sensor."""

    def __init__(self, data, sensor_type, center_id):
        """Initialize the sensor."""
        _LOGGER.info("sensor_type %s", sensor_type)
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + str(center_id)
        self._unit = SENSOR_TYPES[sensor_type][1]
        self._state = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return SENSOR_TYPES[self.type][2]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.data

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        self._state = len(self.data['sessions'])
