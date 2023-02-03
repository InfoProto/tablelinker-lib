from ..core import convertors

from . import (
    date_extract,
    geocoder,
    mapping_col,
    mtab,
    wareki,
)

selectable_convertors = (
    date_extract.DateExtractConvertor,
    date_extract.DatetimeExtractConvertor,
    geocoder.ToCodeConvertor,
    geocoder.ToLatLongConvertor,
    geocoder.ToMunicipalityConvertor,
    geocoder.ToNodeIdConvertor,
    geocoder.ToPostcodeConvertor,
    geocoder.ToPrefectureConvertor,
    mapping_col.AutoMappingColsConvertor,
    mtab.MtabWikilinkConvertor,
    wareki.ToSeirekiConvertor,
    wareki.ToWarekiConvertor,
)


def register():
    for convertor in selectable_convertors:
        convertors.registry_convertor(convertor)
