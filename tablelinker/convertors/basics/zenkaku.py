from logging import getLogger

import jaconv

from tablelinker.core import convertors, params

logger = getLogger(__name__)


class ToHankakuConvertor(convertors.InputOutputConvertor):
    """
    概要
        全角文字を半角文字に変換します。

    コンバータ名
        "to_hankaku"

    パラメータ（InputOutputConvertor 共通）
        * "input_col_idx": 対象列の列番号または列名 [必須]
        * "output_col_idx": 分割した結果を出力する列番号または
          列名のリスト
        * "output_col_name": 結果を出力する列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "kana": カナ文字を変換対象に含める [True]
        * "ascii": アルファベットと記号を対象に含める [True]
        * "digit": 数字を対象に含める [True]
        * "ignore_chars": 対象に含めない文字 [""]

    注釈（InputOutputConvertor 共通）
        - ``output_col_name`` が省略された場合、
          ``input_col_idx`` 列の列名が出力列名として利用されます。
        - ``output_col_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈
        - 変換処理は列名には適用されません。

    サンプル
        「連絡先電話番号」列に含まれる全角数字と記号を半角に置き換えます。

        - タスクファイル例

        .. code-block :: json

            {
                "convertor": "to_hankaku",
                "params": {
                    "input_col_idx": "連絡先電話番号",
                    "output_col_idx": "連絡先電話番号",
                    "kana": false,
                    "ascii": true,
                    "digit": true,
                    "overwrite": true
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     "機関名,部署名,連絡先電話番号\\n"
            ...     "国立情報学研究所,総務チーム,０３－４２１２－２０００\\n"
            ...     "国立情報学研究所,広報チーム,０３－４２１２－２１６４\\n"
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="to_hankaku",
            ...     params={
            ...         "input_col_idx": "連絡先電話番号",
            ...         "output_col_idx": "連絡先電話番号",
            ...         "kana": False,
            ...         "ascii": True,
            ...         "digit": True,
            ...         "overwrite": True,
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            機関名,部署名,連絡先電話番号
            国立情報学研究所,総務チーム,03-4212-2000
            国立情報学研究所,広報チーム,03-4212-2164

    """

    class Meta:
        key = "to_hankaku"
        name = "全角→半角変換"
        description = """
          全角文字を半角文字に変換します
          """
        help_text = None
        params = params.ParamSet(
            params.BooleanParam(
                "kana",
                label="カナ文字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "ascii",
                label="アルファベットと記号を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "digit",
                label="数字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.StringParam(
                "ignore_chars",
                label="対象に含めない文字",
                required=False,
                default_value="",
            ),
        )

    def preproc(self, context):
        super().preproc(context)
        self.kana = context.get_param("kana")
        self.ascii = context.get_param("ascii")
        self.digit = context.get_param("digit")
        self.ignore_chars = context.get_param("ignore_chars")

    def process_convertor(self, record, context):
        return jaconv.z2h(
            record[self.input_col_idx],
            kana=self.kana,
            ascii=self.ascii,
            digit=self.digit,
            ignore=self.ignore_chars)


class ToZenkakuConvertor(convertors.InputOutputConvertor):
    """
    概要
        半角文字を全角文字に変換します。

    コンバータ名
        "to_zenkaku"

    パラメータ（InputOutputConvertor 共通）
        * "input_col_idx": 対象列の列番号または列名 [必須]
        * "output_col_idx": 分割した結果を出力する列番号または
          列名のリスト
        * "output_col_name": 結果を出力する列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "kana": カナ文字を変換対象に含める [True]
        * "ascii": アルファベットと記号を対象に含める [True]
        * "digit": 数字を対象に含める [True]
        * "ignore_chars": 対象に含めない文字 [""]

    注釈（InputOutputConvertor 共通）
        - ``output_col_name`` が省略された場合、
          ``input_col_idx`` 列の列名が出力列名として利用されます。
        - ``output_col_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈
        - 変換処理は列名には適用されません。

    サンプル
        「所在地」列に含まれる半角文字を全角文字に置き換えます。

        - タスクファイル例

        .. code-block :: json

            {
                "convertor": "to_zenkaku",
                "params": {
                    "input_col_idx": "住所",
                    "output_col_idx": "住所",
                    "kana": true,
                    "ascii": true,
                    "digit": true,
                    "overwrite": true
                }
            }

        - コード例

        .. code-block:: python

            >>> import io
            >>> from tablelinker import Table
            >>> stream = io.StringIO((
            ...     'ＮＯ,名称,住所\\n'
            ...     '101100302,特定医療法人平成会平成会病院,北海道札幌市中央区北1条西18丁目1番1\\n'
            ...     '101010421,時計台記念病院,北海道札幌市中央区北1条東1丁目2番地3\\n'
            ...     '101010014,JR札幌病院,北海道札幌市中央区北3条東1丁目1番地\\n'
            ... ))
            >>> table = Table(stream)
            >>> table = table.convert(
            ...     convertor="to_zenkaku",
            ...     params={
            ...         "input_col_idx": "住所",
            ...         "output_col_idx": "住所",
            ...         "kana": True,
            ...         "ascii": True,
            ...         "digit": True,
            ...         "overwrite": True,
            ...     },
            ... )
            >>> table.write(lineterminator="\\n")
            ＮＯ,名称,住所
            101100302,特定医療法人平成会平成会病院,北海道札幌市中央区北１条西１８丁目１番１
            101010421,時計台記念病院,北海道札幌市中央区北１条東１丁目２番地３
            101010014,JR札幌病院,北海道札幌市中央区北３条東１丁目１番地

    """

    class Meta:
        key = "to_zenkaku"
        name = "半角→全角変換"
        description = "半角文字を全角文字に変換します"
        help_text = None
        params = params.ParamSet(
            params.BooleanParam(
                "kana",
                label="カナ文字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "ascii",
                label="アルファベットと記号を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "digit",
                label="数字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.StringParam(
                "ignore_chars",
                label="対象に含めない文字",
                required=False,
                default_value="",
            ),
        )

    def preproc(self, context):
        super().preproc(context)
        self.kana = context.get_param("kana")
        self.ascii = context.get_param("ascii")
        self.digit = context.get_param("digit")
        self.ignore_chars = context.get_param("ignore_chars")

    def process_convertor(self, record, context):
        return jaconv.h2z(
            record[self.input_col_idx],
            kana=self.kana,
            ascii=self.ascii,
            digit=self.digit,
            ignore=self.ignore_chars)
