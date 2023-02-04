from ..core import convertors, params


class ReorderColsConvertor(convertors.Convertor):
    """
    概要
        指定した順番に列を並べ替えます。

    コンバータ名
        "reorder_cols"

    パラメータ
        * "column_list": 並び替えた列番号または列名のリスト [必須]

    注釈
        - ``column_list`` に指定した列が存在しない場合は
          `ValueError` を送出します。
        - ``column_list`` に指定されなかった列は削除されます。

    サンプル
        列を選択して並び替えます。

        .. code-block:: json

            {
                "convertor": "reorder_cols",
                "params": {
                    "column_list": [
                        "所在地",
                        "経度",
                        "緯度",
                        "説明"
                    ]
                }
            }

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
        for idx in output_headers:
            if isinstance(idx, str) and idx not in headers:
                missed_headers.append(idx)
            elif isinstance(idx, int) and (
                    idx < 0 or idx >= len(headers)):
                missed_headers.append(str(idx))

        if len(missed_headers) > 0:
            if len(missed_headers) == 1:
                msg = "'{}' is ".format(missed_headers[0])
            else:
                msg = "'{}' are ".format(",".join(missed_headers))

            raise ValueError(
                "{} not in the original headers.".format(msg))

        self.mapping = []
        for idx in output_headers:
            if isinstance(idx, str):
                idx = headers.index(idx)
            self.mapping.append(idx)

        context.output(self.reorder(headers))

    def process_record(self, record, context):
        context.output(self.reorder(record))

    def reorder(self, fields):
        return [fields[idx] for idx in self.mapping]
