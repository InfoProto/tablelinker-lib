from enum import Enum
import re

from tablelinker.core import convertors, params


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
    def eval_number(val:str) -> float:
        # 桁区切り "," を含む場合は除去
        val = val.replace(',', '')

        # 数字と小数点以外を含む場合は例外
        if not re.match(r'^[\-?\d*\.?\d+]+$', val):
            raise ValueError("値 '{}' は数値ではありません。".format(val))

        return float(val)

    valueA = eval_number(valueA)
    valueB = eval_number(valueB)

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


class CalcColConvertor(convertors.Convertor):
    """
    概要
        2つの入力列に対して四則演算を実行し、結果を出力列に保存します。

    コンバータ名
        "calc"

    パラメータ
        * "input_col_idx1": 入力列1の列番号または列名 [必須]
        * "input_col_idx2": 入力列2の列番号または列名 [必須]
        * "output_col_name": 出力列名 [必須]
        * "operator": 演算子（"+", "-", "*", "/"） ["*"]
        * "delete_col": 入力列を削除するか （true/false） [false]

    注釈
        - 出力列名が元の表に存在している場合、その列に上書きします。
        - 存在していなかった場合、最後に新しい列が追加されます。

    サンプル
        表の「人口」列の値を「面積」列の値で割った商を「人口密度」列に
        出力します。

        - タスクファイル例

        .. code-block:: json

            {
                "convertor": "calc",
                "params": {
                    "input_col_idx1": "人口",
                    "input_col_idx2": "面積",
                    "operator": "/",
                    "output_col_name": "人口密度",
                    "delete_col": false
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     '都道府県名,人口,面積\\n'
            ...     '北海道 ほっかいどう,"5,139,522","83,423.81"\\n'
            ...     '青森県 あおもりけん,"1,204,372","9,645.95"\\n'
            ...     '岩手県 いわてけん,"1,180,512","15,275.01"\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="calc",
            ...     params={
            ...         "input_col_idx1": "人口",
            ...         "input_col_idx2": "面積",
            ...         "operator": "/",
            ...         "output_col_name": "人口密度",
            ...         "delete_col": False,
            ...     },
            ... )
            >>> table.write(lines=2, lineterminator="\\n")
            都道府県名,人口,面積,人口密度
            北海道 ほっかいどう,"5,139,522","83,423.81",61.60737564012001

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
            params.InputAttributeParam(
                "input_col_idx1",
                label="対象列1",
                required=True
            ),
            params.InputAttributeParam(
                "input_col_idx2",
                label="対象列2",
                required=True
            ),
            params.StringParam(
                "output_col_name",
                label="新しい列名"
            ),
            params.EnumsParam(
                "operator",
                label="演算子",
                enums=Calculation,
                labels=CalculationLabels,
                default_value=Calculation.Add
            ),
            params.BooleanParam(
                "delete_col",
                label="元の列を消しますか？",
                default_value=False
            ),
        )

    def preproc(self, context):
        super().preproc(context)

        self.attr1 = context.get_param("input_col_idx1")
        self.attr2 = context.get_param("input_col_idx2")
        self.output_col_name = context.get_param("output_col_name")
        self.delete_col = context.get_param("delete_col")
        self.operator = context.get_param("operator")

        if self.output_col_name is None:
            self.output_col_name = "+".join([
                self.headers[self.attr1],
                self.headers[self.attr2]])

    def process_header(self, headers, context):
        if self.delete_col:
            headers.pop(self.attr1)
            if self.attr1 != self.attr2:
                headers.pop(self.attr2 - 1)

        headers = headers + [self.output_col_name]

        context.output(headers)

    def process_record(self, record, context):
        try:
            valueA = record[self.attr1]
            valueB = record[self.attr2]
            calc_value = calc(valueA, valueB, self.operator)
            record.append(calc_value)
        except ValueError:
            record.append(None)

        if self.delete_col:
            record.pop(self.attr1)
            if self.attr1 != self.attr2:
                record.pop(self.attr2)

        context.output(record)
