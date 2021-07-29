
from . import miio_service
from ..zhi.entity import ZhiPollEntity, ZHI_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol


CONF_DID = 'did'
CONF_MODEL = 'model'

ZHI_MIOT_SCHEMA = ZHI_SCHEMA | {vol.Required(CONF_DID): cv.string}


class ZhiMIoTEntity(ZhiPollEntity):
    # 所有 piid 不重复时，使用 ZhiMIoTEntity，self.data 为一级 dict

    def __init__(self, props, conf, icon=None):
        super().__init__(conf, icon)
        self.did = conf[CONF_DID]
        self.props = props

    @property
    def device_state_attributes(self):
        return {d: self.get_prop(p, s) for s, v in self.props.items() if isinstance(v, dict) for p, d in v.items() if d}

    async def async_poll(self):
        props = [(s, p) for s, v in self.props.items() for p in v]
        values = await miio_service.miot_get_props(self.did, props)
        return self.make_data(props, values)

    async def async_control(self, siid, iid, value=[], op=None, success=None):
        has_prop = not isinstance(value, list) and self.has_prop(iid, siid)
        if has_prop:
            old_value = self.get_prop(iid, siid)
            if value is None:
                value = old_value
            elif value == old_value:
                op and await self.async_update_status('当前已' + op)
                return None
        op and await self.async_update_status('正在' + op)
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
        raise NotImplementedError

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

# TODO: Not Worked!
class ZhiMIoTEntity3(ZhiPollEntity):
    # 所有 piid 不重复时，使用 ZhiMIoTEntity，self.data 为一级 dict

    def __init__(self, spec, conf, icon=None):
        super().__init__(conf, icon)
        self.did = conf[CONF_DID]
        self.model = conf.get(CONF_MODEL)
        if self.model is None:
            self.spec = spec

    @property
    def device_state_attributes(self):
        return self.data

    async def load_spec(self, model):
        import json
        from os import path
        spec_path = path.join(path.dirname(path.abspath(__file__)), model + '.json')
        if path.exists(spec_path):
            try:
                with open(spec_path) as f:
                    spec = json.load(f)
            except Exception as e:
                spec = None
        else:
            spec = None
        if not spec:
            spec = self.filter_spec(await miio_service.miot_spec_for_model(model, 'lite'))
            with open(spec_path, 'w') as f:
                f.write(spec)
        return spec

    async def filter_spec(self, spec):
        return spec

    async def async_poll(self):
        if self.model is not None:
            self.spec = await self.load_spec(self.model)
            self.model = None

        props = [(v['iid'], p, d) for s, v in self.spec.items() for d, p in v.items() if d != 'iid' and not d.startswith('@') and p >= 0]
        if not props:
            return {}
        values = await miio_service.miot_get_props(self.did, props)
        return {props[i][2]: values[i] for i in range(len(values))}

    async def async_control(self, srv, key, value=[], op=None, success=None):
        if isinstance(value, list):
            key = '@' + key
            has_prop = False
        else:
            key = key + '='
            has_prop = key in self.data
        if has_prop:
            old_value = self.data[key]
            if value is None:
                value = old_value
            elif value == old_value:
                op and await self.async_update_status('当前已' + op)
                return None
        op and await self.async_update_status('正在' + op)
        code = await self.mi_control(self.spec[srv]['iid'], abs(self.spec[srv][key]), value)
        if code == 0:
            self.skip_poll = True
            if has_prop:
                self.data[key] = value
            if success:
                success(srv, key, value)
            if op:
                await self.async_update_status(op + '成功')
            else:
                await self.async_update_ha_state()
            return True
        op and await self.async_update_status(op + '错误：%s' % code)
        return False

    async def async_update_status(self, status):
        raise NotImplementedError

    async def mi_control(self, siid, iid, value=[]):
        return await miio_service.miot_control(self.did, siid, iid, value)
