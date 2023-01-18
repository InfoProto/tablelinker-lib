from ..core import filters, params


class MappingColsFilter(filters.Filter):
    """
    指定したカラムのリストにマッピングします。
    カラムのマッピングは指定されたマップによって決定します。
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
            else:
                idx = headers.index(header)
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
