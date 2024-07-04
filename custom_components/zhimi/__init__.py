
from miservice import MiAccount, MiIOService
from homeassistant.helpers import aiohttp_client, storage

DOMAIN = 'zhimi'

miio_service = MiIOService()


def load_account(conf, store, sesssion):
    miio_service.account = MiAccount(sesssion, conf['username'], conf['password'], store)


async def async_setup(hass, config):
    global miio_service
    conf = config.get(DOMAIN)
    store = hass.config.path(storage.STORAGE_DIR, DOMAIN)
    sesssion = aiohttp_client.async_get_clientsession(hass)
    #miio_service.account = MiAccount(sesssion, conf['username'], conf['password'], store)
    await hass.async_add_executor_job(load_account, conf, store, sesssion)
    return True
