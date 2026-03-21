import pytest
import server

class TestDataLoading:
    """
    Unit tests for load_clubs() and load_competitions().

    Issue #14: Add FileNotFoundError handling to data loading functions.
    Branch: improvement/file-not-found-handling

    Verifies that missing JSON files return empty lists instead of crashing.
    """

    @pytest.mark.parametrize("load_function", [
        server.load_clubs,
        server.load_competitions,
    ])
    def test_returns_empty_list_when_file_missing(self, monkeypatch, tmp_path, load_function):
        """
        If the JSON file is not found, the loading function should
        return an empty list rather than raising FileNotFoundError.
        Covers both load_clubs() and load_competitions().
        """
        monkeypatch.chdir(tmp_path)
        result = load_function()
        assert result == []
