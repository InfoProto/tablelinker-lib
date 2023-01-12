from ..core import filters, params
from ..core.mapping import ItemsPair


class MappingColsFilter(filters.Filter):
    """
    指定したカラムのリストにマッピングします。
    カラムのマッピングは語ベクトルと表記の類似度によって決定します。
    """

    class Meta:
        key = "mapping_cols"
        name = "カラムマッピング"
        description = "カラムを指定したリストにマッピングします"
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
                default_value=70),
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
