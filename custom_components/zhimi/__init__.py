from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.aiohttp_client import async_get_clientsession

REQUIREMENTS = ['miservice>=2021.3.1']

DOMAIN = 'zhimi'

_mi_account = None
_miio_service = None


async def async_setup(hass: HomeAssistant, config):
    conf = config.get(DOMAIN)
    global _mi_account, _miio_service
    from miservice import MiAccount, MiIOService
    _mi_account = MiAccount(async_get_clientsession(hass), conf['username'], conf['password'], hass.config.path(STORAGE_DIR, DOMAIN))
    _miio_service = MiIOService(_mi_account, conf.get('region'))
    return True


def get_miio_service():
    return _miio_service
