
from .entity import ZhiMIoTEntity, ZHI_MIOT_SCHEMA
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS
import voluptuous as vol
from math import ceil

import logging
_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(ZHI_MIOT_SCHEMA).extend({
    vol.Optional('siid', default=2): int,
    vol.Optional('piid', default=1): int,
    vol.Optional('piid_brightness'): int,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ZhiMiLight(config)], True)


class ZhiMiLight(ZhiMIoTEntity, LightEntity):

    def __init__(self, conf):
        siid = conf['siid']
        piid = conf['piid']
        props = [piid]
        piid_brightness = conf.get('piid_brightness')
        if piid_brightness is not None:
            props.append(piid_brightness)
        super().__init__({siid: props}, conf)
        self.siid = siid
        self.piid = piid
        self.piid_brightness = piid_brightness
        _LOGGER.debug("ZhiMiLight: siid=%s, piid=%s", siid, piid)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS if self.piid_brightness is not None else 0

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self.data[self.piid_brightness] * 255 / 100 if self.piid_brightness is not None else 100

    @property
    def is_on(self):
        return self.data[self.piid]

    async def async_turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs and self.piid_brightness is not None:
            brightness = kwargs[ATTR_BRIGHTNESS]
            percent_brightness = ceil(100 * brightness / 255.0)
            if await self.async_control(self.siid, self.piid_brightness, percent_brightness):
                self.data[self.piid_brightness] = percent_brightness
        else:
            await self.async_control(self.siid, self.piid, True)

    async def async_turn_off(self, **kwargs):
        await self.async_control(self.siid, self.piid, False)
