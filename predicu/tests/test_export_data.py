import predicu.data as icubam_data
from predicu.tests.utils import load_test_data


def make_monkeypatch_load_bedcounts(data):
    def monkeypatch_load_bedcounts(*args, **kwargs):
        return data

    return monkeypatch_load_bedcounts


def test_export_data(tmpdir, monkeypatch):
    cached_data = load_test_data()
    monkeypatch.setattr(
        icubam_data,
        "load_bedcounts",
        make_monkeypatch_load_bedcounts(cached_data["bedcounts"]),
    )
    from predicu.__main__ import export_data

    test_args = dict(
        output_dir=str(tmpdir),
        api_key="test_api_key",
        max_date=None,
        icubam_host="localhost",
        spread_cum_jump_correction=False,
    )
    export_data(**test_args)
