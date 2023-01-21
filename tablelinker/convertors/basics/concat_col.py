from ..core import filters, params


def concat(value_list, separator=""):
    """文字列を結合します。
    value_list: 対象の文字列リスト
    separator: 区切り文字
    """

    if separator is None:
        separator = ""

    str_value_list = [str(value) for value in value_list]
    return separator.join(str_value_list)


class ConcatColFilter(filters.Filter):
    """
    概要
        2つの入力列の文字列を結合し、結果を出力列に保存します。

    コンバータ名
        "concat"

    パラメータ
        * "input_attr_idx1": 入力列1の列番号または列名 [必須]
        * "input_attr_idx2": 入力列2の列番号または列名 [必須]
        * "output_attr_name": 出力列名 [必須]
        * "separator": 区切り文字 [""]
        * "delete_col": 入力列を削除するか （true/false） [false]

    注釈
        - 出力列名が元の表に存在している場合、その列に上書きします。
        - 存在していなかった場合、最後に新しい列が追加されます。

    サンプル
        表の「姓」列と「名」列を空白で結合し、結果を「姓名」列に
        出力します。

        .. code-block:: json

            {
                "convertor": "concat",
                "params": {
                    "input_attr_idx1": "姓",
                    "input_attr_idx2": "名",
                    "separator": " ",
                    "output_attr_name": "姓名",
                    "delete_col": true
                }
            }

    """

    class Meta:
        key = "concat"
        name = "列結合"

        description = """
        指定した列を結合します
        """

        help_text = """
        結合した列は、最後に追加されます。
        """

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx1", label="対象列1", required=True),
            params.InputAttributeParam("input_attr_idx2", label="対象列2", required=True),
            params.OutputAttributeParam("output_attr_name", label="新しい列名"),
            params.StringParam("separator", label="区切り文字", default_value=""),
            params.BooleanParam("delete_col", label="元の列を消しますか？", default_value=False),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 2:
            return False
        return True

    def process_header(self, headers, context):
        attr1 = context.get_param("input_attr_idx1")
        attr2 = context.get_param("input_attr_idx2")
        output_attr_name = context.get_param("output_attr_name")
        delete_col = context.get_param("delete_col")

        if output_attr_name is None:
            output_attr_name = "+".join([headers[attr1], headers[attr2]])

        headers = headers + [output_attr_name]

        if delete_col:
            headers.pop(attr1)
            if attr1 > attr2:
                headers.pop(attr2)
            elif attr1 < attr2:
                headers.pop(attr2 - 1)

        context.output(headers)

    def process_record(self, record, context):
        attr1 = context.get_param("input_attr_idx1")
        attr2 = context.get_param("input_attr_idx2")
        separator = context.get_param("separator")
        delete_col = context.get_param("delete_col")

        value_list = [record[attr1], record[attr2]]
        concated_value = concat(value_list, separator=separator)

        record.append(concated_value)

        if delete_col:
            record.pop(attr1)
            if attr1 > attr2:
                record.pop(attr2)
            elif attr1 < attr2:
                record.pop(attr2 - 1)

        context.output(record)
