from time import sleep
from convertors.core.core import Job, Runner
from convertors.core.filters import encode_filter
from convertors.core.input import encode_input
from convertors.core.output import decode_output, encode_output
from convertors.core.proxy import encode_proxy
from .tasks import run_local_runner


class CeleryRunner(Runner):
    """
    JOBQUEUEで実行します。
    """

    def run(self, filter, filter_params, input, output, proxy=None):
        _filter = encode_filter(filter)
        _input = encode_input(input)
        _output = encode_output(output)
        _proxy = proxy
        worker = run_local_runner.delay(_filter, filter_params, _input, _output, proxy=_proxy)

        # result.id is uuid
        # same
        #   ```
        #   from celery.result import AsyncResult
        #   result = AsyncResult(uuid)
        #   ```

        # wait result.
        # ```
        # while not worker.ready():
        #     pass
        # result = worker.result
        # ```

        return decode_output(worker.result)


class CeleryAsyncRunner(Runner):
    """
    JOBQUEUEで変換処理を実行します。
    変換終わるまで待機します。
    """

    def run(self, filter, filter_params, input, output, proxy=None):
        _filter = encode_filter(filter)
        _input = encode_input(input)
        _output = encode_output(output)
        _proxy = encode_proxy(proxy) if proxy is not None else None
        worker = run_local_runner.delay(_filter, filter_params, _input, _output, proxy=_proxy)

        while not worker.ready():
            sleep(1)

        return decode_output(worker.result)


class CeleryAsyncJob(Job):
    def __init__(self, filter, filter_params, input, output, proxy=None):
        super(CeleryAsyncJob, self).__init__(
            CeleryAsyncRunner(), filter, filter_params, input, output, proxy=proxy,
        )
