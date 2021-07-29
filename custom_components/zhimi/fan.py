# TODO: Not worked!
from . import miio_service
from .entity import ZhiMIoTEntity, CONF_DID, ZHI_MIOT_SCHEMA
from homeassistant.components.fan import FanEntity, PLATFORM_SCHEMA, SPEED_OFF, DIRECTION_REVERSE, DIRECTION_FORWARD, SUPPORT_PRESET_MODE, SUPPORT_PRESET_MODE, SUPPORT_DIRECTION, SUPPORT_OSCILLATE
from homeassistant.const import STATE_HOME, STATE_OFF, STATE_ON


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(ZHI_MIOT_SCHEMA)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ZhiMiFan(config)])


class ZhiMiFan(ZhiMIoTEntity, FanEntity):

    def __init__(self, conf):
        super().__init__(conf)

        self._speed = SPEED_OFF
        self._last_speed = None

        self._direction = DIRECTION_FORWARD
        self._oscillating = False

    @property
    def supported_features(self):
        return SUPPORT_PRESET_MODE | SUPPORT_OSCILLATE

    @property
    def state(self):
        return (STATE_ON, STATE_OFF)[self._speed == SPEED_OFF]

    @property
    def preset_modes(self):
        return list(self.command.get('speed_list').keys())

    @property
    def preset_mode(self):
        return self._speed

    @property
    def oscillating(self):
        return self._oscillating

    @property
    def current_direction(self):
        return self._direction

    async def async_turn_on(self, speed, **kwargs):
        if 'on' in self.command:
            await self.send_command('on')
            from asyncio import sleep
            sleep(1)
        if 'speed_list' in self.command:
            return self.set_speed(speed or self._last_speed or self.speed_list[1])
        self._speed = STATE_ON
        await self.async_update_ha_state()

    async def async_turn_off(self):
        self._speed = SPEED_OFF
        await self.async_command('off')

    async def async_set_preset_mode(self, speed):
        self._speed = speed
        if speed != SPEED_OFF:
            self._last_speed = speed
        await self.async_command('speed_list', speed)

    async def async_oscillate(self, oscillating):
        self._oscillating = oscillating
        await self.async_command('oscillate')

    async def async_set_direction(self, direction):
        self._direction = direction
        await self.async_command(direction)

    def update_from_last_state(self, state):
        attributes = state.attributes
        self._speed = attributes.get('speed', self._speed)
        #self._last_speed = attributes.get('last_speed', self._last_speed)
        self._direction = attributes.get('direction', self._direction)
        self._oscillating = attributes.get('oscillating', self._oscillating)

    def update_from_sensor(self, state):
        self._speed = (self._last_speed or self.speed_list[1] if 'speed_list' in self.command else STATE_ON) if state.state in [STATE_ON, STATE_HOME] else SPEED_OFF
