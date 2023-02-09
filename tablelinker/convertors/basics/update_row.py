import re

from tablelinker.core import convertors, params


class StringMatchUpdateRowConvertor(convertors.Convertor):
    """
    概要
        指定した列の値が指定した文字列と完全に一致する行の値を
        新しい文字列に置き換えます。部分一致は置き換えません。

    コンバータ名
        "update_row_match"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 検索文字列 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        「性別」列が「女」の行を「F」に置き換えます。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "update_row_match",
                "params": {
                    "input_col_idx": "性別",
                    "query": "女",
                    "new": "F"
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     '"氏名","生年月日","性別","クレジットカード"\\n'
            ...     '"小室 友子","1990年06月20日","女","3562635454918233"\\n'
            ...     '"江島 佳洋","1992年10月07日","男","376001629316609"\\n'
            ...     '"三沢 大志","1995年02月13日","男","4173077927458449"\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="update_row_match",
            ...     params={
            ...         "input_col_idx": "性別",
            ...         "query": "女",
            ...         "new": "F",
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            氏名,生年月日,性別,クレジットカード
            小室 友子,1990年06月20日,F,3562635454918233
            江島 佳洋,1992年10月07日,男,376001629316609
            三沢 大志,1995年02月13日,男,4173077927458449

    """

    class Meta:
        key = "update_row_match"
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
        "update_row_contains"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 検索文字列 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        先頭列に「　」（全角空白）を含む場合、「」に置き換えます（削除）。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "update_row_contains",
                "params": {
                    "input_col_idx": 0,
                    "query": "　",
                    "new": ""
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     ',人口,出生数,死亡数,（再掲）乳児死亡数,（再掲）新生児死亡数,自　然増減数,死産数総数,死産数自然死産,死産数人工死産,周産期死亡数総数,周産期死亡数22週以後の死産数,周産期死亡数早期新生児死亡数,婚姻件数,離婚件数\\n'
            ...     '全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253\\n'
            ...     '01 北海道,5188441,29523,65078,59,25,-35555,728,304,424,92,75,17,20904,9070\\n'
            ...     '02 青森県,1232227,6837,17905,18,15,-11068,145,87,58,32,17,15,4032,1915\\n'
            ...     '03 岩手県,1203203,6718,17204,8,3,-10486,150,90,60,21,19,2,3918,1679\\n'
            ...     '04 宮城県,2280203,14480,24632,27,15,-10152,311,141,170,56,41,15,8921,3553\\n'
            ...     '05 秋田県,955659,4499,15379,9,4,-10880,98,63,35,18,15,3,2686,1213\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="update_row_contains",
            ...     params={
            ...         "input_col_idx": 0,
            ...         "query": "　",
            ...         "new": "",
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            ,人口,出生数,死亡数,（再掲）乳児死亡数,（再掲）新生児死亡数,自　然増減数,死産数総数,死産数自然死産,死産数人工死産,周産期死亡数総数,周産期死亡数22週以後の死産数,周産期死亡数早期新生児死亡数,婚姻件数,離婚件数
            全国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253
            01 北海道,5188441,29523,65078,59,25,-35555,728,304,424,92,75,17,20904,9070
            ...

    """

    class Meta:
        key = "update_row_contains"
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
        "update_row_pattern"

    パラメータ
        * "input_col_idx": 検索対象列の列番号または列名 [必須]
        * "query": 正規表現 [必須]
        * "new": 置き換える文字列 [必須]

    サンプル
        先頭列が「01 北海道」のように数字に続く空白を含む場合、
        その部分を「」に置き換えます（削除）。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "update_row_pattern",
                "params": {
                    "input_col_idx": 0,
                    "query": "[0-9]+ +",
                    "new": ""
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     ',人口,出生数,死亡数,（再掲）乳児死亡数,（再掲）新生児死亡数,自　然増減数,死産数総数,死産数自然死産,死産数人工死産,周産期死亡数総数,周産期死亡数22週以後の死産数,周産期死亡数早期新生児死亡数,婚姻件数,離婚件数\\n'
            ...     '全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253\\n'
            ...     '01 北海道,5188441,29523,65078,59,25,-35555,728,304,424,92,75,17,20904,9070\\n'
            ...     '02 青森県,1232227,6837,17905,18,15,-11068,145,87,58,32,17,15,4032,1915\\n'
            ...     '03 岩手県,1203203,6718,17204,8,3,-10486,150,90,60,21,19,2,3918,1679\\n'
            ...     '04 宮城県,2280203,14480,24632,27,15,-10152,311,141,170,56,41,15,8921,3553\\n'
            ...     '05 秋田県,955659,4499,15379,9,4,-10880,98,63,35,18,15,3,2686,1213\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="update_row_pattern",
            ...     params={
            ...         "input_col_idx": 0,
            ...         "query": "[0-9]+ +",
            ...         "new": "",
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            ,人口,出生数,死亡数,（再掲）乳児死亡数,（再掲）新生児死亡数,自　然増減数,死産数総数,死産数自然死産,死産数人工死産,周産期死亡数総数,周産期死亡数22週以後の死産数,周産期死亡数早期新生児死亡数,婚姻件数,離婚件数
            全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253
            北海道,5188441,29523,65078,59,25,-35555,728,304,424,92,75,17,20904,9070
            青森県,1232227,6837,17905,18,15,-11068,145,87,58,32,17,15,4032,1915
            岩手県,1203203,6718,17204,8,3,-10486,150,90,60,21,19,2,3918,1679
            ...

    """

    class Meta:
        key = "update_row_pattern"
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
                "query",
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
        self.re_pattern = re.compile(context.get_param('query'))
        self.new_value = context.get_param("new")

    def process_record(self, record, context):
        record[self.idx] = self.re_pattern.sub(
            self.new_value, record[self.idx])

        context.output(record)
