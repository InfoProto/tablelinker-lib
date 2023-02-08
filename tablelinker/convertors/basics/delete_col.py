from ...core import convertors, params


class DeleteColConvertor(convertors.Convertor):
    """
    概要
        指定した列を削除します。

    コンバータ名
        "delete_col"

    パラメータ
        * "input_col_idx": 削除する入力列の列番号または列名 [必須]

    サンプル
        表の「備考」列を削除します。

        .. code-block:: json

            {
                "convertor": "delete_col",
                "params": {
                    "input_col_idx": "備考"
                }
            }

    """

    class Meta:
        key = "delete_col"
        name = "列を削除する"

        description = """
        指定した列を削除します
        """

        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="削除する列",
                description="削除する列",
                required=True
            ),
        )

    def preproc(self, context: "Context"):
        super().preproc(context)
        self.input_col_idx = context.get_param("input_col_idx")

    def process_header(self, headers, context):
        headers = self.delete_col(self.input_col_idx, headers)
        context.output(headers)

    def process_record(self, record, context):
        record = self.delete_col(self.input_col_idx, record)
        context.output(record)

    def delete_col(self, input_col_idx, target_list):
        target_list.pop(input_col_idx)
        return target_list


class DeleteColsConvertor(convertors.Convertor):
    """
    概要
        指定した複数の列を削除します。

    コンバータ名
        "delete_cols"

    パラメータ
        * "input_col_idxs": 削除する入力列の列番号または列名のリスト [必須]

    サンプル
        表の「その他」と「備考」列を削除します。

        .. code-block:: json

            {
                "convertor": "delete_cols",
                "params": {
                    "input_col_idxs": ["その他", "備考"]
                }
            }

    """

    class Meta:
        key = "delete_cols"
        name = "列を削除する"

        description = """
        指定した列を削除します
        """

        help_text = None

        params = params.ParamSet(
            params.InputAttributeListParam(
                "input_col_idxs",
                label="削除する列",
                description="削除する列",
                required=True),
        )

    def process_header(self, headers, context):
        self.input_col_idxs = sorted(
            context.get_param("input_col_idxs"), reverse=True)
        headers = self.delete_cols(self.input_col_idxs, headers)
        context.output(headers)

    def process_record(self, record, context):
        record = self.delete_cols(self.input_col_idxs, record)
        context.output(record)

    def delete_cols(self, positions, target_list):
        for pos in positions:
            target_list.pop(pos)

        return target_list
