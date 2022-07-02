
from . import miio_service
from ..zhi.entity import ZhiPollEntity, ZHI_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

import logging
_LOGGER = logging.getLogger(__name__)

CONF_DID = 'did'
CONF_MODEL = 'model'
CONF_IGNORE_STATE = 'ignore_state'

ZHI_MIOT_SCHEMA = ZHI_SCHEMA | {vol.Required(CONF_DID): cv.string, vol.Optional(CONF_IGNORE_STATE): bool}


class ZhiMIoTEntity(ZhiPollEntity):
    # 所有 piid 不重复时，使用 ZhiMIoTEntity，self.data 为一级 dict

    def __init__(self, props, conf, icon=None):
        super().__init__(conf, icon)
        self.did = conf[CONF_DID]
        self.ignore_state = conf.get(CONF_IGNORE_STATE, False)
        self.props = props

    @property
    def device_state_attributes(self):
        return {d: self.get_prop(p, s) for s, v in self.props.items() if isinstance(v, dict) for p, d in v.items() if d}

    async def async_poll(self):
        props = [(s, p) for s, v in self.props.items() for p in v]
        values = await miio_service.miot_get_props(self.did, props)
        return self.make_data(props, values)

    async def async_control(self, siid, iid, value=[], op=None, success=None, ignore_prop=False):
        self.skip_poll = True
        has_prop = not ignore_prop and not isinstance(value, list) and self.has_prop(iid, siid)
        if value is None:
            if has_prop:
                value =  self.get_prop(iid, siid)
            else:
                _LOGGER.error("No old value for %s/%s", siid, iid)
                op and await self.async_update_status(op + '异常')
                return None
        elif not self.ignore_state and has_prop and value == self.get_prop(iid, siid):
            _LOGGER.warn("Ignore same state value: %s", value)
            op and await self.async_update_status('当前已' + op)
            return None

        #op and await self.async_update_status('正在' + op)
        code = await self.mi_control(siid, iid, value)
        if code == 0:
            self.skip_poll = True
            if has_prop:
                self.set_prop(value, iid, siid)
            if success:
                success(siid, iid, value)
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

    async def mi_control(self, siid, iid, value=[]):
        return await miio_service.miot_control(self.did, siid, iid, value)

    def has_prop(self, piid, _=None):
        return piid in self.data

    def get_prop(self, piid, _=None):
        return self.data[piid]

    def set_prop(self, value, piid, _=None):
        self.data[piid] = value

    def make_data(self, props, values):
        return {props[i][1]: values[i] for i in range(len(values))}

# TODO: Not Worked!


class ZhiMIoTEntity2(ZhiMIoTEntity):
    # 多个服务中 piid 有重复时，使用 ZhiMIoTEntity2，self.data 为二级 dict

    def has_prop(self, piid, siid):
        return siid in self.data and piid in self.data[siid]

    def get_prop(self, piid, siid):
        return self.data[siid][piid]

    def set_prop(self, value, piid, siid):
        self.data[siid][piid] = value

    def make_data(self, props, values):
        data = {}
        for i in range(len(values)):
            p = props[i]
            if p[0] not in data:
                data[p[0]] = {}
            data[p[0]][p[1]] = values[i]
        return data
