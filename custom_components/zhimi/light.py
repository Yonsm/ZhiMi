
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from math import ceil
from ..zhimi.entity import ZhiMIoTEntity, ZHI_MIOT_SCHEMA

import logging
_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(ZHI_MIOT_SCHEMA | {
    vol.Optional('power_prop', default='power'): cv.string,
    vol.Optional('brightness_prop'): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ZhiMiLight(config)], True)


class ZhiMiLight(ZhiMIoTEntity, LightEntity):

    def __init__(self, conf):
        self.power_prop = conf['power_prop']
        self.brightness_prop = conf.get('brightness_prop')
        props = [self.power_prop]
        if self.brightness_prop is not None:
            props.append(self.brightness_prop)
        super().__init__(props, conf)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS if self.brightness_prop is not None else 0

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return (self.data[self.brightness_prop] * 255 / 100) if self.brightness_prop is not None else 100

    @property
    def is_on(self):
        power = self.data[self.power_prop]
        return power if '-' in self.power_prop else power == 'on'

    async def async_turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs and self.brightness_prop is not None:
            brightness = kwargs[ATTR_BRIGHTNESS]
            percent_brightness = ceil(100 * brightness / 255.0)
            if await self.async_control(self.brightness_prop, percent_brightness):
                self.data[self.brightness_prop] = percent_brightness
        else:
            await self.async_control(self.power_prop, True if '-' in self.power_prop else 'on')

    async def async_turn_off(self, **kwargs):
        await self.async_control(self.power_prop, False if '-' in self.power_prop else 'off')
