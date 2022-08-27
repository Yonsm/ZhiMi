from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_SENSORS, CONF_DEVICE


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    sensors = []
    for k, v in discovery_info[CONF_SENSORS].items():
        sensor = SensorEntity()
        sensor.sensor_id = k
        sensor._attr_name = v
        sensor._attr_should_poll = False
        device_class = sensor._attr_device_class = {'temp_dec': 'temperature', 'aqi': 'pm25', 'co2': 'carbon_dioxide'}.get(k, k)
        sensor._attr_native_unit_of_measurement = {'temperature': '°C', 'humidity': '%', 'pm25': 'µg/m³', 'carbon_dioxide': 'ppm'}.get(device_class)
        sensors.append(sensor)
    discovery_info[CONF_DEVICE].sensors = sensors
    async_add_entities(sensors, True)
