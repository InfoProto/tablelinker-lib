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


class ToGeocodeCodeFilter(filters.InputOutputFilter):
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
        logger.warning("ToGeocoderCodeFilter.can_apply returns {}".format(res))
        return res

    def process_filter(self, output_attr_name, record, context):
        initialize_jageocoder()
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[output_attr_name]))
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


class ToGeocodePrefectureFilter(filters.InputOutputFilter):
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

    def process_filter(self, output_attr_name, record, context):
        initialize_jageocoder()
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[output_attr_name]))
            if len(candidates) > 0:
                node = candidates[0][0]
                result = node.get_pref_name()

        except:  # noqa: E722
            result = context.get_param("default")
        return result


class ToGeocodeMunicipalitiesFilter(filters.InputOutputFilter):
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

    def process_filter(self, output_attr_name, record, context):
        initialize_jageocoder()
        result = context.get_param("default")
        try:
            candidates = jageocoder.searchNode(str(record[output_attr_name]))
            if len(candidates) > 0:
                node = candidates[0][0]
                if node.level >= 3:
                    result = node.get_city_name()

        except:  # noqa: E722
            result = context.get_param("default")
        return result


class ToGeocodeLatitudeFilter(filters.InputOutputFilter):
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

    def process_filter(self, output_attr_name, record, context):
        initialize_jageocoder()
        geocode = jageocoder.search(str(record[output_attr_name]))
        result = ""
        if geocode["candidates"]:
            candidates = [str(candidate["y"]) for candidate in geocode["candidates"]]
            result = ",".join(candidates)
        return result


class ToGeocodeLongitudeFilter(filters.InputOutputFilter):
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

    def process_filter(self, output_attr_name, record, context):
        initialize_jageocoder()
        geocode = jageocoder.search(str(record[output_attr_name]))
        result = ""
        if geocode["candidates"]:
            candidates = [str(candidate["x"]) for candidate in geocode["candidates"]]
            result = ",".join(candidates)

        return result
