from logging import getLogger

from ..core import convertors, params

logger = getLogger(__name__)


class InsertColConvertor(convertors.Convertor):
    """
    概要
        新しい列を追加します。

    コンバータ名
        "insert_col"

    パラメータ
        * "output_attr_idx": 新しい列を追加する列番号または列名 [最後尾]
        * "output_attr_name": 追加する列名 [必須]
        * "value": 追加した列にセットする値 [""]

    注釈
        - 出力列名が元の表に存在していても同じ名前の列を追加します。
        - 追加する位置を既存の列名で指定した場合、その列の直前に
          新しい列を挿入します。
        - 追加する位置を省略した場合、最後尾に追加します。

    サンプル
        「所在地」列の前に「都道府県名」列を挿入し、その列の
        すべての値を「東京都」にセットします。

        .. code-block:: json

            {
                "convertor": "insert_col",
                "params": {
                    "output_attr_idx": "所在地",
                    "output_attr_name": "都道府県名",
                    "value": "東京都"
                }
            }

    """

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
                description="新しく追加する列名です。",
                help_text="既存の名前が指定された場合も同じ名前の列が追加されます。",
                required=True,
            ),
            params.AttributeParam(
                "output_attr_idx",
                label="出力列の位置",
                description="新しい列の挿入位置です。",
                label_suffix="の後",
                empty=True,
                empty_label="先頭",
                required=False,
            ),
            params.StringParam(
                "value",
                label="新しい値",
                required=False,
                default_value="",
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
        output_attr_idx = context.get_param("output_attr_idx")
        if output_attr_idx is None:
            output_attr_idx = len(headers)

        headers = self.insert_list(output_attr_idx, new_name, headers)
        context.output(headers)

    def process_record(self, record, context):
        value = context.get_param("value")
        output_attr_idx = context.get_param("output_attr_idx")
        record = self.insert_list(output_attr_idx, value, record)
        context.output(record)

    def insert_list(self, output_attr_idx, value, target_list):
        target_list.insert(output_attr_idx, value)
        return target_list


class InsertColsConvertor(convertors.Convertor):
    """
    概要
        新しい複数の列を追加します。

    コンバータ名
        "insert_cols"

    パラメータ
        * "output_attr_idx": 新しい列を追加する列番号または列名 [最後尾]
        * "output_attr_names": 追加する列名のリスト [必須]
        * "values": 追加した列にセットする値のリスト [""]

    注釈
        - 出力列名が元の表に存在していても同じ名前の列を追加します。
        - 追加する位置を既存の列名で指定した場合、その列の直前に
          新しい列を挿入します。
        - 追加する位置を省略した場合、最後尾に追加します。
        - ``values`` に単一の値を指定した場合はすべての列にその値をセットします。
        - ``values`` にリストを指定する場合、追加する列数と
          長さが同じである必要があります。

    サンプル
        「所在地」列の前に「都道府県名」「市区町村名」列を挿入し、
        その列のすべての値を「東京都」「八丈町」にセットします。

        .. code-block:: json

            {
                "convertor": "insert_cols",
                "params": {
                    "output_attr_idx": "所在地",
                    "output_attr_names": ["都道府県名", "市区町村名"],
                    "values": ["東京都", "八丈町"]
                }
            }

    """

    class Meta:
        key = "insert_cols"
        name = "新規列追加（複数）"

        description = """
        新規列を複数指定した場所に追加します。
        """

        help_text = None

        params = params.ParamSet(
            params.AttributeParam(
                "output_attr_idx",
                label="新規列を追加する位置",
                description="新規列の挿入位置です。",
                required=False,
            ),
            params.StringListParam(
                "output_attr_names",
                label="新しい列名のリスト",
                required=True
            ),
            params.StringListParam(
                "values",
                label="新しい列にセットする値のリスト",
                required=False,
                default_value=""
            ),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 0

    def initial_context(self, context):
        super().initial_context(context)
        self.output_attr_idx = context.get_param("output_attr_idx")
        self.new_names = context.get_param("output_attr_names")
        self.new_values = context.get_param("values")

        if isinstance(self.new_values, str):
            self.new_values = [self.new_values] * len(self.new_names)
        elif len(self.new_values) != len(self.new_names):
            logger.error("追加する列数と、値の列数が一致しません。")
            raise ValueError((
                "The length of 'values' must be equal to "
                "the length of 'output_attr_names'."))

    def process_header(self, headers, context):
        if self.output_attr_idx is None:
            self.output_attr_idx = len(headers)

        headers = self.insert_list(
            self.output_attr_idx, self.new_names, headers)
        context.output(headers)

    def process_record(self, record, context):
        record = self.insert_list(
            self.output_attr_idx, self.new_values, record)
        context.output(record)

    def insert_list(self, output_attr_idx, value_list, target_list):
        new_list = target_list[0:output_attr_idx] + value_list \
            + target_list[output_attr_idx:]
        return new_list
