import requests
import urllib3
import io
import ssl


# TODO: FIX OpenSSL SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED
class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    '''Transport adapter" that allows us to use custom ssl_context.'''

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

session = get_legacy_session()

# /TODO: FIX OpenSSL SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED


def _headers():
    # Get a copy of the default headers that requests would use
    headers = requests.utils.default_headers()

    # Update the headers with your custom ones
    # You don't have to worry about case-sensitivity with
    # the dictionary keys, because default_headers uses a custom
    # CaseInsensitiveDict implementation within requests' source code.
    headers.update(
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0',
        }
    )

    return headers


def req_get(url):
    headers = _headers()

    req = session.get(url, headers=headers)
    req.raise_for_status()
    
    return req

def pandas_get(url):
    headers = _headers()

    req = session.get(url, headers=headers, stream=True)
    req.raise_for_status()

    req.raw.decode_content = True
    
    return req.raw

