import typing
from typing import Dict, Union, Optional
from pathlib import Path

import xarray as xr

from nwpc_data.grib._level import fix_level_type

from ._util import (
    _fill_parameter,
    _fill_level,
    _fill_level_type,
    _fill_level_value,
    _fill_index_path,
    _load_first_variable,
)


def load_field_from_file(
        file_path: Union[str, Path],
        parameter: Union[str, Dict],
        level_type: Union[str, Dict],
        level: Union[int, float] = None,
        with_index: Union[str, bool] = False,
) -> Optional[xr.DataArray]:
    """
    Load **one** field from GRIB2 file using [ecmwf/cfgrib](https://github.com/ecmwf/cfgrib).

    This function loads the first data fitting searching conditions.

    Parameters
    ----------
    file_path: str or Path
        GRIB2 file path
    parameter: str or typing.Dict
        parameter identifier. support two types:
        - str: parameter name, see shortName key using grib_ls of ecCodes.
        - typing.Dict: parameter keys, including:
            - discipline
            - parameterCategory
            - parameterNumber
    level_type: str or typing.Dict
        level type, see typeOfLevel key using grib_ls of ecCodes.
    level: int or float or None
        level value. If none, all levels will be loaded.
    with_index: str or bool
        use index file generated by cfgrib.
        if False, index file will not be used.
        if True, cfgrib will generate index file.

    Returns
    -------
    xr.DataArray or None:
        `xr.DataArray` if found one data, or None if not.

    Examples
    --------
    Read 850hPa temperature from a GRAEPS GFS grib2 file.
    >>> load_field_from_file(
   ...     file_path="/g1/COMMONDATA/OPER/NWPC/GRAPES_GFS_GMF/Prod-grib/2020031721/ORIG/gmf.gra.2020031800105.grb2",
   ...     parameter="t",
   ...     level_type="isobaricInhPa",
   ...     level=850,
   ... )
    <xarray.DataArray 't' (latitude: 720, longitude: 1440)>
    [1036800 values with dtype=float32]
    Coordinates:
        time           datetime64[ns] ...
        step           timedelta64[ns] ...
        isobaricInhPa  int64 ...
      * latitude       (latitude) float64 89.88 89.62 89.38 ... -89.38 -89.62 -89.88
      * longitude      (longitude) float64 0.0 0.25 0.5 0.75 ... 359.2 359.5 359.8
        valid_time     datetime64[ns] ...
    Attributes:
        GRIB_paramId:                             130
        GRIB_shortName:                           t
        GRIB_units:                               K
        GRIB_name:                                Temperature
        GRIB_cfName:                              air_temperature
        GRIB_cfVarName:                           t
        GRIB_dataType:                            fc
        GRIB_missingValue:                        9999
        GRIB_numberOfPoints:                      1036800
        GRIB_typeOfLevel:                         isobaricInhPa
        GRIB_NV:                                  0
        GRIB_stepUnits:                           1
        GRIB_stepType:                            instant
        GRIB_gridType:                            regular_ll
        GRIB_gridDefinitionDescription:           Latitude/longitude
        GRIB_Nx:                                  1440
        GRIB_iDirectionIncrementInDegrees:        0.25
        GRIB_iScansNegatively:                    0
        GRIB_longitudeOfFirstGridPointInDegrees:  0.0
        GRIB_longitudeOfLastGridPointInDegrees:   359.75
        GRIB_Ny:                                  720
        GRIB_jDirectionIncrementInDegrees:        0.25
        GRIB_jPointsAreConsecutive:               0
        GRIB_jScansPositively:                    0
        GRIB_latitudeOfFirstGridPointInDegrees:   89.875
        GRIB_latitudeOfLastGridPointInDegrees:    -89.875
        long_name:                                Temperature
        units:                                    K
        standard_name:                            air_temperature

    Load a filed without shortName.
    >>> load_field_from_file(
    ...     file_path="/g1/COMMONDATA/OPER/NWPC/GRAPES_GFS_GMF/Prod-grib/2020031721/ORIG/gmf.gra.2020031800105.grb2",
    ...     parameter={
    ...         "discipline": 0,
    ...         "parameterCategory": 2,
    ...         "parameterNumber": 225,
    ...     },
    ...     level_type="isobaricInhPa",
    ...     level=850,
    ... )
    <xarray.DataArray 'paramId_0' (latitude: 720, longitude: 1440)>
    [1036800 values with dtype=float32]
    Coordinates:
        time           datetime64[ns] ...
        step           timedelta64[ns] ...
        isobaricInhPa  int64 ...
      * latitude       (latitude) float64 89.88 89.62 89.38 ... -89.38 -89.62 -89.88
      * longitude      (longitude) float64 0.0 0.25 0.5 0.75 ... 359.2 359.5 359.8
        valid_time     datetime64[ns] ...
    Attributes:
        GRIB_paramId:                             0
        GRIB_dataType:                            fc
        GRIB_missingValue:                        9999
        GRIB_numberOfPoints:                      1036800
        GRIB_typeOfLevel:                         isobaricInhPa
        GRIB_NV:                                  0
        GRIB_stepUnits:                           1
        GRIB_stepType:                            instant
        GRIB_gridType:                            regular_ll
        GRIB_gridDefinitionDescription:           Latitude/longitude
        GRIB_Nx:                                  1440
        GRIB_iDirectionIncrementInDegrees:        0.25
        GRIB_iScansNegatively:                    0
        GRIB_longitudeOfFirstGridPointInDegrees:  0.0
        GRIB_longitudeOfLastGridPointInDegrees:   359.75
        GRIB_Ny:                                  720
        GRIB_jDirectionIncrementInDegrees:        0.25
        GRIB_jPointsAreConsecutive:               0
        GRIB_jScansPositively:                    0
        GRIB_latitudeOfFirstGridPointInDegrees:   89.875
        GRIB_latitudeOfLastGridPointInDegrees:    -89.875
        GRIB_discipline:                          0
        GRIB_parameterCategory:                   2
        GRIB_parameterNumber:                     225
        long_name:                                original GRIB paramId: 0
        units:                                    1


    """
    data_set = load_fields_from_file(
        file_path=file_path,
        parameter=parameter,
        level_type=level_type,
        level=level,
        with_index=with_index
    )

    if data_set is None:
        return None

    return _load_first_variable(data_set)


