from ..core import filters, params


class MoveColFilter(filters.Filter):
    """
    列を移動します。
    """

    class Meta:
        key = "move_col"
        name = "列移動"
        description = "列を指定した位置に移動します"
        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="移動する列", description="処理をする対象の列", required=True),
            params.AttributeParam(
                "output_attr_new_index",
                label="移動する列の移動先の位置",
                description="新しく列の挿入位置です。",
                label_suffix="の後",
                empty=True,
                empty_label="先頭",
                required=False,
            ),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1

    def process_header(self, headers, context):
        input_attr_idx = context.get_param("input_attr_idx")
        input_attr_idx_new_index = context.get_param("output_attr_new_index")
        headers = self.move_list(input_attr_idx, input_attr_idx_new_index, headers)
        context.output(headers)

    def process_record(self, record, context):
        input_attr_idx = context.get_param("input_attr_idx")
        output_attr_new_index = context.get_param("output_attr_new_index")
        record = self.move_list(input_attr_idx, output_attr_new_index, record)
        context.output(record)

    def move_list(self, input_attr_idx, output_attr_new_index, target_list):
        if output_attr_new_index is None:
            col = target_list.pop(input_attr_idx)
            target_list.insert(output_attr_new_index, col)
        elif input_attr_idx == output_attr_new_index:
            col = target_list.pop(input_attr_idx)
            target_list.insert(output_attr_new_index, col)
        elif input_attr_idx < output_attr_new_index:
            col = target_list.pop(input_attr_idx)
            target_list.insert(output_attr_new_index - 1, col)
        elif input_attr_idx > output_attr_new_index:
            col = target_list.pop(input_attr_idx)
            target_list.insert(output_attr_new_index, col)
        return target_list


# TODO: 未完成
class SortColFilter(filters.Filter):
    """
    列を移動します。
    """

    class Meta:
        key = "sort_col"
        name = "列名を合わせる"

        description = """
        指定された順序で列名を変更します。
        """

        help_text = None

        params = params.ParamSet(params.StringListParam("input_attr_idx_names", label="対象列名", required=True),)

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 0:
            return False
        return True

    def process_header(self, headers, context):
        input_attr_idx_names = context.get_param("input_attr_idx_names")
        col_mapping = [headers.index(input_attr_idx_name) for input_attr_idx_name in input_attr_idx_names]
        context.set_data("col_mapping", col_mapping)
        context.output(input_attr_idx_names)

    def process_record(self, record, context):
        col_mapping = context.get_data("col_mapping")
        new_record = [record[index] for index in col_mapping]
        context.output(new_record)
