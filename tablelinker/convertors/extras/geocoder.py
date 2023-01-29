from logging import getLogger

import jageocoder

from ..core import filters, params

logger = getLogger(__name__)

jageocoder_initialized = False


def initialize_jageocoder() -> bool:
    """
    jageocoder を初期化します。
    """
    global jageocoder_initialized
    if jageocoder_initialized:
        return True

    try:
        jageocoder.init()
        jageocoder_initialized = True
    except RuntimeError as e:
        logger.error(e)
        jageocoder_initialized = False

    return jageocoder_initialized


def check_jageocoder(func):
    """
    jageocoder が利用できない場合は常に False を返す decorator
    利用できる場合は func を実行して結果を返します。
    """
    def wrapper(*args, **kwargs):
        if not initialize_jageocoder():
            return False

        return func(*args, **kwargs)

    return wrapper


class ToCodeFilter(filters.InputOutputFilter):
    """
    概要
        住所から自治体コードを計算します。

    コンバータ名
        "geocoder_code"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "within": 検索対象とする都道府県名、市区町村名のリスト []
        * "default": コードが計算できなかった場合の値 ["0"]
        * "with_check_digit": 検査数字を含むかどうか [False]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈（コンバータ固有）
        - ``with_check_digit`` が False の場合は JIS の 5 桁コードを、
          True の場合は総務省の 6 桁コードを返します。
        - 住所が一意ではない場合、最初の候補を選択します。
          精度を向上させたい場合は ``within`` で候補となる
          都道府県名や市区町村名を指定してください。

    サンプル
        「所在地」列から 5 桁自治体コードを算出し、
        先頭に新しく「市区町村コード」列を作って格納します。
        「所在地」列が空欄などで計算できない場合は "0" を格納します。

        .. code-block :: json

            {
                "convertor": "geocoder_code",
                "params": {
                    "input_attr_idx": "所在地",
                    "output_attr_name": "市区町村コード",
                    "output_attr_idx": 0,
                    "within": ["千葉県", "埼玉県", "東京都", "神奈川県"],
                    "default": "0"
                }
            }

    """

    class Meta:
        key = "geocoder_code"
        name = "住所から自治体コード"
        description = """
        住所から自治体コードを返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringListParam(
                "within",
                label="都道府県・市区町村名のリスト",
                required=False,
                default_value=[],
                help_text="検索対象とする都道府県名・市区町村名のリスト。"),
            params.StringParam(
                "default",
                label="デフォルト値",
                required=False,
                default_value="0",
                help_text="コードが取得できない場合の値。"),
            params.BooleanParam(
                "with_check_digit",
                label="検査数字を含む",
                required=False,
                default_value=False,
                help_text="6桁団体コードの場合はチェック。"),)

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        res = len(attrs) == 1 and attrs[0]["attr_type"] == "address"
        return res

    @check_jageocoder
    def initial_context(self, context):
        super().initial_context(context)
        self.within = context.get_param("within")
        self.default = context.get_param("default")
        self.with_check_digit = context.get_param("with_check_digit")
        jageocoder.set_search_config(target_area=self.within)

    def process_filter(self, record, context):
        result = self.default
        value = str(record[self.input_attr_idx])
        if value == '':
            return result

        try:
            candidates = jageocoder.searchNode(value)
            if len(candidates) > 0:
                node = candidates[0][0]
                if self.with_check_digit:
                    if node.level < 3:
                        result = node.get_pref_local_authority_code()
                    else:
                        result = node.get_city_local_authority_code()
                else:
                    if node.level < 3:
                        result = node.get_pref_jiscode() + "000"
                    else:
                        result = node.get_city_jiscode()

        except RuntimeError as e:
            logger.error(e)
            result = self.default

        return result


class ToPrefectureFilter(filters.InputOutputFilter):
    """
    概要
        住所から都道府県名を計算します。

    コンバータ名
        "geocoder_prefecture"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "within": 検索対象とする都道府県名、市区町村名のリスト []
        * "default": 都道府県名が計算できなかった場合の値 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈（コンバータ固有）
        - 住所が一意ではない場合、最初の候補を選択します。
          精度を向上させたい場合は ``within`` で候補となる
          都道府県名や市区町村名を指定してください。

    サンプル
        「所在地」列から都道府県名を計算し、
        先頭に新しく「都道府県名」列を作って格納します。
        「所在地」列が空欄などで計算できない場合は "" を格納します。

        .. code-block :: json

            {
                "convertor": "geocoder_prefecture",
                "params": {
                    "input_attr_idx": "所在地",
                    "output_attr_name": "都道府県名",
                    "output_attr_idx": 0,
                    "within": ["東京都"],
                    "default": "0"
                }
            }

    """

    class Meta:
        key = "geocoder_prefecture"
        name = "住所から都道府県名"
        description = """
        住所から都道府県を返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringListParam(
                "within",
                label="都道府県・市区町村名のリスト",
                required=False,
                default_value=[],
                help_text="検索対象とする都道府県名・市区町村名のリスト。"),
            params.StringParam(
                "default",
                label="デフォルト都道府県名",
                required=False,
                default_value=""),
        )

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    @check_jageocoder
    def initial_context(self, context):
        super().initial_context(context)
        self.within = context.get_param("within")
        self.default = context.get_param("default")
        jageocoder.set_search_config(target_area=self.within)

    def process_filter(self, record, context):
        result = self.default
        value = str(record[self.input_attr_idx])
        if value == '':
            return result

        try:
            candidates = jageocoder.searchNode(value)
            if len(candidates) > 0:
                node = candidates[0][0]
                result = node.get_pref_name()

        except RuntimeError as e:
            logger.error(e)
            result = self.default

        return result