def load_fields_from_file(
        file_path: Union[str, Path],
        parameter: Union[str, Dict] = None,
        level_type: str = None,
        level: Union[int, float] = None,
        with_index: Union[str, bool] = False,
) -> Optional[xr.Dataset]:
    """
    Load fields from GRIB2 file using [ecmwf/cfgrib](https://github.com/ecmwf/cfgrib).

    Parameters
    ----------
    file_path: str or Path
        GRIB2 data file path
    parameter: str or typing.Dict
        see `load_message_from_file`
    level_type: str
        see `load_message_from_file`
    level: int or float or None
        see `load_message_from_file`
    with_index: str or bool
        see `load_message_from_file`

    Returns
    -------
    xr.Dataset or None:
        `xr.Dataset` if found, or None if not.

    Examples
    --------
    >>> load_fields_from_file(
    ...     file_path="/g1/COMMONDATA/OPER/NWPC/GRAPES_GFS_GMF/Prod-grib/2020031721/ORIG/gmf.gra.2020031800105.grb2",
    ...     parameter="t",
    ...     level_type="isobaricInhPa",
    ... )
    <xarray.Dataset>
    Dimensions:        (isobaricInhPa: 36, latitude: 720, longitude: 1440)
    Coordinates:
        time           datetime64[ns] ...
        step           timedelta64[ns] ...
      * isobaricInhPa  (isobaricInhPa) int64 1000 975 950 925 900 850 ... 5 4 3 2 1
      * latitude       (latitude) float64 89.88 89.62 89.38 ... -89.38 -89.62 -89.88
      * longitude      (longitude) float64 0.0 0.25 0.5 0.75 ... 359.2 359.5 359.8
        valid_time     datetime64[ns] ...
    Data variables:
        t              (isobaricInhPa, latitude, longitude) float32 ...
    Attributes:
        GRIB_edition:            2
        GRIB_centre:             babj
        GRIB_centreDescription:  Beijing
        GRIB_subCentre:          0
        Conventions:             CF-1.7
        institution:             Beijing
        history:                 2020-03-20T08:15:39 GRIB to CDM+CF via cfgrib-0....

    """
    filter_by_keys = {}
    read_keys = []

    if parameter is not None:
        _fill_parameter(parameter, filter_by_keys, read_keys)

    if level_type is not None:
        level_type = fix_level_type(level_type)
        _fill_level_type(level_type, filter_by_keys, read_keys)

    if level is not None:
        _fill_level_value(level, filter_by_keys, read_keys)

    backend_kwargs = {
        "filter_by_keys": filter_by_keys
    }
    if len(read_keys) > 0:
        backend_kwargs["read_keys"] = read_keys

    _fill_index_path(with_index, backend_kwargs)

    data_set = xr.open_dataset(
        file_path,
        engine="cfgrib",
        backend_kwargs=backend_kwargs
    )

    return data_set
