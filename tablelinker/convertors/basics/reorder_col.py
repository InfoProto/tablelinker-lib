from ..core import filters, params


class ReorderColsFilter(filters.Filter):
    """
    指定したカラムの順番に列を並べ替えます。
    """

    class Meta:
        key = "reorder_cols"
        name = "カラム並べ替え"
        description = "カラムを指定した順番に並べ替えます"
        help_text = None

        params = params.ParamSet(
            params.StringListParam(
                "column_list",
                label="カラムリスト",
                description="並べ替えた後のカラムのリスト",
                required=True),
        )

    def process_header(self, headers, context):
        output_headers = context.get_param("column_list")
        missed_headers = []
        for header in output_headers:
            if header not in headers:
                missed_headers.append(header)

        if len(missed_headers) > 0:
            if len(missed_headers) == 1:
                msg = "'{}' is ".format(missed_headers[0])
            else:
                msg = "'{}' are ".format(",".join(missed_headers))

            raise ValueError(
                "{} not in the original headers.".format(msg))

        self.mapping = []
        for header in output_headers:
            idx = headers.index(header)
            self.mapping.append(idx)

        context.output(self.reorder(headers))

    def process_record(self, record, context):
        context.output(self.reorder(record))

    def reorder(self, fields):
        return [fields[idx] for idx in self.mapping]
