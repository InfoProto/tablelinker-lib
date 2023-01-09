from ..core import filters

from . import (
    concat_col,
    split_col,
    truncate,
    wareki,
    zenkaku,
    select_row,
    delete_row,
    calc_col,
    geocoder,
    rename_col,
    move_col,
    insert_col,
    delete_col,
    mtab,
)

filters.registry_filter(truncate.TruncateFilter)
filters.registry_filter(concat_col.ConcatColFilter)
filters.registry_filter(split_col.SplitColFilter)
filters.registry_filter(split_col.PivotColFilter)
filters.registry_filter(wareki.ToSeirekiFilter)
filters.registry_filter(zenkaku.ToHarfNumberFilter)
filters.registry_filter(select_row.StringContainSelectRowFilter)
filters.registry_filter(delete_row.StringContainDeleteRowFilter)
filters.registry_filter(calc_col.CalcColFilter)
filters.registry_filter(zenkaku.ToHarfSymbolFilter)
filters.registry_filter(zenkaku.ToWholeSymbolFilter)
filters.registry_filter(zenkaku.ToHarfAlphanumericFilter)
filters.registry_filter(zenkaku.ToWholeAlphanumericFilter)
filters.registry_filter(move_col.MoveColFilter)
filters.registry_filter(move_col.SortColFilter, False)
filters.registry_filter(insert_col.InsertColFilter)
filters.registry_filter(insert_col.InsertColListFilter, False)
filters.registry_filter(rename_col.RenameColFilter)
filters.registry_filter(delete_col.DeleteColFilter)
filters.registry_filter(geocoder.ToGeocodeCodeFilter)
filters.registry_filter(geocoder.ToGeocodePrefectureFilter)
filters.registry_filter(geocoder.ToGeocodeMunicipalitiesFilter)
filters.registry_filter(geocoder.ToGeocodeLongitudeFilter)
filters.registry_filter(geocoder.ToGeocodeLatitudeFilter)
filters.registry_filter(mtab.MtabFilter)
