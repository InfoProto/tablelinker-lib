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
        "concat_col"

    パラメータ
        * "input_attr_idx1": 入力列1の列番号または列名 [必須]
        * "input_attr_idx2": 入力列2の列番号または列名 [必須]
        * "output_attr_name": 出力列名
        * "output_attr_idx": 出力列の列番号または列名
        * "separator": 区切り文字 [""]

    注釈
        - ``output_attr_name`` が省略された場合、
          入力列 1, 2 の列名を結合して出力列名とします。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    サンプル
        表の「姓」列と「名」列を空白で結合し、結果を「姓名」列に
        出力します。

        .. code-block:: json

            {
                "convertor": "concat_col",
                "params": {
                    "input_attr_idx1": "姓",
                    "input_attr_idx2": "名",
                    "separator": " ",
                    "output_attr_name": "姓名"
                }
            }

    """

    class Meta:
        key = "concat_col"
        name = "列結合"

        description = """
        指定した列を結合します
        """

        help_text = ""

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_attr_idx1",
                label="対象列1",
                required=True
            ),
            params.InputAttributeParam(
                "input_attr_idx2",
                label="対象列2",
                required=True
            ),
            params.OutputAttributeParam(
                "output_attr_name",
                label="新しい列名",
                required=False
            ),
            params.AttributeParam(
                "output_attr_idx",
                label="出力する位置",
                required=False
            ),
            params.StringParam(
                "separator",
                label="区切り文字",
                required=False,
                default_value=""
            ),
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

    def initial_context(self, context):
        super().initial_context(context)
        headers = context.get_data("headers")

        self.attr1 = context.get_param("input_attr_idx1")
        self.attr2 = context.get_param("input_attr_idx2")
        self.output_attr_name = context.get_param("output_attr_name")
        self.output_attr_idx = context.get_param("output_attr_idx")
        self.separator = context.get_param("separator")
        self.del_attr = None

        if self.output_attr_name is None:
            self.output_attr_name = concat(
                [headers[self.attr1], headers[self.attr2]],
                self.separator)

        # 出力列名が存在するかどうかを確認
        try:
            idx = headers.index(self.output_attr_name)
            if self.output_attr_idx is None:
                self.output_attr_idx = idx

            if idx < self.output_attr_idx:
                self.output_attr_idx -= 1
                self.del_attr = idx
            elif idx > self.output_attr_idx:
                self.del_attr = idx

        except ValueError:
            # 存在しない場合
            if self.output_attr_idx is None or \
                    self.output_attr_idx > len(headers):
                self.output_attr_idx = len(headers)

    def process_header(self, headers, context):
        if self.del_attr:
            del headers[self.del_attr]

        headers.insert(
            self.output_attr_idx,
            self.output_attr_name)

        context.output(headers)

    def process_record(self, record, context):
        value_list = [record[self.attr1], record[self.attr2]]
        concated_value = concat(
            value_list, separator=self.separator)

        if self.del_attr:
            del record[self.del_attr]

        record.insert(
            self.output_attr_idx,
            concated_value)

        context.output(record)


class ConcatColsFilter(filters.Filter):
    """
    概要
        複数の入力列の文字列を結合し、結果を出力列に保存します。

    コンバータ名
        "concat_cols"

    パラメータ
        * "input_attr_idxs": 入力列の列番号または列名のリスト [必須]
        * "output_attr_name": 出力列名
        * "output_attr_idx": 出力列の列番号または列名
        * "separator": 区切り文字 [""]

    注釈
        - ``output_attr_name`` が省略された場合、
          入力列の列名を結合して出力列名とします。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    サンプル
        表の「都道府県名」「住所1」「住所2」列を結合し、
        結果を「住所（全体）」列に出力します。

        .. code-block:: json

            {
                "convertor": "concat_cols",
                "params": {
                    "input_attr_idxs": ["都道府県名", "住所1", "住所2"],
                    "output_attr_name": "住所（全体）",
                    "separator": " "
                }
            }

    """

    class Meta:
        key = "concat_cols"
        name = "複数列結合"

        description = """
        指定した複数列を結合します
        """

        help_text = ""

        params = params.ParamSet(
            params.InputAttributeListParam(
                "input_attr_idxs",
                label="対象列",
                required=True,
            ),
            params.OutputAttributeParam(
                "output_attr_name",
                label="新しい列名",
                required=True,
            ),
            params.AttributeParam(
                "output_attr_idx",
                label="出力する位置",
                required=False,
            ),
            params.StringParam(
                "separator",
                label="区切り文字",
                default_value="",
            ),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) < 2:
            return False
        return True

    def initial_context(self, context):
        super().initial_context(context)
        headers = context.get_data("headers")

        self.input_attr_idxs = context.get_param("input_attr_idxs")
        self.output_attr_name = context.get_param("output_attr_name")
        self.output_attr_idx = context.get_param("output_attr_idx")
        self.separator = context.get_param("separator")
        self.del_attr = None

        if self.output_attr_name is None:
            self.output_attr_name = concat([
                headers[x] for x in self.input_attr_idxs],
                self.separator)

        # 出力列名が存在するかどうかを確認
        try:
            idx = headers.index(self.output_attr_name)
            if self.output_attr_idx is None:
                self.del_attr = idx
                self.output_attr_idx = idx
            elif idx < self.output_attr_idx:
                self.output_attr_idx -= 1
                self.del_attr = idx
            elif idx > self.output_attr_idx:
                self.del_attr = idx

        except ValueError:
            # 存在しない場合
            if self.output_attr_idx is None or \
                    self.output_attr_idx > len(headers):
                self.output_attr_idx = len(headers)

    def process_header(self, headers, context):
        if self.del_attr:
            del headers[self.del_attr]

        headers.insert(
            self.output_attr_idx,
            self.output_attr_name)

        context.output(headers)

    def process_record(self, record, context):
        value_list = [record[x] for x in self.input_attr_idxs]
        concated_value = concat(
            value_list, separator=self.separator)

        if self.del_attr:
            del record[self.del_attr]

        record.insert(
            self.output_attr_idx,
            concated_value)

        context.output(record)
