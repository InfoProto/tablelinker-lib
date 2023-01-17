from ..core import filters, params


class StringContainSelectRowFilter(filters.Filter):
    """
    特定文字列で行を抽出するフィルターです。
    """

    class Meta:
        key = "select_string_contains"
        name = "行抽出フィルター"
        description = """
        指定された文字列が含まれる行を抽出します
        """
        help_text = """
        「対象列」に「文字列」に指定した文字が含まれる行以外を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_attr_idx", label="対象列", required=True),
            params.StringParam("query", label="文字列", required=True),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 0

    def process_record(self, record, context):
        idx = context.get_param("input_attr_idx")
        query = context.get_param("query")
        value = record[idx]
        if query in value:
            context.output(record)
