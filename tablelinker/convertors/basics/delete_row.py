import re

from tablelinker.core import convertors, params


class StringMatchDeleteRowConvertor(convertors.Convertor):
    r"""
    概要
        指定した列が、指定した文字列と一致する行を削除します。

    コンバータ名
        "delete_row_match"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        「性別」列が「女」の行を削除します。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "delete_row_match",
                "params": {
                    "input_col_idx": "性別",
                    "query": "女"
                }
            }

        - コード例

        .. code-block:: python

            >>> # データはランダム生成
            >>> from tablelinker import Table
            >>> table = Table(data=(
            ...     '"氏名","生年月日","性別","クレジットカード"\n'
            ...     '"小室 友子","1990年06月20日","女","3562635454918233"\n'
            ...     '"江島 佳洋","1992年10月07日","男","376001629316609"\n'
            ...     '"三沢 大志","1995年02月13日","男","4173077927458449"\n'
            ... ))
            >>> table = table.convert(
            ...     convertor="delete_row_match",
            ...     params={
            ...         "input_col_idx": "性別",
            ...         "query": "女",
            ...     },
            ... )
            >>> table.write()
            氏名,生年月日,性別,クレジットカード
            江島 佳洋,1992年10月07日,男,376001629316609
            三沢 大志,1995年02月13日,男,4173077927458449

    """

    class Meta:
        key = "delete_row_match"
        name = "行削除フィルター（一致）"
        description = """
        指定された列の値が文字列と一致する行を除外します
        """
        help_text = """
        「対象列」が「文字列」と一致する行を削除します。
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
        )

    def preproc(self, context):
        super().preproc(context)
        self.input_col_idx = context.get_param("input_col_idx")
        self.query = context.get_param("query")

    def process_record(self, record, context):
        if self.query != record[self.input_col_idx]:
            context.output(record)


class StringContainDeleteRowConvertor(convertors.Convertor):
    r"""
    概要
        指定した列に、指定した文字列を含む行を削除します。

    コンバータ名
        "delete_row_contains"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 文字列 [必須]

    サンプル
        「生年月日」列に「10月」を含む行を削除します。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "delete_row_contains",
                "params": {
                    "input_col_idx": "生年月日",
                    "query": "10月"
                }
            }

        - コード例

        .. code-block:: python

            >>> # データはランダム生成
            >>> from tablelinker import Table
            >>> table = Table(data=(
            ...     '"氏名","生年月日","性別","クレジットカード"\n'
            ...     '"小室 友子","1990年06月20日","女","3562635454918233"\n'
            ...     '"江島 佳洋","1992年10月07日","男","376001629316609"\n'
            ...     '"三沢 大志","1995年02月13日","男","4173077927458449"\n'
            ... ))
            >>> table = table.convert(
            ...     convertor="delete_row_contains",
            ...     params={
            ...         "input_col_idx": "生年月日",
            ...         "query": "10月",
            ...     },
            ... )
            >>> table.write()
            氏名,生年月日,性別,クレジットカード
            小室 友子,1990年06月20日,女,3562635454918233
            三沢 大志,1995年02月13日,男,4173077927458449

    """

    class Meta:
        key = "delete_row_contains"
        name = "行削除フィルター（部分文字列）"
        description = """
        指定された文字列が含まれる行を除外します
        """
        help_text = """
        「対象列」に「文字列」に指定した文字が含まれる行を削除します。
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
        )

    def preproc(self, context):
        super().preproc(context)
        self.input_col_idx = context.get_param("input_col_idx")
        self.query = context.get_param("query")

    def process_record(self, record, context):
        if self.query not in record[self.input_col_idx]:
            context.output(record)


class PatternMatchDeleteRowConvertor(convertors.Convertor):
    r"""
    概要
        指定した列が指定した正規表現と一致する行を削除します。
        正規表現は列の先頭から一致（match）する必要があります。

    コンバータ名
        "delete_pattern_match"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "pattern": 正規表現 [必須]

    サンプル
        「生年月日」が偶数の行を削除します。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "delete_row_pattern",
                "params": {
                    "input_col_idx": "生年月日",
                    "query": ".*[02468]日"
                }
            }

        - コード例

        .. code-block:: python

            >>> # データはランダム生成
            >>> from tablelinker import Table
            >>> table = Table(data=(
            ...     '"氏名","生年月日","性別","クレジットカード"\n'
            ...     '"小室 友子","1990年06月20日","女","3562635454918233"\n'
            ...     '"江島 佳洋","1992年10月07日","男","376001629316609"\n'
            ...     '"三沢 大志","1995年02月13日","男","4173077927458449"\n'
            ... ))
            >>> table = table.convert(
            ...     convertor="delete_row_pattern",
            ...     params={
            ...         "input_col_idx": "生年月日",
            ...         "query": r".*[02468]日",
            ...     },
            ... )
            >>> table.write()
            氏名,生年月日,性別,クレジットカード
            江島 佳洋,1992年10月07日,男,376001629316609
            三沢 大志,1995年02月13日,男,4173077927458449

    """

    class Meta:
        key = "delete_row_pattern"
        name = "行削除フィルター（正規表現）"
        description = """
        指定された列が指定した正規表現と一致する行を削除します
        """
        help_text = """
        「対象列」が「正規表現」に一致した行を削除します。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="対象列",
                required=True
            ),
            params.StringParam(
                "query",
                label="正規表現",
                required=True
            ),
        )

    def preproc(self, context):
        super().preproc(context)
        self.input_col_idx = context.get_param("input_col_idx")
        self.re_pattern = re.compile(context.get_param('query'))

    def process_record(self, record, context):
        value = record[self.input_col_idx]
        m = self.re_pattern.match(value)
        if m is None:
            context.output(record)
