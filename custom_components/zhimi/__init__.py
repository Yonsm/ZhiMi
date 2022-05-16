
import logging
DOMAIN = 'zhimi'

mi_account = None
miio_service = None


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    conf = config.get(DOMAIN)
    global mi_account, miio_service
    from miservice import MiAccount, MiIOService
    mi_account = MiAccount(hass.helpers.aiohttp_client.async_get_clientsession(), conf['username'], conf['password'], hass.config.path(hass.helpers.storage.STORAGE_DIR, DOMAIN))
    miio_service = MiIOService(mi_account, conf.get('region'))
    _LOGGER.debug("async_setup complete: %s", conf['username'])
    return True
