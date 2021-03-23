
from . import miio_service
from ..zhi.entity import ZhiPollEntity, ZHI_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol


CONF_DID = 'did'

ZHI_MIOT_SCHEMA = ZHI_SCHEMA | {vol.Required(CONF_DID): cv.string}


class ZhiMIoTEntity(ZhiPollEntity):

    def __init__(self, props, conf, icon=None):
        super().__init__(conf, icon)
        self.did = conf[CONF_DID]
        self.props = props

    async def async_poll(self):
        props = [(s, p) for s, v in self.props.items() for p in v]
        values = await miio_service.miot_get_props(self.did, props)
        data = {}
        for i in range(len(values)):
            p = props[i]
            if p[0] not in data:
                data[p[0]] = {}
            data[p[0]][p[1]] = values[i]
        return data

    @property
    def device_state_attributes(self):
        return {d: self.data[s][p] for s, v in self.props.items() if isinstance(v, dict) for p, d in v.items() if d}

    async def async_update_status(self, status):
        raise NotImplementedError

    async def mi_control(self, siid, piid, value=[]):
        return await miio_service.miot_control(self.did, siid, piid, value)

    async def async_control(self, siid, piid, value=[], doing=None):
        has_piid = piid > 0 and self.props and siid in self.data and piid in self.data[siid]
        if has_piid:
            if value is None:
                value = self.data[siid][piid]
            elif value == self.data[siid][piid]:
                doing and await self.async_update_status('当前已' + doing)
                return None
        doing and await self.async_update_status('正在' + doing)
        code = await self.mi_control(siid, piid, value)
        if code == 0:
            if has_piid:
                self.skip_poll = True
                self.data[siid][piid] = value
            if doing:
                await self.async_update_status(doing + '成功')
            elif has_piid:
                await self.async_update_ha_state()
            return True
        doing and await self.async_update_status(doing + '错误：%s' % code)
        return False
