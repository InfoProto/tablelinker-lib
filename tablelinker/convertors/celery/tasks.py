from config.celery import app
from convertors.core.core import LocalRunner

from convertors.core.filters import decode_filter
from convertors.core.input import decode_input
from convertors.core.output import decode_output, encode_output
from convertors.core.proxy import decode_proxy


@app.task(name="celery_job_runner")
def run_local_runner(filter, filter_params, input, output, proxy=None):

    _filter = decode_filter(filter)
    _input = decode_input(input)
    _output = decode_output(output)
    _proxy = decode_proxy(proxy) if proxy is not None else None

    LocalRunner().run(_filter, filter_params, _input, _output, proxy=_proxy)

    return encode_output(_output)
