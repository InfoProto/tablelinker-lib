from ..core import filters

from . import (
    concat_col,
    split_col,
    truncate,
    zenkaku,
    select_row,
    delete_row,
    calc_col,
    rename_col,
    move_col,
    insert_col,
    delete_col,
    reorder_col,
)

selectable_filters = (
    truncate.TruncateFilter,
    concat_col.ConcatColFilter,
    split_col.SplitColFilter,
    split_col.PivotColFilter,
    zenkaku.ToHarfNumberFilter,
    select_row.StringContainSelectRowFilter,
    delete_row.StringContainDeleteRowFilter,
    calc_col.CalcColFilter,
    zenkaku.ToHarfSymbolFilter,
    zenkaku.ToWholeSymbolFilter,
    zenkaku.ToHarfAlphanumericFilter,
    zenkaku.ToWholeAlphanumericFilter,
    move_col.MoveColFilter,
    insert_col.InsertColFilter,
    rename_col.RenameColFilter,
    rename_col.RenameColsFilter,
    delete_col.DeleteColFilter,
    reorder_col.ReorderColsFilter,
)


def register():
    for filter in selectable_filters:
        filters.registry_filter(filter)
