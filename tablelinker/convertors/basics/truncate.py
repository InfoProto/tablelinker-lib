from ..core import convertors, params, validators


class TruncateConvertor(convertors.InputOutputConvertor):
    """
    概要
        指定した列を指定文字数まで切り詰めます。

    コンバータ名
        "truncate"

    パラメータ（InputOutputConvertor 共通）
        * "input_col_idx": 対象列の列番号または列名 [必須]
        * "output_col_idx": 分割した結果を出力する列番号または
          列名のリスト
        * "output_col_name": 結果を出力する列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "length": 最大文字数 [10]
        * "ellipsis": 切り詰めた場合に追加される記号 ["…"]

    注釈（InputOutputConvertor 共通）
        - ``output_col_name`` が省略された場合、
          ``input_col_idx`` 列の列名が出力列名として利用されます。
        - ``output_col_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈
        - 切り詰め処理は列名には適用されません。
        - もともとの文字数が ``length`` 以下の場合は
          ``ellipsis`` は追加されません。

    サンプル
        「説明」列を 120 文字で切り詰めます。

        .. code-block :: json

            {
                "convertor": "truncate",
                "params": {
                    "input_col_idx": "説明",
                    "length": 120,
                    "ellipsis": "..."
                }
            }

    """

    class Meta:
        key = "truncate"
        name = "文字列を切り詰める"
        description = "文字列を指定された文字数で切り取ります"
        help_text = None
        params = params.ParamSet(
            params.IntParam(
                "length",
                label="最大文字列長",
                required=True,
                validators=(
                    validators.IntValidator(),
                    validators.RangeValidator(min=1),),
                default_value="10",
            ),
            params.StringParam(
                "ellipsis",
                label="省略記号",
                default_value="…"
            ),
        )

    def initial_context(self, context):
        super().initial_context(context)
        self.length = context.get_param("length")
        self.ellipsis = context.get_param("ellipsis")

    def process_convertor(self, record, context):
        value = record[self.input_col_idx]
        if len(value) > self.length:
            value = value[:self.length] + self.ellipsis

        return value
