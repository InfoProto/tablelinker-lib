import re

from ..core import filters, params


class StringMatchDeleteRowFilter(filters.Filter):
    """
    概要
        指定した列が、指定した文字列と一致する行を削除します。

    コンバータ名
        "delete_string_match"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        表の 0 列目が空欄の行を削除します。

        .. code-block:: json

            {
                "convertor": "delete_string_match",
                "params": {
                    "input_attr_idx": 0,
                    "query": ""
                }
            }
    """

    class Meta:
        key = "delete_string_match"
        name = "行削除フィルター（一致）"
        description = """
        指定された列の値が文字列と一致する行を除外します
        """
        help_text = """
        「対象列」が「文字列」と一致する行を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="対象列", required=True),
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

    def initial_context(self, context):
        super().initial_context(context)
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.query = context.get_param("query")

    def process_record(self, record, context):
        if self.query != record[self.input_attr_idx]:
            context.output(record)


class StringContainDeleteRowFilter(filters.Filter):
    """
    概要
        指定した列に、指定した文字列を含む行を削除します。

    コンバータ名
        "delete_string_contains"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        表の 0 列目に「市」を含む行を削除します。

        .. code-block:: json

            {
                "convertor": "delete_string_contains",
                "params": {
                    "input_attr_idx": 0,
                    "query": "市"
                }
            }
    """

    class Meta:
        key = "delete_string_contains"
        name = "行削除フィルター（部分文字列）"
        description = """
        指定された文字列が含まれる行を除外します
        """
        help_text = """
        「対象列」に「文字列」に指定した文字が含まれる行を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="対象列", required=True),
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

    def initial_context(self, context):
        super().initial_context(context)
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.query = context.get_param("query")

    def process_record(self, record, context):
        if self.query not in record[self.input_attr_idx]:
            context.output(record)


class PatternMatchDeleteRowFilter(filters.Filter):
    """
    概要
        指定した列が指定した正規表現と一致する行を削除します。
        正規表現は列の先頭から一致（match）する必要があります。

    コンバータ名
        "delete_pattern_match"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "pattern": 正規表現 [必須]

    サンプル
        表の 0 列目が空欄、または末尾が「区部」「市」の行を
        削除します。

        .. code-block:: json

            {
                "convertor": "delete_pattern_match",
                "params": {
                    "input_attr_idx":0,
                    "pattern":"(^$|.+区部$|.+市$)"
                }
            }
    """

    class Meta:
        key = "delete_pattern_match"
        name = "行削除フィルター（正規表現）"
        description = """
        指定された列が指定した正規表現と一致する行を削除します
        """
        help_text = """
        「対象列」が「正規表現」に一致した行を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="対象列", required=True),
            params.StringParam("pattern", label="正規表現", required=True),
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

    def initial_context(self, context):
        super().initial_context(context)
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.re_pattern = re.compile(context.get_param('pattern'))

    def process_record(self, record, context):
        value = record[self.input_attr_idx]
        m = self.re_pattern.match(value)
        if m is None:
            context.output(record)
