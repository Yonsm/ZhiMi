
from . import miio_service
from ..zhi.entity import ZhiPollEntity, ZHI_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

import logging
_LOGGER = logging.getLogger(__name__)

CONF_DID = 'did'
CONF_MODEL = 'model'
CONF_IGNORE_STATE = 'ignore_state'

ZHI_MIOT_SCHEMA = ZHI_SCHEMA | {
    vol.Required(CONF_DID): cv.string,
    vol.Optional(CONF_MODEL): cv.string,
    vol.Optional(CONF_IGNORE_STATE): bool
}


class ZhiMiEntity(ZhiPollEntity):

    def __init__(self, props, conf, icon=None):
        super().__init__(conf, icon)
        self.did = conf[CONF_DID]
        self.ignore_state = conf.get(CONF_IGNORE_STATE)
        self.props = {v: k for svc in props for k, v in vars(svc).items() if not k.startswith('__') and isinstance(v, tuple)} if isinstance(props, tuple) else props

    @property
    def device_state_attributes(self):
        return {d: self.data[p] for p, d in self.props.items() if d} if isinstance(self.props, dict) else None

    async def async_poll(self):
        props = list(self.props.keys()) if isinstance(self.props, dict) else self.props
        prop = props[0]
        if isinstance(prop, str) and not prop[0].isdigit():
            get_props = miio_service.home_get_props
        else:
            if isinstance(prop, str):
                props = list(map(lambda s: tuple(map(int, s.split('-'))), props))
            get_props = miio_service.miot_get_props
        values = await get_props(self.did, props)
        return {self.props[i]: values[i] for i in range(len(values))}

    async def async_control(self, prop, value=[], op=None, success=None, ignore_prop=False):
        has_prop = not ignore_prop and not isinstance(value, list) and prop in self.data
        if value is None:
            if has_prop:
                value = self.data[prop]
            else:
                _LOGGER.error("No old value for %s", prop)
                op and await self.async_update_status(op + '异常')
                return None
        elif not self.ignore_state and has_prop and value == self.data[prop]:
            _LOGGER.warn("Ignore same state value: %s", value)
            op and await self.async_update_status('当前已' + op)
            return None

        # op and await self.async_update_status('正在' + op)
        key = prop
        if isinstance(prop, str) and not prop[0].isdigit():
            control = miio_service.home_set_prop
        else:
            control = (miio_service.miot_action if isinstance(value, list) else miio_service.miot_set_prop)
            if isinstance(prop, str):
                prop = tuple(map(int, prop.split('-')))
        code = await control(self.did, prop, value)

        if code == 0:
            self.skip_poll = True
            if has_prop:
                self.data[key] = value
            if success:
                success(key, value)
            if op:
                await self.async_update_status(op + '成功')
            else:
                await self.async_update_ha_state()
            return True
        op and await self.async_update_status(op + '错误：%s' % code)
        return False

    async def async_update_status(self, status):
        _LOGGER.debug("async_update_status: %s", status)
        #raise NotImplementedError
