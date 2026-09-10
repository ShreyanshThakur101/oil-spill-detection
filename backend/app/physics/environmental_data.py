"""
Environmental data reader module for CMEMS (ocean currents) and ERA5 (wind) NetCDF files.
"""
from pathlib import Path
from ..config import DATA_DIR

ENV_DATA_DIR = DATA_DIR / "raw" / "environmental"


def get_current_reader(case_id: str):
    """
    Get OpenDrift reader for cached ocean current NetCDF file.
    """
    path = ENV_DATA_DIR / f"{case_id}_currents.nc"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached current data: {path}. Run environmental data prep first.")
    from opendrift.readers import reader_netCDF_CF_generic
    return reader_netCDF_CF_generic.Reader(str(path))


def get_wind_reader(case_id: str):
    """
    Get OpenDrift reader for cached wind NetCDF file.
    """
    path = ENV_DATA_DIR / f"{case_id}_wind.nc"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached wind data: {path}. Run environmental data prep first.")
    from opendrift.readers import reader_netCDF_CF_generic
    return reader_netCDF_CF_generic.Reader(str(path))
