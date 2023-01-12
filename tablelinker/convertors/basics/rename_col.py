from ..core import filters, params


class RenameColFilter(filters.Filter):
    """
    カラム名を変更します。
    """

    class Meta:
        key = "rename_col"
        name = "カラム名変更"

        description = """
        指定した列名を変更します
        """

        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="入力列", description="処理をする対象の列", required=True),
            params.StringParam("new_col_name", label="新しい列名", required=True),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1

    def process_header(self, headers, context):
        new_col_name = context.get_param("new_col_name")
        input_attr_idx = context.get_param("input_attr_idx")

        headers[input_attr_idx] = new_col_name

        context.output(headers)


class RenameColsFilter(filters.Filter):
    """
    全ての列名を一括変更します。
    """

    class Meta:
        key = "rename_cols"
        name = "カラム名一括変更"
        description = "カラム名を一括で変更します"
        help_text = None

        params = params.ParamSet(
            params.StringListParam(
                "column_list",
                label="カラム名リスト",
                description="変更後のカラム名のリスト",
                required=True),
        )

    def process_header(self, headers, context):
        output_headers = context.get_param("column_list")
        if len(headers) != len(output_headers):
            raise ValueError(
                "Length of columns is not identical to the original headers.")

        context.output(output_headers)
