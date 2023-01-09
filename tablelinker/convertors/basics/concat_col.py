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
    文字列を結合します。
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
            params.OutputAttributeParam("output_attr_name", label="新しい列名"),
            params.InputAttributeParam("attr1", label="対象列1", required=True),
            params.InputAttributeParam("attr2", label="対象列2", required=True),
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
        attr1 = context.get_param("attr1")
        attr2 = context.get_param("attr2")
        output_attr_name = context.get_param("output_attr_name")
        delete_col = context.get_param("delete_col")

        if output_attr_name is None:
            output_attr_name = "+".join([headers[attr1], headers[attr2]])

        headers = headers + [output_attr_name]

        if delete_col:
            headers.pop(attr1)
            if attr1 != attr2:
                headers.pop(attr2)

        context.output(headers)

    def process_record(self, record, context):
        attr1 = context.get_param("attr1")
        attr2 = context.get_param("attr2")
        separator = context.get_param("separator")
        delete_col = context.get_param("delete_col")

        value_list = [record[attr1], record[attr2]]
        concated_value = concat(value_list, separator=separator)

        record.append(concated_value)

        if delete_col:
            record.pop(attr1)
            if attr1 != attr2:
                record.pop(attr2)

        context.output(record)
