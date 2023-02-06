import re

from ..core import convertors, params


class StringMatchUpdateRowConvertor(convertors.Convertor):
    """
    概要
        指定した列の値が指定した文字列と完全に一致する行の値を
        新しい文字列に置き換えます。部分一致は置き換えません。

    コンバータ名
        "update_string_match"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 検索文字列 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        表の 0 列目が「全　国」の場合、「全国」に変更します。

        .. code-block :: json

            {
                "convertor": "select_string_match",
                "params": {
                    "input_col_idx": 0,
                    "query": "全　国",
                    "new": "全国"
                }
            }

    """

    class Meta:
        key = "update_string_match"
        name = "行の値を変更（完全一致）"
        description = """
        指定された列の値が文字列と完全一致する場合に変更します
        """
        help_text = """
        「対象列」の値が「文字列」と完全一致する場合、
        「新しい文字列」に変更します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="対象列",
                required=True
            ),
            params.StringParam(
                "query",
                label="文字列",
                required=True
            ),
            params.StringParam(
                "new",
                label="新しい文字列",
                required=True
            )
        )

    def preproc(self, context):
        super().preproc(context)
        self.idx = context.get_param("input_col_idx")
        self.query = context.get_param("query")
        self.new_value = context.get_param("new")

    def process_record(self, record, context):
        value = record[self.idx]
        if self.query == value:
            record[self.idx] = self.new_value

        context.output(record)


class StringContainUpdateRowConvertor(convertors.Convertor):
    """
    概要
        指定した列の値が指定した文字列を含む場合、
        その部分を新しい文字列に置き換えます。

    コンバータ名
        "update_string_contains"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 検索文字列 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        表の 0 列目が「（その他）」を含む場合、「他」に変更します。

        .. code-block :: json

            {
                "convertor": "update_string_contains",
                "params": {
                    "input_col_idx": 0,
                    "query": "（その他）",
                    "new": "他"
                }
            }

    """

    class Meta:
        key = "update_string_contains"
        name = "行の値を変更（部分一致）"
        description = """
        指定された列の値が文字列と部分一致する場合に変更します
        """
        help_text = """
        「対象列」の値の一部が「文字列」に一致する場合、
        一致した部分を「新しい文字列」に変更します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="対象列",
                required=True
            ),
            params.StringParam(
                "query",
                label="文字列",
                required=True
            ),
            params.StringParam(
                "new",
                label="新しい文字列",
                required=True
            )
        )

    def preproc(self, context):
        super().preproc(context)
        self.idx = context.get_param("input_col_idx")
        self.query = context.get_param("query")
        self.new_value = context.get_param("new")

    def process_record(self, record, context):
        value = record[self.idx]
        if self.query in value:
            # すべての出現箇所を置換
            record[self.idx] = value.replace(
                self.query, self.new_value)

        context.output(record)


class PatternMatchUpdateRowConvertor(convertors.Convertor):
    """
    概要
        指定した列の値が指定した正規表現と一致する場合、
        一致した部分を新しい文字列に置き換えます。
        正規表現は列の途中が一致しても対象となります（search）。

    コンバータ名
        "update_pattern_match"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "pattern": 正規表現 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        表の 0 列目が「～市〇〇区」の場合、「〇〇区」の部分を
        "" と置き換え（削除）します。

        .. code-block:: json

            {
                "convertor": "udpate_pattern_match",
                "params": {
                    "input_col_idx":0,
                    "pattern":"(?<=^市).+区$",
                    "new": ""
                }
            }

    """

    class Meta:
        key = "update_pattern_match"
        name = "行の値を変更（正規表現）"
        description = """
        指定された列の値が指定した正規表現と一致する場合に変更します
        """
        help_text = """
        「対象列」の値の一部が「正規表現」に一致する場合、
        一致した部分を「新しい文字列」に変更します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="対象列",
                required=True
            ),
            params.StringParam(
                "pattern",
                label="正規表現",
                required=True
            ),
            params.StringParam(
                "new",
                label="新しい文字列",
                required=True
            )
        )

    def preproc(self, context):
        super().preproc(context)
        self.idx = context.get_param("input_col_idx")
        self.re_pattern = re.compile(context.get_param('pattern'))
        self.new_value = context.get_param("new")

    def process_record(self, record, context):
        record[self.idx] = self.re_pattern.sub(
            self.new_value, record[self.idx])

        context.output(record)
