from ..core import filters, params


class DeleteColFilter(filters.Filter):
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
