from ml_service.api.routers.predict import _validate_item


class TestValidateItem:
    def test_dict_with_keys_is_valid(self) -> None:
        assert _validate_item({"x": 1}) == []

    def test_empty_dict_is_rejected(self) -> None:
        errors = _validate_item({})
        assert errors == ["object must not be empty"]

    def test_non_dict_is_rejected(self) -> None:
        for bad in [None, 1, "str", [1, 2], 1.5, True]:
            assert _validate_item(bad) == ["expected JSON object"]
