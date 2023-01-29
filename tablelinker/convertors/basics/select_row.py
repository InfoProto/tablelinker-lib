import re

from ..core import filters, params


class StringMatchSelectRowFilter(filters.Filter):
    """
    概要
        指定した列が、指定した文字列と一致する行を選択します。

    コンバータ名
        "select_string_match"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        表の 0 列目が「東京都」の行を選択します。

        .. code-block :: json

            {
                "convertor": "select_string_match",
                "params": {
                    "input_attr_idx": 0,
                    "query": "東京都",
                }
            }

    """

    class Meta:
        key = "select_string_match"
        name = "行選択フィルター（一致）"
        description = """
        指定された列の値が文字列と一致する行を選択します
        """
        help_text = """
        「対象列」が「文字列」と一致する行を選択します（それ以外を削除します）。
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
        if query == value:
            context.output(record)


class StringContainSelectRowFilter(filters.Filter):
    """
    概要
        指定した列に、指定した文字列を含む行を選択します。

    コンバータ名
        "select_string_contains"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        表の 0 列目に「市」を含む行を選択します。

        .. code-block:: json

            {
                "convertor": "select_string_contains",
                "params": {
                    "input_attr_idx": 0,
                    "query": "市",
                }
            }

    """

    class Meta:
        key = "select_string_contains"
        name = "行選択フィルター（部分文字列）"
        description = """
        指定された文字列が含まれる行を選択します
        """
        help_text = """
        「対象列」に「文字列」に指定した文字が含まれる行を選択します（それ以外を削除します）。
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


class PatternMatchSelectRowFilter(filters.Filter):
    """
    概要
        指定した列が指定した正規表現と一致する行を選択します。
        正規表現は列の先頭から一致（match）する必要があります。

    コンバータ名
        "select_pattern_match"

    パラメータ
        * "input_attr_idx": 検索対象列の列番号または列名 [必須]
        * "pattern": 正規表現 [必須]

    サンプル
        表の 0 列目の末尾が「区部」「市」の行を選択します。

        .. code-block:: json

            {
                "convertor": "select_pattern_match",
                "params": {
                    "input_attr_idx":0,
                    "pattern":"(.+区部$|.+市$)"}
            }

    """

    class Meta:
        key = "select_pattern_match"
        name = "行選択フィルター（正規表現）"
        description = """
        指定された列が指定した正規表現と一致する行を選択します
        """
        help_text = """
        「対象列」が「正規表現」に一致した行を選択します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_attr_idx", label="対象列", required=True),
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
        self.re_pattern = re.compile(context.get_param('pattern'))

    def process_record(self, record, context):
        attr = context.get_param("input_attr_idx")
        value = record[attr]
        m = self.re_pattern.match(value)
        if m is not None:
            context.output(record)
