from freestream_resolver.embed_chain import prepare_link
from freestream_resolver.models import ScrapeRequest


def test_prepare_link_dood_redirect():
    url = prepare_link("https://dood.so/e/abc123")
    assert url is not None
    assert "doodstream.com" in url


def test_scrape_request_defaults():
    req = ScrapeRequest(imdb_id="tt0111161", title="The Shawshank Redemption")
    assert req.media_type == "movie"
