import json
from logging import getLogger
import os
import sys
import tempfile

from tablelinker import Table

logger = getLogger(__name__)


def usage():
    print("Usage: cat <input.csv> | python -m tablelinker [-d] <task.json>")
    print((
        "ex. cat sample/sakurai_sightseeing_spots.csv | "
        "python -m tablelinker sample/task.json"))
    sys.exit(-1)


if __name__ == '__main__':
    import logging

    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] in ('-d', '--debug', '--verbose'):
        if len(sys.argv) != 3:
            usage()

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(module)s:%(lineno)d:%(message)s')
        taskfile = sys.argv[2]
    else:
        if len(sys.argv) != 2:
            usage()

        logging.basicConfig(level=logging.WARNING)
        taskfile = sys.argv[1]

    # 利用するコンバータ
    import tablelinker.convertors.basics as basic_convertors
    import tablelinker.convertors.extras as extra_convertors
    basic_convertors.register()
    extra_convertors.register()

    with open(taskfile, 'r') as jsonf:
        logger.debug("Reading tasks from '{}'.".format(
            taskfile))
        tasks = json.load(jsonf)

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.debug("Reading csv data from STDIN...")
        csv_in = os.path.join(tmpdir, 'input.csv')
        with open(csv_in, 'wb') as fout:
            fout.write(sys.stdin.buffer.read())

        logger.debug("Start convertor(s)...")
        table = Table(csv_in)

        if isinstance(tasks, dict):
            # コンバータが一つだけ指定されている場合
            logger.debug("Running {}".format(tasks["convertor"]))
            table = table.convert(
                tasks["convertor"], tasks["params"])
        elif isinstance(tasks, list):
            # 複数のコンバータがリストで指定されている場合
            for task in tasks:
                logger.debug("Running {}".format(task["convertor"]))
                table = table.convert(
                    task["convertor"], task["params"])

        table.write(sys.stdout)