import re

from jeraconv import jeraconv

from ..core import filters, params


class ToSeirekiFilter(filters.InputOutputFilter):
    """
    概要
        和暦から西暦を計算します。

    コンバータ名
        "to_seireki"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    サンプル
        「年月日」列が和暦ならば西暦に変換します。

        .. code-block :: json

            {
                "convertor": "to_seireki",
                "params": {
                    "input_attr_idx": "年月日",
                    "output_attr_idx": "年月日",
                    "overwrite": true
                }
            }

    """

    j2w = None

    class Meta:
        key = "to_seireki"
        name = "和暦西暦変換"
        description = """
        和暦を西暦に変換します
        """
        help_text = None
        params = params.ParamSet()

    def initial_context(self, context):
        super().initial_context(context)
        if self.__class__.j2w is None:
            self.__class__.j2w = jeraconv.J2W()

        # self.re_pattern = re.compile((
        #     r"明治(元|\d+)年|大正(元|\d+)年|昭和(元|\d+)年"
        #     r"|平成(元|\d+)年|令和(元|\d+)年"))

        self.re_pattern = re.compile(r"(..(元|\d+)年?)")

    def process_filter(self, record, context):
        result = record[self.input_attr_idx]

        targets = self.re_pattern.findall(result)
        for target in targets:
            try:
                yy = "{:d}年".format(self.j2w.convert(target[0]))
                result = result.replace(target[0], yy)
            except ValueError as e:
                # 和暦ではない
                continue

        return result


class ToWarekiFilter(filters.InputOutputFilter):
    """
    概要
        西暦から和暦を計算します。

    コンバータ名
        "to_wareki"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    サンプル
        「年月日」列が西暦ならば和暦に変換します。

        .. code-block :: json

            {
                "convertor": "to_wareki",
                "params": {
                    "input_attr_idx": "年月日",
                    "output_attr_idx": "年月日",
                    "overwrite": true
                }
            }

    """

    w2j = None

    class Meta:
        key = "to_wareki"
        name = "西暦和暦変換"
        description = """
        西暦を和暦に変換します
        """
        help_text = None
        params = params.ParamSet()

    def initial_context(self, context):
        super().initial_context(context)
        if self.__class__.w2j is None:
            self.__class__.w2j = jeraconv.W2J()

        # self.re_pattern = re.compile((
        #     r"明治(元|\d+)年|大正(元|\d+)年|昭和(元|\d+)年"
        #     r"|平成(元|\d+)年|令和(元|\d+)年"))

        self.re_pattern = re.compile(r"((西暦|)([12]\d{3})年?)")

    def process_filter(self, record, context):
        result = record[self.input_attr_idx]

        targets = self.re_pattern.findall(result)
        for target in targets:
            try:
                converted = self.w2j.convert(
                    int(target[2]), 1, 1, return_type='dict')
                yy = "{}{:d}".format(
                    converted['era'], converted['year'])
                if target[0][-1] == "年":
                    yy += "年"

                result = result.replace(target[0], yy)
            except ValueError as e:
                # 西暦ではない
                continue

        return result
