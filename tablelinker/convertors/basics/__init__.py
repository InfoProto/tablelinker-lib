from ..core import convertors

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

selectable_convertors = (
    calc_col.CalcColConvertor,
    concat_col.ConcatColConvertor,
    concat_col.ConcatColsConvertor,
    concat_title.ConcatTitleConvertor,
    delete_col.DeleteColConvertor,
    delete_col.DeleteColsConvertor,
    delete_row.StringMatchDeleteRowConvertor,
    delete_row.StringContainDeleteRowConvertor,
    delete_row.PatternMatchDeleteRowConvertor,
    generate_pk.GeneratePkConvertor,
    insert_col.InsertColConvertor,
    insert_col.InsertColsConvertor,
    mapping_col.MappingColsConvertor,
    move_col.MoveColConvertor,
    rename_col.RenameColConvertor,
    rename_col.RenameColsConvertor,
    reorder_col.ReorderColsConvertor,
    select_row.StringMatchSelectRowConvertor,
    select_row.StringContainSelectRowConvertor,
    select_row.PatternMatchSelectRowConvertor,
    split_col.SplitColConvertor,
    split_col.SplitRowConvertor,
    truncate.TruncateConvertor,
    update_row.StringMatchUpdateRowConvertor,
    update_row.StringContainUpdateRowConvertor,
    update_row.PatternMatchUpdateRowConvertor,
    zenkaku.ToHankakuConvertor,
    zenkaku.ToZenkakuConvertor,
)


def register():
    for convertor in selectable_convertors:
        convertors.registry_convertor(convertor)
