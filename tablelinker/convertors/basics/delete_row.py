from ..core import filters, params


class StringContainDeleteRowFilter(filters.Filter):
    """
    特定文字列で行を削除するフィルターです。
    """

    class Meta:
        key = "delete_string_contains"
        name = "行削除フィルター"
        description = """
        指定された文字列が含まれる行を除外します
        """
        help_text = """
        「対象列」に「文字列」に指定した文字が含まれる行を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam("attr", label="対象列", required=True),
            params.StringParam("query", label="文字列", required=True),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 0:
            return False
        return True

    def process_record(self, record, context):
        attr = context.get_param("attr")
        query = context.get_param("query")
        value = record[attr]
        if query not in value:
            context.output(record)
