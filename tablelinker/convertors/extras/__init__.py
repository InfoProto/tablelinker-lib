from ..core import filters

from . import (
    date_extract,
    geocoder,
    mapping_col,
    mtab,
    wareki,
)

selectable_filters = (
    date_extract.DateExtractFilter,
    date_extract.DatetimeExtractFilter,
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
