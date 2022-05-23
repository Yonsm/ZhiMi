
DOMAIN = 'zhimi'

mi_account = None
miio_service = None


async def async_setup(hass, config):
    conf = config.get(DOMAIN)
    global mi_account, miio_service
    from miservice import MiAccount, MiIOService
    mi_account = MiAccount(hass.helpers.aiohttp_client.async_get_clientsession(), conf['username'], conf['password'], hass.config.path(hass.helpers.storage.STORAGE_DIR, DOMAIN))
    miio_service = MiIOService(mi_account, conf.get('region'))
    return True
