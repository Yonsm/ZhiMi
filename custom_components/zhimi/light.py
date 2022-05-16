
from .entity import ZhiMIoTEntity, ZHI_MIOT_SCHEMA
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(ZHI_MIOT_SCHEMA).extend({
    vol.Optional('siid', default=2): int,
    vol.Optional('piid', default=1): int,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ZhiMiLight(config)], True)


class ZhiMiLight(ZhiMIoTEntity, LightEntity):

    def __init__(self, conf):
        self.siid = conf['siid']
        self.piid = conf['piid']
        super().__init__({self.siid: [self.piid]}, conf)

    @property
    def is_on(self):
        return self.data[self.piid]

    async def async_turn_on(self, **kwargs):
        await self.async_control(self.siid, self.piid, True)

    async def async_turn_off(self, **kwargs):
        await self.async_control(self.siid, self.piid, False)
