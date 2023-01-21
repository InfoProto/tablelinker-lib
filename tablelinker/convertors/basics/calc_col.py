from ..core import filters, params
from enum import Enum


class Calculation(Enum):
    Add = "+"
    Sub = "-"
    Mul = "*"
    Div = "/"


CalculationLabels = {
    Calculation.Add: "和",
    Calculation.Sub: "差",
    Calculation.Mul: "積",
    Calculation.Div: "商",
}


def calc(valueA, valueB, calculation):
    """文字列を結合します。
    valueA: 数値A
    valueB: 数値B
    separator: 区切り文字
    """
    if calculation == Calculation.Add:
        return valueA + valueB
    elif calculation == Calculation.Sub:
        return valueA - valueB
    elif calculation == Calculation.Mul:
        return valueA * valueB
    elif calculation == Calculation.Div:
        return valueA / valueB
    else:
        raise "Unknown Calculation"


class CalcColFilter(filters.Filter):
    """
    概要
        2つの入力列に対して四則演算を実行し、結果を出力列に保存します。

    コンバータ名
        "calc"

    パラメータ
        * "input_attr_idx1": 入力列1の列番号または列名 [必須]
        * "input_attr_idx2": 入力列2の列番号または列名 [必須]
        * "output_attr_name": 出力列名 [必須]
        * "operator": 演算子（"+", "-", "*", "/"） ["*"]
        * "delete_col": 入力列を削除するか （true/false） [false]

    注釈
        - 出力列名が元の表に存在している場合、その列に上書きします。
        - 存在していなかった場合、最後に新しい列が追加されます。

    サンプル
        表の「人口」列の値を「面積」列の値で割った商を「人口密度」列に
        出力します。

        .. code-block:: json

            {
                "convertor": "calc",
                "params": {
                    "input_attr_idx1": "人口",
                    "input_attr_idx2": "面積",
                    "operator": "/",
                    "output_attr_name": "人口密度",
                    "delete_col": false
                }
            }

    """

    class Meta:
        key = "calc"
        name = "列演算"

        description = """
        ２つの列を四則演算します。
        """

        help_text = None

        #
        params = params.ParamSet(
            params.InputAttributeParam("input_attr_idx1", label="対象列1", required=True),
            params.InputAttributeParam("input_attr_idx2", label="対象列2", required=True),
            params.StringParam("output_attr_name", label="新しい列名"),
            params.EnumsParam(
                "operator", label="演算子", enums=Calculation,
                labels=CalculationLabels, default_value=Calculation.Add
            ),
            params.BooleanParam("delete_col", label="元の列を消しますか？", default_value=False),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 2:
            return False
        return True

    def process_header(self, headers, context):
        attr1 = context.get_param("input_attr_idx1")
        attr2 = context.get_param("input_attr_idx2")
        output_attr_name = context.get_param("output_attr_name")
        delete_col = context.get_param("delete_col")

        if output_attr_name is None:
            output_attr_name = "+".join([headers[attr1], headers[attr2]])

        if delete_col:
            headers.pop(attr1)
            if attr1 != attr2:
                headers.pop(attr2 - 1)

        headers = headers + [output_attr_name]

        context.output(headers)

    def process_record(self, record, context):
        attr1 = context.get_param("input_attr_idx1")
        attr2 = context.get_param("input_attr_idx2")
        calculation = context.get_param("operator")
        delete_col = context.get_param("delete_col")

        try:
            valueA = int(record[attr1])
            valueB = int(record[attr2])
            calc_value = calc(valueA, valueB, calculation)
            record.append(calc_value)
        except ValueError:
            record.append(None)

        if delete_col:
            record.pop(attr1)
            if attr1 != attr2:
                record.pop(attr2)

        context.output(record)
