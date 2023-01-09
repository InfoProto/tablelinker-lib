import codecs
import json

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class MTabAnnotate(object):

    MTAB_URL = "https://mtab.app/api/v1/mtab"

    def __init__(self):
        # MEMO: session mode必要か？
        self.session = Session()
        self.result = None
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def annotate(self, file):
        self.result = None
        # info = codecs.lookup("UTF-8-SIG")
        file.seek(0)
        with file.open(mode="rb") as f:
            # with info.streamreader(file, "surrogateescape") as reader:
            try:
                self.result = self.mtab_post(f)
            except Exception as e:
                # TODO mtabのサーバ側からのレスポンスがない場合がある
                print(e)
                self.result = None

    def mtab_post(self, file):
        try:
            files = {"file": ("datafile.csv", file.read(), "text/csv")}
            response = self.session.post(self.MTAB_URL, files=files)

            if response.status_code == 200:
                response_json = response.json()
                return response_json
        except Exception as message:
            raise message


class MTabResult(object):
    def __init__(self):
        self.run_time = None
        self.structure_data = None
        self.cta_data = None
        self.cea_data = None

    def analyze(self, mtab_file):
        with mtab_file.open(mode="rb") as file:
            result_json = json.load(file)
            self.analyze_structure(result_json)
            self.analyze_cta(result_json)
            self.analyze_cea(result_json)

    def analyze_structure(self, result_json):
        if result_json and result_json["tables"]:
            self.run_time = result_json["tables"][0]["run_time"]
            self.structure_data = result_json["tables"][0]["structure"]

    def analyze_cta(self, result_json):
        if result_json and result_json["tables"]:
            self.cta_data = result_json["tables"][0]["semantic"]["cta"]

    def analyze_cea(self, result_json):
        if result_json and result_json["tables"]:
            self.cea_data = result_json["tables"][0]["semantic"]["cea"]
