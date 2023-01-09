from ..core import filters, params
from enum import Enum


class Calculation(Enum):
    Add = "1"
    Sub = "2"
    Mul = "3"
    Div = "4"


CalculationLabels = {
    Calculation.Add: "足し算",
    Calculation.Sub: "引き算",
    Calculation.Mul: "掛け算",
    Calculation.Div: "割り算",
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
    ２つの列を演算します。
    """

    class Meta:
        key = "clac"
        name = "列演算"

        description = """
        ２つの列を四則演算します。
        """

        help_text = None

        #
        params = params.ParamSet(
            params.InputAttributeParam("attr1", label="対象列1", required=True),
            params.InputAttributeParam("attr2", label="対象列2", required=True),
            params.EnumsParam(
                "calculation", label="計算", enums=Calculation, labels=CalculationLabels, default_value=Calculation.Add
            ),
            params.StringParam("output_attr_name", label="新しい列名"),
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
        attr1 = context.get_param("attr1")
        attr2 = context.get_param("attr2")
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
        attr1 = context.get_param("attr1")
        attr2 = context.get_param("attr2")
        calculation = context.get_param("calculation")
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
