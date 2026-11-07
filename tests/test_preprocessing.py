"""Tests du nettoyage des données."""

import pandas as pd
import pytest

from immo_price.preprocessing import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    clean_dvf,
    split_by_year,
)


def test_clean_keeps_only_valid_apartments(raw_df) -> None:
    clean = clean_dvf(raw_df)
    assert len(clean) == 2
    assert list(clean.columns) == [*FEATURE_COLUMNS, TARGET_COLUMN]


def test_clean_computes_price_per_m2(raw_df) -> None:
    clean = clean_dvf(raw_df)
    assert clean[TARGET_COLUMN].tolist() == [pytest.approx(6000)] * 2


def test_clean_normalizes_postal_code(raw_df) -> None:
    clean = clean_dvf(raw_df)
    assert set(clean["code_postal"]) == {"94270", "94120"}


def test_clean_extracts_year(raw_df) -> None:
    clean = clean_dvf(raw_df)
    assert sorted(clean["annee"].tolist()) == [2023, 2024]


@pytest.mark.parametrize("mutation_id", ["B", "C", "D", "E", "G", "H", "I"])
def test_clean_drops_invalid_mutation(raw_df, mutation_id) -> None:
    subset = raw_df[raw_df["id_mutation"] == mutation_id]
    result = clean_dvf(subset)
    assert result.empty
    assert list(result.columns) == [*FEATURE_COLUMNS, TARGET_COLUMN]


def test_clean_ignores_dependance_rows(raw_df) -> None:
    subset = raw_df[raw_df["id_mutation"] == "F"]
    assert len(clean_dvf(subset)) == 1


def test_split_by_year_uses_last_year_as_test() -> None:
    df = pd.DataFrame({"annee": [2022, 2023, 2024, 2024], "x": [1, 2, 3, 4]})
    train, test = split_by_year(df)
    assert set(train["annee"]) == {2022, 2023}
    assert set(test["annee"]) == {2024}


def test_split_by_year_with_explicit_test_year() -> None:
    df = pd.DataFrame({"annee": [2022, 2023, 2024]})
    train, test = split_by_year(df, test_year=2023)
    assert set(train["annee"]) == {2022}
    assert set(test["annee"]) == {2023}


def test_split_by_year_single_year_raises() -> None:
    df = pd.DataFrame({"annee": [2024, 2024]})
    with pytest.raises(ValueError):
        split_by_year(df)
