from ..core import filters, params


def split(value, separator=",", limit=None):
    """
    列を指定された文字列で分割します。
    value_list: 対象の文字列リスト
    separator: 区切り文字
    limit: 区切りの最大文字
    """
    if limit is None:
        return value.split(separator)
    else:
        return value.split(separator, limit)


class SplitColFilter(filters.Filter):
    """
    文字列を分割するフィルターです。
    """

    class Meta:
        key = "split_col"
        name = "列の分割"
        description = """
        列を指定された文字列で分割して、複数の列を生成します
        """
        help_text = """
        生成した列は、一番うしろに追加され、数字が付きます。
        """

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_attr_idx",
                label="入力列",
                description="処理をする対象の列を選択してください。",
                required=True),
            params.OutputAttributeParam(
                "output_attr_name",
                label="出力列のプレフィックス",
                description="変換結果を出力する列名です。空もしくは既存の名前が指定された場合、置換となります。",
                prefix=True,
                required=False,
            ),
            params.AttributeParam(
                "output_attr_new_index",
                label="出力列の位置",
                description="新しく生成した列の挿入位置です。",
                label_suffix="の後",
                empty=True,
                empty_label="先頭",
                required=False,
            ),
            params.StringParam(
                "separator",
                label="区切り文字",
                default_value=",",
                required=True,
                description="文字列を分割する区切り文字を指定します。",
                help_text="「東京都,千葉県」の場合は、「,」になります。",
            ),
            # params.AttributeParam("attr", label="対象列", required=True),
            # params.StringParam("output_attr_name", label="新しい列名", help_text="新しく生成する列の名称です。"),
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

    def initial(self, context):
        self.output_attr_index = None
        self.new_attr = None

        input_attr_idx = context.get_param("input_attr_idx")
        separator = context.get_param("separator")

        context.next()  # skip haeder

        # すべてのデータを読んで、最大の列数を算出する
        limit = max([len(split(record[input_attr_idx], separator=separator)) for record in context.read()])
        context.set_data("limit", limit)

    def process_header(self, headers, context):
        input_attr_idx = context.get_param("input_attr_idx")
        limit = context.get_data("limit")

        output_attr_name = context.get_param("output_attr_name")
        if output_attr_name is None:
            output_attr_name = headers[input_attr_idx]

        output_attr_names = ["_".join([output_attr_name, str(n + 1)]) for n in range(limit)]

        # 移動
        new_headers = headers[:]
        output_attr_new_index = context.get_param("output_attr_new_index")
        if output_attr_new_index is None:  # 先頭
            for output_attr_name in reversed(output_attr_names):
                new_headers.insert(0, output_attr_name)
        else:  # 指定位置
            for output_attr_name in reversed(output_attr_names):
                new_headers.insert(output_attr_new_index + 1, output_attr_name)
        context.output(new_headers)

        # context.output(headers + output_attr_names)

    def process_record(self, record, context):
        input_attr_idx = context.get_param("input_attr_idx")
        separator = context.get_param("separator")
        limit = context.get_data("limit")

        splited_values = split(record[input_attr_idx], separator=separator, limit=limit)

        values = [splited_values[n] if len(splited_values) > n else "" for n in range(limit)]

        # 移動
        # output_attr_new_index = context.get_param("output_attr_new_index")
        # if output_attr_new_index is None:  # 先頭
        #     record.insert(0, header.pop(self.output_attr_index))
        # else:  # 指定位置
        #     record.insert(output_attr_new_index + 1, header.pop(self.output_attr_index))

        context.output(record + values)


class PivotColFilter(filters.Filter):
    """
    文字列を分割して複数の行にするフィルターです。
    """

    class Meta:
        key = "pivotal_col"
        name = "列の展開"
        description = """
        列を指定された文字列で分割して、複数の行を生成します。
        """
        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx", label="入力列", description="処理をする対象の列", required=True),
            params.StringParam("separator", label="区切り文字", required=True, default_value=","),
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

    def initial(self, context):
        pass

    def process_record(self, record, context):
        input_attr_idx = context.get_param("input_attr_idx")
        separator = context.get_param("separator")
        splited_values = split(record[input_attr_idx], separator=separator)

        for value in splited_values:
            new_record = [v for v in record]
            new_record[input_attr_idx] = value
            context.output(new_record)
