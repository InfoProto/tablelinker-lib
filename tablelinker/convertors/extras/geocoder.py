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
    住所から自治体コードを返すフィルターです。
    """

    class Meta:
        key = "geocoder_code"
        name = "住所から自治体コード"
        description = """
        住所から自治体コードを返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringParam(
                "default",
                label="デフォルト値",
                required=False,
                default_value="0",
                help_text="コードが取得できない場合の値。"),
            params.BooleanParam(
                "withCheckDigit",
                label="検査数字を含む",
                required=False,
                default_value=False,
                help_text="6桁団体コードの場合はチェック。"),)

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        res = len(attrs) == 1 and attrs[0]["attr_type"] == "address"
        return res

    def initial(self, context):
        super().initial(context)
        initialize_jageocoder()

    def process_filter(self, input_attr_idx, record, context):
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[input_attr_idx]))
            if len(candidates) > 0:
                node = candidates[0][0]
                if context.get_param("withCheckDigit"):
                    if node.level < 3:
                        result = node.get_pref_local_authority_code()
                    else:
                        result = node.get_city_local_authority_code()
                else:
                    if node.level < 3:
                        result = node.get_pref_jiscode() + "000"
                    else:
                        result = node.get_city_jiscode()

        except RuntimeError as e:  # noqa: E722
            logger.error(e)
            result = context.get_param("default")
        return result


class ToPrefectureFilter(filters.InputOutputFilter):
    """
    住所から都道府県を返すフィルターです。
    """

    class Meta:
        key = "geocoder_prefecture"
        name = "住所から都道府県名"
        description = """
        住所から都道府県を返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringParam(
                "default",
                label="デフォルト都道府県名", required=False),)

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    def initial(self, context):
        super().initial(context)
        initialize_jageocoder()

    def process_filter(self, input_attr_idx, record, context):
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[input_attr_idx]))
            if len(candidates) > 0:
                node = candidates[0][0]
                result = node.get_pref_name()

        except:  # noqa: E722
            result = context.get_param("default")
        return result


class ToMunicipalitiesFilter(filters.InputOutputFilter):
    """
    住所から市区町村を返すフィルターです。
    """

    class Meta:
        key = "geocoder_municipalities"
        name = "住所から市区町村"
        description = """
        住所から市区町村を返します
        """
        help_text = None
        params = params.ParamSet(
            params.StringParam(
                "default",
                label="デフォルト市区町村", required=False),)

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    def initial(self, context):
        super().initial(context)
        initialize_jageocoder()

    def process_filter(self, input_attr_idx, record, context):
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[input_attr_idx]))
            if len(candidates) > 0:
                node = candidates[0][0]
                if node.level >= 3:
                    result = node.get_city_name()

        except:  # noqa: E722
            result = context.get_param("default")
        return result


class ToLatitudeFilter(filters.InputOutputFilter):
    """
    住所から緯度を返すフィルターです。
    """

    class Meta:
        key = "geocoder_latitude"
        name = "住所から緯度"
        description = """
        住所から緯度を生成します
        """
        help_text = None
        params = params.ParamSet()

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    def initial(self, context):
        super().initial(context)
        initialize_jageocoder()

    def process_filter(self, input_attr_idx, record, context):
        geocode = jageocoder.search(str(record[input_attr_idx]))
        result = ""
        if geocode["candidates"]:
            candidates = [str(candidate["y"]) for candidate in geocode["candidates"]]
            result = ",".join(candidates)
        return result


class ToLongitudeFilter(filters.InputOutputFilter):
    """
    住所から経度を返すフィルターです。
    """

    class Meta:
        key = "geocoder_longitude"
        name = "住所から経度"
        description = """
        住所から経度を返します
        """
        help_text = None
        params = params.ParamSet()

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    def initial(self, context):
        super().initial(context)
        initialize_jageocoder()

    def process_filter(self, input_attr_idx, record, context):
        geocode = jageocoder.search(str(record[input_attr_idx]))
        result = ""
        if geocode["candidates"]:
            candidates = [str(candidate["x"]) for candidate in geocode["candidates"]]
            result = ",".join(candidates)

        return result


class ToLatLongFilter(filters.InputOutputsFilter):
    """
    住所から緯度・経度を返すフィルターです。
    """

    class Meta:
        key = "geocoder_latlong"
        name = "住所から緯度経度"
        description = """
        住所から緯度・経度を生成します
        """
        help_text = None
        params = params.ParamSet()

    @classmethod
    @check_jageocoder
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return len(attrs) == 1 and attrs[0]["attr_type"] == "address"

    @check_jageocoder
    def initial(self, context):
        # 出力列名が3つ指定されていることを確認
        output_attr_names = context.get_param("output_attr_names")
        if isinstance(output_attr_names, str) or \
                len(output_attr_names) != 3:
            raise ValueError((
                "The output_attr_names parameter of geocoder_latlong "
                "requires 3 column names for latitude, longitude and level."))

        initialize_jageocoder()
        super().initial(context)

    def process_filter(self, input_attr_idx, record, context):
        geocode = jageocoder.search(str(record[input_attr_idx]))
        result = ["", ""]
        if geocode["candidates"]:
            lats = [str(candidate["y"]) for candidate in geocode["candidates"]]
            lons = [str(candidate["x"]) for candidate in geocode["candidates"]]
            lvls = [str(candidate["level"]) for candidate in geocode["candidates"]]
            result = [",".join(lats), ",".join(lons), ",".join(lvls)]

        return result
