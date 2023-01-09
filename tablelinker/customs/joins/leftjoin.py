from convertors.core import filters, params


class LeftJoinFilter(filters.Filter):
    """
    結合フィルター
    """

    class Meta:
        key = "leftjoin"  # Filterのキーになります。全体絵一意になる必要があります。
        name = "データソース結合"  # フィルターの名前です。画面に表示されます。
        description = "データセットに別のデータセットの列を結合します。"  # フィルターの名前です。画面に表示される予定です。
        help_text = None  # フィルターの使い方です。画面に表示される予定です。

        # フィルターで使用されるパラメータのリストです。
        params = params.ParamSet(
            params.InputAttributeParam("attr", label="結合元データセット　キー列", required=True),
            params.CollectionParam("target", label="結合対象データセット", group="target", required=True),
            params.AttributeParam(
                "target_key_attr", label="結合対象データセット　キー列", group="target", collection_param_name="target", required=True,
            ),
            params.OutputAttributeListParam(
                "target_attrs", label="対象データセット　出力列", collection_param_name="target", required=True,
            ),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 0

    def initial(self, context):
        # 結合対象のデータの呼び出し
        target = context.get_param("target")
        target_key_attr = context.get_param("target_key_attr")
        id_map = target.idmap(target_key_attr)  # idmapの生成
        context.set_data("id_map", id_map)
        context.set_data("target_headers", target.headers())

    def process_header(self, header, context):
        # データのヘッダの生成
        target_headers = context.get_data("target_headers")
        target_attrs = context.get_param("target_attrs")

        for target_attr in target_attrs:
            new_name = target_headers[target_attr]
            if new_name in header:
                new_name = "_" + new_name
            header.append(new_name)

        context.output(header)

    def process_record(self, record, context):
        # レコード毎の処理
        attr = context.get_param("attr")
        target_attrs = context.get_param("target_attrs")
        id_map = context.get_data("id_map")

        # 値を取り出して最後に追加
        for target_attr in target_attrs:
            value = id_map.get(record[attr])
            record.append(value if value is None else value[target_attr])

        context.output(record)  # 配列を渡してください。
