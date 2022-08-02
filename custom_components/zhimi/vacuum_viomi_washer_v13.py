from ..zhimi.entity import ZhiMiEntity
from .viomi_washer_v13 import *
from asyncio import sleep
from homeassistant.components.vacuum import SUPPORT_CLEAN_SPOT, SUPPORT_FAN_SPEED, SUPPORT_LOCATE, SUPPORT_PAUSE, SUPPORT_RETURN_HOME, SUPPORT_SEND_COMMAND, SUPPORT_START, SUPPORT_STATUS, SUPPORT_STOP, SUPPORT_TURN_OFF, SUPPORT_TURN_ON, VacuumEntity
from datetime import datetime, timedelta
import logging


_LOGGER = logging.getLogger(__name__)

APPOINT_MIN = 1  # 3 in app default
APPOINT_MAX = 23  # 19 in app default
DEFAULT_APPOINT_TIME = -8  # -8 means 8 o'clock, 8 means 8 hours later


Washer.IIDS = {
    'switch_status': Washer.Switch_Status,
    'mode': Washer.Mode,
    'target_temperature': Washer.Target_Temperature,
    'spin_speed': Washer.Spin_Speed,
    'drying_time': Washer.Drying_Time,
    'rinsh_times': Washer.Rinsh_Times,
    'speed_level': Washer.Speed_Level,
}

Washer_Status_Names = ZhiMiEntity.member_names(Washer_Status)
Washer_Mode_Names = ZhiMiEntity.member_names(Washer_Mode)

class ZhiMiVacuum(ZhiMiEntity, VacuumEntity):

    def __init__(self, conf):
        super().__init__(ALL_SVCS, conf, 'mdi:washing-machine')

    async def async_poll(self):
        data = await super().async_poll()
        self._status = Washer_Status_Names[data[Washer.Status]]
        if data[Washer.Status] == Washer_Status.Paused:
            self._status += '｜暂停'
        if data[Washer.Status] != Washer_Status.Off:
            left_time = data[Washer.Left_Time]
            if left_time:
                self._status += '｜剩%s分钟' % left_time
            drying_time = data[Washer.Drying_Time]
            if drying_time:
                self._status += '|' + Washer_Drying_Time(drying_time).name
            appoint_time = data[Washer.预约完成时间]
            if appoint_time:
                self._status += '｜预约%s' % datetime.fromtimestamp(appoint_time).strftime('%H:%M')
        return data

    @property
    def supported_features(self):
        return SUPPORT_STATUS | SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_FAN_SPEED | SUPPORT_START | SUPPORT_PAUSE | SUPPORT_STOP | SUPPORT_RETURN_HOME | SUPPORT_SEND_COMMAND | SUPPORT_CLEAN_SPOT | SUPPORT_LOCATE

    @property
    def status(self):
        return self._status

    async def async_update_status(self, status):
        self._status = status
        await self.async_update_ha_state()

    @property
    def is_on(self):
        return self.data[Washer.Status] != Washer_Status.Off

    async def async_turn_on(self, **kwargs):
        if self.data[Washer.Status] == Washer_Status.Idle:
            await self.async_update_status('已是待机状态')
        else:
            if self.data[Washer.Status] != Washer_Status.Off:
                await self.async_turn_off()
                await sleep(1)

            def success(siid, iid, value):
                self.data[Washer.Status] = Washer_Status.Idle
            await self.async_control(Washer.Switch_Status, True, '开机', success, True)

    async def async_turn_off(self, **kwargs):
        def success(siid, iid, value):
            self.data[Washer.Status] = Washer_Status.Off
        await self.async_control(Washer.Switch_Status, False, '关机', success, True)

    @property
    def fan_speed(self):
        return [self.data[Washer.Mode]]
        return Washer.Mode(self.data[Washer.Mode]).name

    @property
    def fan_speed_list(self):
        return [k for k in vars(Washer_Mode).keys() if not k.startswith('__')]

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        await self.async_control(Washer.Mode, self.fan_speed_list.index(fan_speed) + 1, '设定' + fan_speed + '模式')

    async def async_start(self):
        if self.data[Washer.Status] == Washer_Status.Busy:
            lock = not self.data[Physical_Control_Locked.Physical_Control_Locked]
            return await self.async_control(Physical_Control_Locked.Physical_Control_Locked, lock, '锁定' if lock else '解锁')
        if not self.is_on:
            await self.async_turn_on()
            await sleep(1)
        await self.async_action(Washer.Start_Wash, '启动')

    async def async_pause(self):
        if self.data[Washer.Status] == Washer_Status.Busy:
            await self.async_action(Washer.Pause, '暂停')
        else:
            await self.async_update_status('非工作状态，无法暂停')

    async def async_stop(self, **kwargs):
        if self.data[Washer.Status] == Washer_Status.Off:
            await self.async_update_status('已经是关机状态')
        else:
            await self.async_turn_off()

    async def async_return_to_base(self, **kwargs):
        await self.async_stop()

    async def async_send_command(self, command, params=None, **kwargs):
        for item in command.split(';'):
            parts = item.split('=', 1)
            count = len(parts)
            cmd = parts[0]
            if count > 1:
                value = parts[1][1:] if parts[1].startswith('$') else int(parts[1])
            async_cmd = 'async_' + cmd
            if hasattr(self, async_cmd):
                # turn_on/turn_off,start/pause/stop/return_to_base,locate/clean_spot
                # fanspeed=$[value],dry_mode|appoint[=value]
                async_func = getattr(self, async_cmd)
                await (async_func(value) if count > 1 else async_func())
            elif count > 1 and cmd in Washer.IIDS:
                prop = Washer.IIDS[cmd]
                code = await self.async_control(prop, value, '设定' + ALL_PROPS[prop])
                if code is None:
                    continue
                elif code == False:
                    return
            else:
                _LOGGER.error("Invalid speed format:%s", params)
                continue
            await sleep(1)

    async def async_action(self, aiid, op):
        await self.async_control(aiid, [self.data[Washer.Mode]], op, self.action_success)

    def action_success(self, siid, aiid, value):
        self.data[Washer.Status] = (Washer_Status.Busy, Washer_Status.Paused)[aiid == Washer.Start_Wash]

    async def async_clean_spot(self, **kwargs):
        if not self.is_on:
            await self.async_turn_on()
            await sleep(1)
        await self.async_dry_mode(0 if self.data[Washer.Drying_Time] else 1)

    async def async_locate(self, **kwargs):
        if not self.is_on:
            await self.async_turn_on()
            await sleep(1)
        await self.async_appoint()

    async def async_dry_mode(self, mode=1):
        await self.async_control(Washer.Drying_Time, Washer_Drying_Time.智能烘干 if mode == 1 else mode, ('设定' if mode else '取消') + '烘干模式')

    async def async_appoint(self, atime=DEFAULT_APPOINT_TIME):
        now = datetime.now()
        if atime < 0:
            aclock = -atime
            if now.hour > aclock:
                now += timedelta(days=1)
            status = '预约%s点钟完成洗衣' % aclock
            stamp = datetime(now.year, now.month, now.day, aclock).timestamp()
        else:
            status = '预约%s小时后完成洗衣' % atime
            stamp = now.timestamp() + atime * 60 * 60 * 1000
        await (self.async_control(自定义属性.预约完成时间戳, int(stamp), status) if atime else self.async_start())
