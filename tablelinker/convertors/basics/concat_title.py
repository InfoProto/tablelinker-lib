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


class ConcatTitleFilter(filters.Filter):
    """
    概要
        タイトル行が複数行に分割されている場合に結合して
        列見出しに設定します。
        タイトル行以降のデータには影響しません。

    コンバータ名
        "concat_title"

    パラメータ
        * "lineno_from": タイトル行の開始行番号 [0]
        * "lines": タイトル行として利用する行数: [2]
        * "empty_value": 空欄の場合の文字列: ""
        * "separator": 区切り文字 ["/"]
        * "hierarchical_heading": 階層型見出しかどうか [False]

    注釈
        - ``empty_value`` に "" を指定すると、空欄の行は無視されます。
        - ``hierarchical_heading`` に True を指定すると、上の列が
          空欄の場合にその左側の値を上位見出しとして利用します。

    サンプル
        表の1行目から3行目までを結合して列見出しを作ります。

        .. code-block:: json

            {
                "convertor": "concat_title",
                "params": {
                    "lines": 3,
                    "separator": "-"
                }
            }

    """

    class Meta:
        key = "concat_title"
        name = "タイトル結合"

        description = """
        指定した行数の列見出しを結合して新しいタイトルを生成します
        """

        help_text = ""

        params = params.ParamSet(
            params.IntParam(
                "lineno_from",
                label="開始行",
                required=False,
                default_value=0,
            ),
            params.IntParam(
                "lines",
                label="行数",
                required=False,
                default_value=2,
            ),
            params.StringParam(
                "empty_value",
                label="空欄表示文字",
                required=False,
                default_value="",
            ),
            params.StringParam(
                "separator",
                label="区切り文字",
                required=False,
                default_value="/",
            ),
            params.BooleanParam(
                "hierarchical_heading",
                label="階層型見出し",
                required=False,
                default_value=False,
            ),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) > 0:
            return False
        return True

    def initial_context(self, context):
        super().initial_context(context)
        self.lineno_from = context.get_param("lineno_from")
        self.lines = context.get_param("lines")
        self.empty_value = context.get_param("empty_value")
        self.separator = context.get_param("separator")
        self.hierarchical = context.get_param("hierarchical_heading")

    def process_header(self, headers, context):
        # 開始行までスキップ
        for lineno in range(0, self.lineno_from):
            headers = context.next()

        new_headers = [[] for _ in range(len(headers))]
        for lineno in range(0, self.lines):
            for i, value in enumerate(headers):
                if value != "":
                    if self.hierarchical and i > 0 and \
                            "".join(new_headers[i]) == "":
                        new_headers[i] = new_headers[i - 1][: -1]

                    new_headers[i].append(value)
                else:
                    new_headers[i].append("")

            headers = context.next()

        for i, values in enumerate(new_headers):
            if self.empty_value != "":
                values = filter(
                    None,
                    [v if v != "" else self.empty_value for v in values]
                )
            else:
                values = filter(None, values)

            headers[i] = concat(values, self.separator)

        context.output(headers)
