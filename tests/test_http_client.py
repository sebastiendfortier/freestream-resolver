from freestream_resolver.http_client import KODI_UA, flaresolverr_url


def test_kodi_ua_present():
    assert "Mozilla" in KODI_UA


def test_flaresolverr_default_url():
    assert flaresolverr_url().endswith("/v1")
