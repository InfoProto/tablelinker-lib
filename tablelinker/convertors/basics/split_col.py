import re

from ..core import filters, params


class SplitColFilter(filters.Filter):
    """
    概要
        指定した列を区切り文字で複数列に分割します。

    コンバータ名
        "split_col"

    パラメータ
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_idxs": 分割した結果を出力する列番号または
          列名のリスト [必須]
        * "separator": 区切り文字（正規表現） [","]

    注釈
        - ``output_attr_idxs`` で指定された列名が存在しない場合、
          最後尾に追加されます。
        - 分割した列の数が ``output_attr_idxs`` よりも少ない場合は
          足りない列の値が "" になります。
        - 分割した列の数が ``output_attr_idxs`` よりも多い場合は
          最後の列に残りのすべての文字列が出力されます。

    サンプル
        「氏名」列を空白で区切り、「姓」列と「名」列に分割します。

        .. code-block :: json

            {
                "convertor": "split_col",
                "params": {
                    "input_attr_idx": "氏名",
                    "output_attr_idxs": ["姓", "名"],
                    "separator": "\\s+",
                }
            }

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
            params.OutputAttributeListParam(
                "output_attr_idxs",
                label="分割後に出力する列番号または列名のリスト",
                description="変換結果を出力する列名です。",
                required=True,
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

    def initial_context(self, context):
        super().initial_context(context)
        self.headers = context.get_data("headers")
        self.re_separator = re.compile(context.get_param("separator"))
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.output_attr_idxs = context.get_param("output_attr_idxs")

    def process_header(self, headers, context):
        # 出力列として指定された列番号が存在しない場合の処理
        counter = 1
        for i, idx in enumerate(self.output_attr_idxs):
            if idx >= len(self.headers):
                input_header = headers[self.input_attr_idx]
                self.output_attr_idxs[i] = len(self.headers)
                self.headers.append(f"{input_header}_{counter:d}")
                counter +=1

        context.output(self.headers)

    def process_record(self, record, context):
        original = record[self.input_attr_idx]
        splits = self.re_separator.split(
            original, maxsplit=len(self.output_attr_idxs) - 1)
        
        new_record = record + [""] * (len(self.headers) - len(record))
        for i, new_val in enumerate(splits):
            new_record[self.output_attr_idxs[i]] = new_val

        context.output(new_record)


class SplitRowFilter(filters.Filter):
    """
    概要
        指定した列を区切り文字で複数行に分割します。

    コンバータ名
        "explode_col"

    パラメータ
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "separator": 区切り文字（正規表現） [","]

    注釈
        - 分割前の行は削除されます。
        - 区切り文字が末尾の場合、対象列が空欄の行も出力されます。

    サンプル
        「アクセス方法」列を「。」で区切り、複数行に分割します。

        .. code-block :: json

            {
                "convertor": "split_row",
                "params": {
                    "input_attr_idx": "アクセス方法",
                    "separator": "。",
                }
            }

    """

    class Meta:
        key = "split_row"
        name = "列を分割して行に展開"
        description = """
        列を指定された文字列で分割して、複数の行を生成します。
        """
        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_attr_idx",
                label="入力列",
                description="処理をする対象の列",
                required=True
            ),
            params.StringParam(
                "separator",
                label="区切り文字",
                required=True,
                default_value=","
            ),
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

    def initial_context(self, context):
        super().initial_context(context)
        self.re_separator = re.compile(context.get_param("separator"))
        self.input_attr_idx = context.get_param("input_attr_idx")

    def process_record(self, record, context):
        splits = self.re_separator.split(record[self.input_attr_idx])

        for value in splits:
            new_record = record[:]  # 元のレコードを複製
            new_record[self.input_attr_idx] = value
            context.output(new_record)
