from ..core import filters, params
from ..core.mapping import ItemsPair


class AutoMappingColsFilter(filters.Filter):
    """
    概要
        指定した列名リストに合わせて既存の列をマッピングします。
        マッピングは語ベクトルと表記の類似度によって決定します。

    コンバータ名
        "auto_mapping_cols"

    パラメータ
        * "column_list": 出力したい列名のリスト [必須]
        * "keep_colname": 元の列名を保持するか [False]
        * "threshold": 列をマッピングするしきい値 [40]

    注釈
        - 元の列のうち、マッピング先の列との類似度が ``threshold``
          以下のものは削除されます。
        - ``threshold`` は 0 - 100 の整数で指定します。
          値が大きいほど一致度が高いものしか残りません。
        - ``keep_colname`` に True を指定すると、元の列名と
          マッピング先の列名が異なる場合に出力列名を
          `<マッピング先の列名> / <元の列名>` に変更します。

    サンプル
        出力したい列名のリストに合わせてマッピングします。

        .. code-block:: json

            {
                "convertor": "auto_mapping_cols",
                "params": {
                    "column_list": [
                        "名称",
                        "所在地",
                        "経度",
                        "緯度",
                        "説明"
                    ],
                    "keep_colname": true
                }
            }

    """

    class Meta:
        key = "auto_mapping_cols"
        name = "自動カラムマッピング"
        description = "カラムを指定したリストに自動マッピングします"
        help_text = None

        params = params.ParamSet(
            params.StringListParam(
                "column_list",
                label="カラムリスト",
                description="マッピング先のカラムリスト",
                required=True),
            params.BooleanParam(
                "keep_colname",
                label="元カラム名を保持",
                description="元のカラム名を保持するかどうか",
                required=False,
                default_value=False),
            params.IntParam(
                "threshold",
                label="しきい値",
                description="カラムが一致すると判定するしきい値(0-100)",
                required=False,
                default_value=40),
        )

    def process_header(self, headers, context):
        output_headers = context.get_param("column_list")
        pair = ItemsPair(output_headers, headers)
        self.mapping = []
        new_headers = []
        for result in pair.mapping():
            output, header, score = result
            if output is None:
                # マッピングされなかったカラムは除去
                continue

            if score * 100.0 < context.get_param("threshold") or \
                    header is None:
                self.mapping.append(None)
                new_headers.append(output)
            else:
                idx = headers.index(header)
                self.mapping.append(idx)
                if output == header or \
                        not context.get_param('keep_colname'):
                    new_headers.append(output)
                else:
                    new_headers.append("{} / {}".format(
                        output, header))

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
