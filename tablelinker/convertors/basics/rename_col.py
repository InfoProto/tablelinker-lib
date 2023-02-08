from logging import getLogger

from ...core import convertors, params

logger = getLogger(__name__)


class RenameColConvertor(convertors.Convertor):
    """
    概要
        列名を変更します。

    コンバータ名
        "rename_col"

    パラメータ
        * "input_col_idx": 変更する列の列番号または列名 [必須]
        * "output_col_name": 新しい列名 [必須]

    注釈
        - 新しい列名が元の表に存在していても同じ名前の列を追加します。

    サンプル
        先頭列（0列目）の名称を「都道府県名」に変更します。

        .. code-block:: json

            {
                "convertor": "rename_col",
                "params": {
                    "input_col_idx": 0,
                    "output_col_name": "都道府県名"
                }
            }

    """

    class Meta:
        key = "rename_col"
        name = "カラム名変更"

        description = """
        指定した列名を変更します
        """

        help_text = None

        params = params.ParamSet(
            params.InputAttributeParam(
                "input_col_idx",
                label="入力列",
                description="処理をする対象の列",
                required=True
            ),
            params.StringParam(
                "output_col_name",
                label="新しい列名",
                required=True
            ),
        )

    def process_header(self, headers, context):
        input_col_idx = context.get_param("input_col_idx")
        new_name = context.get_param("output_col_name")
        headers[input_col_idx] = new_name
        context.output(headers)


class RenameColsConvertor(convertors.Convertor):
    """
    概要
        すべての列名を一括変更します。

    コンバータ名
        "rename_cols"

    パラメータ
        * "column_list": 新しい列名のリスト [必須]

    注釈
        - ``column_list`` の列数が既存の列数と等しくないとエラーになります。

    サンプル
        列名を一括変換します。

        .. code-block:: json

            {
                "convertor": "rename_cols",
                "params": {
                    "column_list": [
                        "都道府県名",
                        "人口",
                        "出生数",
                        "死亡数",
                        "（再掲）乳児死亡数",
                        "（再掲）新生児死亡数",
                        "自然増減数",
                        "死産数-総数",
                        "死産数-自然死産",
                        "死産数-人口死産",
                        "周産期死亡数-総数",
                        "周産期死亡数-22週以降の死産数",
                        "周産期死亡数-早期新生児死亡数",
                        "婚姻件数",
                        "離婚件数"
                    ]
                }
            }

    """

    class Meta:
        key = "rename_cols"
        name = "カラム名一括変更"
        description = "カラム名を一括で変更します"
        help_text = None

        params = params.ParamSet(
            params.StringListParam(
                "column_list",
                label="カラム名リスト",
                description="変更後のカラム名のリスト",
                required=True),
        )

    def process_header(self, headers, context):
        output_headers = context.get_param("column_list")
        if len(headers) != len(output_headers):
            logger.error("新しい列数と、既存の列数が一致しません。")
            raise ValueError((
                "The length of 'column_list' must be equal to "
                "the length of the original rows."))

        context.output(output_headers)
