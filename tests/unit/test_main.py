"""Unit tests for main.py — COUNTIES data integrity and _validate_coordinates."""

import pytest
from fastapi import HTTPException

from main import COUNTIES, _validate_coordinates

# ---------------------------------------------------------------------------
# Expected county names (alphabetical) for the Republic of Ireland
# ---------------------------------------------------------------------------

EXPECTED_COUNTY_NAMES = sorted(
    [
        "Carlow",
        "Cavan",
        "Clare",
        "Cork",
        "Donegal",
        "Dublin",
        "Galway",
        "Kerry",
        "Kildare",
        "Kilkenny",
        "Laois",
        "Leitrim",
        "Limerick",
        "Longford",
        "Louth",
        "Mayo",
        "Meath",
        "Monaghan",
        "Offaly",
        "Roscommon",
        "Sligo",
        "Tipperary",
        "Waterford",
        "Westmeath",
        "Wexford",
        "Wicklow",
    ]
)


# ---------------------------------------------------------------------------
# COUNTIES data integrity
# ---------------------------------------------------------------------------


class TestCountiesData:
    """Verify the COUNTIES constant contains all 26 Republic of Ireland counties."""

    def test_counties_has_26_entries(self):
        assert len(COUNTIES) == 26

    def test_each_county_has_required_keys(self):
        for county in COUNTIES:
            assert "name" in county, f"Missing 'name' key in {county}"
            assert "lat" in county, f"Missing 'lat' key in {county}"
            assert "lon" in county, f"Missing 'lon' key in {county}"

    def test_each_county_has_only_expected_keys(self):
        expected_keys = {"name", "lat", "lon"}
        for county in COUNTIES:
            assert set(county.keys()) == expected_keys, (
                f"Unexpected keys in {county['name']}: {set(county.keys()) - expected_keys}"
            )

    def test_county_names_match_expected(self):
        actual_names = sorted(c["name"] for c in COUNTIES)
        assert actual_names == EXPECTED_COUNTY_NAMES

    def test_no_duplicate_county_names(self):
        names = [c["name"] for c in COUNTIES]
        assert len(names) == len(set(names)), "Duplicate county names found"

    def test_county_names_are_strings(self):
        for county in COUNTIES:
            assert isinstance(county["name"], str)
            assert len(county["name"]) > 0

    def test_latitudes_within_ireland_range(self):
        """Ireland spans roughly 51.4N to 55.4N latitude."""
        for county in COUNTIES:
            assert 51.0 <= county["lat"] <= 56.0, (
                f"{county['name']} latitude {county['lat']} outside Ireland range"
            )

    def test_longitudes_within_ireland_range(self):
        """Ireland spans roughly 5.5W to 10.5W longitude."""
        for county in COUNTIES:
            assert -11.0 <= county["lon"] <= -5.5, (
                f"{county['name']} longitude {county['lon']} outside Ireland range"
            )

    def test_coordinates_are_floats(self):
        for county in COUNTIES:
            assert isinstance(county["lat"], float), (
                f"{county['name']} lat is {type(county['lat'])}, expected float"
            )
            assert isinstance(county["lon"], float), (
                f"{county['name']} lon is {type(county['lon'])}, expected float"
            )


# ---------------------------------------------------------------------------
# _validate_coordinates
# ---------------------------------------------------------------------------


class TestValidateCoordinates:
    """Verify _validate_coordinates raises HTTPException for out-of-range values."""

    def test_valid_coordinates_pass(self):
        """Valid Dublin coordinates should not raise."""
        _validate_coordinates(lat=53.3498, lon=-6.2603)

    def test_valid_zero_coordinates_pass(self):
        """Zero lat/lon (Gulf of Guinea) should be valid."""
        _validate_coordinates(lat=0.0, lon=0.0)

    # -- Boundary values (should pass) --

    def test_latitude_at_negative_90_passes(self):
        _validate_coordinates(lat=-90.0, lon=0.0)

    def test_latitude_at_positive_90_passes(self):
        _validate_coordinates(lat=90.0, lon=0.0)

    def test_longitude_at_negative_180_passes(self):
        _validate_coordinates(lat=0.0, lon=-180.0)

    def test_longitude_at_positive_180_passes(self):
        _validate_coordinates(lat=0.0, lon=180.0)

    def test_all_boundary_corners_pass(self):
        """All four extreme corners of the coordinate space."""
        for lat, lon in [(-90, -180), (-90, 180), (90, -180), (90, 180)]:
            _validate_coordinates(lat=float(lat), lon=float(lon))

    # -- Invalid latitude --

    def test_latitude_above_90_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=91.0, lon=0.0)
        assert exc_info.value.status_code == 400
        assert "Latitude" in exc_info.value.detail
        assert "91.0" in exc_info.value.detail

    def test_latitude_below_negative_90_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=-91.0, lon=0.0)
        assert exc_info.value.status_code == 400
        assert "Latitude" in exc_info.value.detail
        assert "-91.0" in exc_info.value.detail

    def test_latitude_extremely_high_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=999.0, lon=0.0)
        assert exc_info.value.status_code == 400

    # -- Invalid longitude --

    def test_longitude_above_180_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=0.0, lon=200.0)
        assert exc_info.value.status_code == 400
        assert "Longitude" in exc_info.value.detail
        assert "200.0" in exc_info.value.detail

    def test_longitude_below_negative_180_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=0.0, lon=-181.0)
        assert exc_info.value.status_code == 400
        assert "Longitude" in exc_info.value.detail
        assert "-181.0" in exc_info.value.detail

    # -- Invalid latitude checked first --

    def test_invalid_lat_and_lon_reports_latitude_error(self):
        """When both lat and lon are invalid, latitude should fail first."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_coordinates(lat=91.0, lon=200.0)
        assert exc_info.value.status_code == 400
        assert "Latitude" in exc_info.value.detail
