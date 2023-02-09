from tablelinker.core import convertors, params


def concat(value_list, separator=""):
    """文字列を結合します。
    value_list: 対象の文字列リスト
    separator: 区切り文字
    """

    if separator is None:
        separator = ""

    str_value_list = [str(value) for value in value_list]
    return separator.join(str_value_list)


class ConcatTitleConvertor(convertors.Convertor):
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

          eStat の表など、1行目に大項目、2行目に小項目が記載されている場合に
          このオプションを指定してください。

    サンプル

        統計局の集計表によく見られる、1行目に大項目、2行目と3行目に
        小項目が分割して記載されているタイトルを、
        ``hierarchical_heading`` を True にして階層見出しとして結合します。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "concat_title",
                "params": {
                    "lines": 3,
                    "separator": "",
                    "hierarchical_heading": true
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     ',人口,出生数,死亡数,（再掲）,,自　然,死産数,,,周産期死亡数,,,婚姻件数,離婚件数\\n'
            ...     ',,,,乳児死亡数,新生児,増減数,総数,自然死産,人工死産,総数,22週以後,早期新生児,,\\n'
            ...     ',,,,,死亡数,,,,,,の死産数,死亡数,,\\n'
            ...     '全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="concat_title",
            ...     params={
            ...         "lines": 3,
            ...         "separator": "",
            ...         "hierarchical_heading": True,
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            ,人口,出生数,死亡数,（再掲）乳児死亡数,（再掲）新生児死亡数,自　然増減数,死産数総数,死産数自然死産,死産数人工死産,周産期死亡数総数,周産期死亡数22週以後の死産数,周産期死亡数早期新生児死亡数,婚姻件数,離婚件数
            全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253

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

    def preproc(self, context):
        super().preproc(context)
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

            if lineno < self.lines - 1:
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
