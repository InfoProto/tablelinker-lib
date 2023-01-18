from ..core import filters

from . import (
    geocoder,
    mapping_col,
    mtab,
    wareki,
)

selectable_filters = (
    geocoder.ToCodeFilter,
    geocoder.ToPrefectureFilter,
    geocoder.ToMunicipalitiesFilter,
    geocoder.ToLongitudeFilter,
    geocoder.ToLatitudeFilter,
    geocoder.ToLatLongFilter,
    mapping_col.AutoMappingColsFilter,
    mtab.MtabFilter,
    wareki.ToSeirekiFilter,
)


def register():
    for filter in selectable_filters:
        filters.registry_filter(filter)
