from ...core import convertors, params


class MappingColsConvertor(convertors.Convertor):
    """
    概要
        既存の列名と新しい列名のマッピングテーブルを利用して、
        既存の表を新しい表に変換します。

    コンバータ名
        "mapping_cols"

    パラメータ
        * "column_map": 列名のマッピングテーブル [必須]

    注釈
        - マッピングテーブルの左側（キー）は出力される新しい列名、
          右側（値）は既存の表に含まれる列番号または列名です。
        - 既存の列名でマッピングテーブルに含まれないものは削除されます。
        - 新しい列名で対応する列名が null のもの新規に追加される列で、
          値は空（""）になります。


    サンプル
        「」「人口」「出生数」「死亡数」…「婚姻件数」「離婚件数」のうち、
        「」「人口」「婚姻件数」「離婚件数」の列だけを選択し、
        「都道府県」「人口」「婚姻件数」「離婚件数」にマップします。

        .. code-block:: json

            {
                "convertor": "mapping_cols",
                "params": {
                    "column_map": {
                        "都道府県": 0,
                        "人口": "人口",
                        "婚姻件数": "婚姻件数",
                        "離婚件数": "離婚件数"
                    }
                }
            }

    """

    class Meta:
        key = "mapping_cols"
        name = "カラムマッピング"
        description = "カラムを指定した通りにマッピングします"
        help_text = None

        params = params.ParamSet(
            params.DictParam(
                "column_map",
                label="カラムマップ",
                description="マッピング先のカラムをキー、元のカラムを値とする辞書",
                required=True),
        )

    def process_header(self, headers, context):
        column_map = context.get_param("column_map")
        self.mapping = []
        new_headers = []
        for output, header in column_map.items():
            if header is None:
                self.mapping.append(None)
                new_headers.append(output)
                continue

            if isinstance(header, str):
                try:
                    idx = headers.index(header)
                except ValueError:
                    raise RuntimeError((
                        "出力列 '{}' にマップされた列 '{}' は"
                        "有効な列名ではありません。有効な列名は次の通り; {}"
                    ).format(output, header, ",".join(headers)))

            elif isinstance(header, int):
                idx = header
            else:
                raise RuntimeError((
                    "出力列 '{}' にマップされた列 '{}' には"
                    "列名か位置を表す数字を指定してください。"
                ).format(output, header))

            self.mapping.append(idx)
            new_headers.append(output)

        context.output(new_headers)

    def process_record(self, record, context):
        context.output(self.reorder(record))

    def reorder(self, fields):
        new_fields = []
        for idx in self.mapping:
            if idx is None:
                new_fields.append('')
            else:
                new_fields.append(fields[idx])

        return new_fields
