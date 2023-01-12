from ..core import filters, params

from ...mtab.mtab import MTabResult


class MtabFilter(filters.InputOutputFilter):
    """
    Mtabデータからwikidataと、dbpediaの列を追加する。
    """

    class Meta:
        key = "mtab"
        name = "Mtabデータからwikidataと、dbpediaの列を追加する"
        description = """
        Mtabデータからwikidataの列を追加します
        """
        help_text = ""
        params = params.ParamSet()

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return True

    def initial(self, context):
        mtab_file = context._input._dataset.mtab_file
        mtab_result = None

        if mtab_file and mtab_file.size > 0:
            mtab_result = MTabResult()
            mtab_result.analyze(mtab_file)

        if mtab_result:
            input_attr_idx = context.get_param("input_attr_idx")
            wikidata_map = {}
            for data in mtab_result.cea_data:
                row = data["target"][0]
                col = data["target"][1]
                if col == input_attr_idx:
                    wikidata = data["annotation"]["wikidata"]
                    wikidata_map[row] = wikidata
            context.set_data("wikidata", wikidata_map)

    def process_filter(self, input_attr_idx, record, context):
        wikidata = context.get_data("wikidata")
        if wikidata:
            return wikidata[input_attr_idx]
        else:
            return None
