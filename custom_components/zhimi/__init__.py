from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .micom.miauth import MiAuth
from .micom.miiocom import MiIOCom
from homeassistant.helpers.storage import STORAGE_DIR

import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhimi'

_miauth = None
_miiocom = None


async def async_setup(hass, config):
    conf = config.get(DOMAIN)
    global _miauth, _miiocom
    # TODO: new aiohttp session?
    # TODO: Use session context?
    _miauth = MiAuth(async_get_clientsession(hass), conf['username'], conf['password'], hass.config.path(STORAGE_DIR, DOMAIN))
    _miiocom = MiIOCom(_miauth, conf.get('region'))
    return True


def get_miiocom():
    return _miiocom
