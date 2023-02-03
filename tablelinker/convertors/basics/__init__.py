from ..core import filters

from . import (
    calc_col,
    concat_col,
    concat_title,
    delete_col,
    delete_row,
    generate_pk,
    insert_col,
    mapping_col,
    move_col,
    rename_col,
    reorder_col,
    select_row,
    split_col,
    truncate,
    update_row,
    zenkaku,
)

selectable_filters = (
    calc_col.CalcColFilter,
    concat_col.ConcatColFilter,
    concat_col.ConcatColsFilter,
    concat_title.ConcatTitleFilter,
    delete_col.DeleteColFilter,
    delete_col.DeleteColsFilter,
    delete_row.StringMatchDeleteRowFilter,
    delete_row.StringContainDeleteRowFilter,
    delete_row.PatternMatchDeleteRowFilter,
    generate_pk.GeneratePkFilter,
    insert_col.InsertColFilter,
    insert_col.InsertColsFilter,
    mapping_col.MappingColsFilter,
    move_col.MoveColFilter,
    rename_col.RenameColFilter,
    rename_col.RenameColsFilter,
    reorder_col.ReorderColsFilter,
    select_row.StringMatchSelectRowFilter,
    select_row.StringContainSelectRowFilter,
    select_row.PatternMatchSelectRowFilter,
    split_col.SplitColFilter,
    split_col.SplitRowFilter,
    truncate.TruncateFilter,
    update_row.StringMatchUpdateRowFilter,
    update_row.StringContainUpdateRowFilter,
    update_row.PatternMatchUpdateRowFilter,
    zenkaku.ToHankakuFilter,
    zenkaku.ToZenkakuFilter,
)


def register():
    for filter in selectable_filters:
        filters.registry_filter(filter)