class ToMunicipalityFilter(filters.InputOutputFilter):
    """
    概要
        住所から市区町村名を計算します。

    コンバータ名
        "geocoder_municipality"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "within": 検索対象とする都道府県名、市区町村名のリスト []
        * "default": 都道府県名が計算できなかった場合の値 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈（コンバータ固有）
        - 住所が一意ではない場合、最初の候補を選択します。
          精度を向上させたい場合は ``within`` で候補となる
          都道府県名や市区町村名を指定してください。

    サンプル
        「所在地」列から市区町村名を計算し、
        先頭に新しく「市区町村名」列を作って格納します。
        「所在地」列が空欄などで計算できない場合は "" を格納します。

        .. code-block :: json

            {
                "convertor": "geocoder_municipality",
                "params": {
                    "input_attr_idx": "所在地",
                    "output_attr_name": "市区町村名",
                    "output_attr_idx": 0,
                    "within": ["東京都"],
                    "default": "0"
                }
            }

    """

    class Meta:
        key = "geocoder_municipality"
        name = "住所から市区町村"
        description = """
        住所から市区町村を返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringListParam(
                "within",
                label="都道府県・市区町村名のリスト",
                required=False,
                default_value=[],
                help_text="検索対象とする都道府県名・市区町村名のリスト。"),
            params.StringParam(
                "default",
                label="デフォルト市区町村", required=False),)

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    @check_jageocoder
    def initial_context(self, context):
        super().initial_context(context)
        self.within = context.get_param("within")
        self.default = context.get_param("default")
        jageocoder.set_search_config(target_area=self.within)

    def process_filter(self, record, context):
        result = self.default
        value = str(record[self.input_attr_idx])
        if value == '':
            return result

        try:
            candidates = jageocoder.searchNode(value)
            if len(candidates) > 0:
                node = candidates[0][0]
                if node.level >= 3:
                    result = node.get_city_name()

        except RuntimeError as e:
            logger.error(e)
            result = self.default

        return result


class ToLatLongFilter(filters.InputOutputsFilter):
    """
    概要
        住所から緯度・経度・住所レベルを計算します。

    コンバータ名
        "geocoder_latlong"

    パラメータ（InputOutputsFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_names": 結果を出力する列名のリスト
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "within": 検索対象とする都道府県名、市区町村名のリスト []
        * "default": 都道府県名が計算できなかった場合の値 ["", "", ""]

    注釈（InputOutputsFilter 共通）
        - ``output_attr_idx`` が省略された場合、最後尾に追加します。
        - ``output_attr_names`` で指定された列名が存在している場合、
          ``output_attr_idx`` が指定する位置に移動されます。

    注釈（コンバータ固有）
        - ``output_attr_names`` には、「緯度」「経度」「住所レベル」を
          格納するための3つの列名を指定する必要があります。省略された場合、
          「緯度」「経度」「住所レベル」が列名として利用されます。
        - 住所が一意ではない場合、最初の候補を選択します。
          精度を向上させたい場合は ``within`` で候補となる
          都道府県名や市区町村名を指定してください。

    サンプル
        「所在地」列から経緯度と住所レベルを計算し、
        先頭に新しく「緯度」「経度」「住所レベル」列を作って格納します。
        「所在地」列が空欄などで計算できない場合は "" を格納します。

        .. code-block :: json

            {
                "convertor": "geocoder_latlong",
                "params": {
                    "input_attr_idx": "所在地",
                    "output_attr_names": ["緯度", "経度", "住所レベル"],
                    "output_attr_idx": 0,
                    "within": ["東京都"],
                    "default": ""
                }
            }

    """

    class Meta:
        key = "geocoder_latlong"
        name = "住所から緯度経度"
        description = """
        住所から緯度・経度を生成します
        """
        help_text = None
        params = params.ParamSet(
            params.StringListParam(
                "within",
                label="都道府県・市区町村名のリスト",
                required=False,
                default_value=[],
                help_text="検索対象とする都道府県名・市区町村名のリスト。"),
            params.StringListParam(
                "default",
                label="緯度・経度・住所レベルのデフォルト値",
                required=False,
                default_value=["", "", ""],
                help_text=""),
        )

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    @check_jageocoder
    def initial_context(self, context):
        super().initial_context(context)
        self.within = context.get_param("within")
        self.default = context.get_param("default")
        jageocoder.set_search_config(target_area=self.within)

        # 出力列名が3つ指定されていることを確認
        self.output_attr_names = context.get_param("output_attr_names")
        if self.output_attr_names is None:
            self.output_attr_names = ["緯度", "経度", "住所レベル"]
        elif isinstance(self.output_attr_names, str) or \
                len(self.output_attr_names) != 3:
            raise ValueError((
                "The output_attr_names parameter of geocoder_latlong "
                "requires 3 column names for latitude, longitude and level."))

        # デフォルト値が文字列の場合は 3 列ともその値にする
        # デフォルト値が 3 列でない場合、3 列分になるように加工する
        if isinstance(self.default, str):
            self.default = [self.default] * 3
        elif len(self.default) < 3:
            self.default = (self.default * 3)[0:3]
        elif len(self.default) > 3:
            self.default = self.default[0:3]

    def process_filter(self, record, context):
        result = self.default
        value = str(record[self.input_attr_idx])
        if value == '':
            return result

        try:
            geocode = jageocoder.search(value)
            if geocode["candidates"]:
                lats = [str(candidate["y"])
                        for candidate in geocode["candidates"]]
                lons = [str(candidate["x"])
                        for candidate in geocode["candidates"]]
                lvls = [str(candidate["level"])
                        for candidate in geocode["candidates"]]
                result = [",".join(lats), ",".join(lons), ",".join(lvls)]
        except RuntimeError as e:
            logger.error(e)
            result = self.default

        return result
