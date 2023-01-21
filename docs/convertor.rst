.. _convertor:

コンバータ
==========

コンバータは、表データを別の表データに変換する処理を表します。

Tablelinker では、列名の変更や列の削除、挿入などの操作、
特定の条件を満たす行の選択など、列や行に対する処理を行うものを
「基本コンバータ」、和暦・西暦変換やジオコーディングなど、
外部の知識を利用して表データに情報を追加したり表現を変換する
処理を行うものを「拡張コンバータ」と便宜上分類しています。

基本コンバータを利用するには外部の辞書等は不要ですが、
拡張コンバータを利用するには事前に辞書をダウンロードしたり、
利用時にインターネット接続が必要になります。


.. _basic_convertor:

基本コンバータ
--------------

以下の基本コンバータが利用可能です。

列操作
^^^^^^

.. autoclass::
    tablelinker.convertors.basics.calc_col.CalcColFilter

.. autoclass::
    tablelinker.convertors.basics.concat_col.ConcatColFilter

.. autoclass::
    tablelinker.convertors.basics.delete_col.DeleteColFilter

行操作
^^^^^^

.. autoclass::
    tablelinker.convertors.basics.delete_row.StringMatchDeleteRowFilter

.. autoclass::
    tablelinker.convertors.basics.delete_row.StringContainDeleteRowFilter

.. autoclass::
    tablelinker.convertors.basics.delete_row.PatternMatchDeleteRowFilter

.. autoclass::
    tablelinker.convertors.basics.insert_col.InsertColFilter

.. autoclass::
    tablelinker.convertors.basics.move_col.MoveColFilter

.. autoclass::
    tablelinker.convertors.basics.rename_col.RenameColFilter

.. autoclass::
    tablelinker.convertors.basics.rename_col.RenameColsFilter

.. autoclass::
    tablelinker.convertors.basics.reorder_col.ReorderColsFilter

.. autoclass::
    tablelinker.convertors.basics.select_row.StringMatchSelectRowFilter

.. autoclass::
    tablelinker.convertors.basics.select_row.StringContainSelectRowFilter

.. autoclass::
    tablelinker.convertors.basics.select_row.PatternMatchSelectRowFilter

.. autoclass::
    tablelinker.convertors.basics.split_col.SplitColFilter

.. autoclass::
    tablelinker.convertors.basics.split_col.PivotColFilter

.. autoclass::
    tablelinker.convertors.basics.truncate.TruncateFilter

.. autoclass::
    tablelinker.convertors.basics.zenkaku.ToHarfAlphanumericFilter

.. autoclass::
    tablelinker.convertors.basics.zenkaku.ToHarfNumberFilter

.. autoclass::
    tablelinker.convertors.basics.zenkaku.ToHarfSymbolFilter

.. autoclass::
    tablelinker.convertors.basics.zenkaku.ToWholeAlphanumericFilter

.. autoclass::
    tablelinker.convertors.basics.zenkaku.ToWholeSymbolFilter
