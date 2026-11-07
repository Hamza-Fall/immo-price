"""Tests du téléchargement et du chargement des données."""

from pathlib import Path

import pandas as pd
import pytest
import requests

from immo_price import data_loading
from immo_price.config import get_settings
from immo_price.data_loading import USECOLS, build_url, download_dvf, load_raw


class FakeResponse:
    """Fausse réponse HTTP."""

    def __init__(self, content: bytes = b"donnees", fail: bool = False) -> None:
        self.content = content
        self.fail = fail

    def raise_for_status(self) -> None:
        if self.fail:
            raise requests.HTTPError("404 Not Found")


def write_csv_gz(path: Path, rows: int = 2) -> None:
    """Écrit un petit CSV compressé avec les colonnes utiles + une en trop."""
    data = {column: ["1"] * rows for column in USECOLS}
    data["colonne_inutile"] = ["x"] * rows
    pd.DataFrame(data).to_csv(path, index=False, compression="gzip")


def test_build_url() -> None:
    url = build_url(2024, "94")
    assert url == (
        "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/departements/94.csv.gz"
    )


def test_download_dvf_downloads_missing_file(monkeypatch, tmp_path) -> None:
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return FakeResponse(b"contenu")

    monkeypatch.setattr(requests, "get", fake_get)
    paths = download_dvf("94", [2023, 2024], tmp_path / "data")
    assert len(calls) == 2
    assert [p.name for p in paths] == ["dvf_94_2023.csv.gz", "dvf_94_2024.csv.gz"]
    assert paths[0].read_bytes() == b"contenu"


def test_download_dvf_skips_existing_file(monkeypatch, tmp_path) -> None:
    (tmp_path / "dvf_94_2024.csv.gz").write_bytes(b"deja la")

    def fail_get(url, timeout):
        raise AssertionError("Aucun téléchargement attendu")

    monkeypatch.setattr(requests, "get", fail_get)
    paths = download_dvf("94", [2024], tmp_path)
    assert paths == [tmp_path / "dvf_94_2024.csv.gz"]


def test_download_dvf_propagates_http_error(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(requests, "get", lambda url, timeout: FakeResponse(fail=True))
    with pytest.raises(requests.HTTPError):
        download_dvf("94", [2024], tmp_path)


def test_load_raw_concatenates_and_keeps_useful_columns(tmp_path) -> None:
    first = tmp_path / "a.csv.gz"
    second = tmp_path / "b.csv.gz"
    write_csv_gz(first, rows=2)
    write_csv_gz(second, rows=3)
    df = load_raw([first, second])
    assert len(df) == 5
    assert list(df.columns) == USECOLS


def test_load_raw_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_raw([tmp_path / "absent.csv.gz"])


def test_load_raw_empty_list() -> None:
    with pytest.raises(ValueError):
        load_raw([])


def test_main_calls_download(monkeypatch, tmp_path) -> None:
    captured = {}

    def fake_download(departement, years, dest_dir):
        captured["args"] = (departement, years, dest_dir)
        return []

    monkeypatch.setattr(data_loading, "download_dvf", fake_download)
    monkeypatch.setenv("IMMO_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        "sys.argv", ["immo-download", "--departement", "75", "--years", "2024"]
    )
    get_settings.cache_clear()
    data_loading.main()
    get_settings.cache_clear()
    assert captured["args"] == ("75", [2024], tmp_path)
