from ..core import filters

from . import (
    geocoder,
    mapping_col,
    mtab,
    wareki,
)

selectable_filters = (
    geocoder.ToCodeFilter,
    geocoder.ToLatLongFilter,
    geocoder.ToMunicipalityFilter,
    geocoder.ToNodeIdFilter,
    geocoder.ToPostcodeFilter,
    geocoder.ToPrefectureFilter,
    mapping_col.AutoMappingColsFilter,
    mtab.MtabWikilinkFilter,
    wareki.ToSeirekiFilter,
    wareki.ToWarekiFilter,
)


def register():
    for filter in selectable_filters:
        filters.registry_filter(filter)
