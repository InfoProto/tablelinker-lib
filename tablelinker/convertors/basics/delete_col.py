from ..core import filters, params


class DeleteColFilter(filters.Filter):
    """
    概要
        指定した列を削除します。

    コンバータ名
        "delete_col"

    パラメータ
        * "input_attr_idx": 削除する入力列の列番号または列名 [必須]

    サンプル
        表の「備考」列を削除します。

        .. code-block:: json

            {
                "convertor": "delete_col",
                "params": {
                    "input_attr_idx": "備考"
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
            params.InputAttributeParam("input_attr_idx", label="削除する列", description="削除する列", required=True),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def process_header(self, headers, context):
        input_attr_idx = context.get_param("input_attr_idx")
        headers = self.delete_col(input_attr_idx, headers)
        context.output(headers)

    def process_record(self, record, context):
        input_attr_idx = context.get_param("input_attr_idx")
        record = self.delete_col(input_attr_idx, record)
        context.output(record)

    def delete_col(self, input_attr_idx, target_list):
        target_list.pop(input_attr_idx)
        return target_list


class DeleteColsFilter(filters.Filter):
    """
    概要
        指定した複数の列を削除します。

    コンバータ名
        "delete_cols"

    パラメータ
        * "input_attr_idxs": 削除する入力列の列番号または列名のリスト [必須]

    サンプル
        表の「その他」と「備考」列を削除します。

        .. code-block:: json

            {
                "convertor": "delete_cols",
                "params": {
                    "input_attr_idxs": ["その他", "備考"]
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
                "input_attr_idxs",
                label="削除する列",
                description="削除する列",
                required=True),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def process_header(self, headers, context):
        self.input_attr_idxs = sorted(
            context.get_param("input_attr_idxs"), reverse=True)
        headers = self.delete_cols(self.input_attr_idxs, headers)
        context.output(headers)

    def process_record(self, record, context):
        record = self.delete_cols(self.input_attr_idxs, record)
        context.output(record)

    def delete_cols(self, positions, target_list):
        for pos in positions:
            target_list.pop(pos)

        return target_list
