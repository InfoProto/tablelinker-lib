from ..core import filters, params


class InsertColFilter(filters.Filter):
    class Meta:
        key = "insert_col"
        name = "新規列追加"

        description = """
        新規列を指定した場所に追加します。
        """

        message = "{new_name}を追加しました。"

        help_text = None

        params = params.ParamSet(
            params.OutputAttributeParam(
                "output_attr_name",
                label="出力列名",
                description="変換結果を出力する列名です。",
                help_text="空もしくは既存の名前が指定された場合、置換となります。",
                required=False,
            ),
            params.StringParam("new_value", label="新しい値", required=False, default_value=""),
            params.AttributeParam(
                "output_attr_new_index",
                label="出力列の位置",
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
        return len(attrs) == 0

    def process_header(self, headers, context):
        new_name = context.get_param("output_attr_name")
        output_attr_new_index = context.get_param("output_attr_new_index")
        headers = self.insert_list(output_attr_new_index, new_name, headers)
        context.output(headers)

    def process_record(self, record, context):
        new_value = context.get_param("new_value")
        output_attr_new_index = context.get_param("output_attr_new_index")
        record = self.insert_list(output_attr_new_index, new_value, record)
        context.output(record)

    def insert_list(self, output_attr_new_index, new_value, target_list):
        target_list.insert(output_attr_new_index, new_value)
        return target_list


class InsertColListFilter(filters.Filter):
    """
    新規列追加
    """

    class Meta:
        key = "insert_col_list"
        name = "新規列追加"

        description = """
        新規列を複数指定した場所に追加します。
        """

        help_text = None

        params = params.ParamSet(
            params.StringListParam("new_name_list", label="新しい列名", required=True),
            params.StringParam("new_value", label="新しい値", required=False, default_value=""),
            params.AttributeParam(
                "target_col",
                label="新規列を追加する位置",
                description="新規列の挿入位置です。",
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
        return len(attrs) == 0

    def process_header(self, headers, context):
        new_name_list = context.get_param("new_name_list")
        target_col = context.get_param("target_col")
        headers = self.insert_list(target_col, new_name_list, headers)
        context.output(headers)

    def process_record(self, record, context):
        new_name_list = context.get_param("new_name_list")
        new_value = context.get_param("new_value")
        target_col = context.get_param("target_col")
        record = self.insert_list(target_col, [new_value for new_name in new_name_list], record)
        context.output(record)

    def insert_list(self, target_col, value_list, target_list):
        target_list[target_col:0] = value_list
        return target_list
