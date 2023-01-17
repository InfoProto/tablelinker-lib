import csv
import json
from logging import getLogger
import os
import sys
import tempfile

from docopt import docopt

from tablelinker import Table

logger = getLogger(__name__)

HELP = """
'tablelinker' は CSV 形式の表データを読み込み、
さまざまなコンバータを適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

Usage:
  {p} -h
  {p} [-d] [-i <file>] [-o <file>] <task>
  {p} mapping [-d] [-i <file>] [-o <file>] [-t <val>] <template>

Options:
  -h --help              このヘルプを表示
  -d --debug             デバッグメッセージを表示
  -i, --input=<file>     入力ファイルを指定（省略時は標準入力）
  -o, --output=<file>    出力ファイルを指定（省略時は標準出力）
  -t, --th=<val>         マッピングしきい値 (0-100) [default: 70]

Parameters:
  <task>        コンバータとパラメータを記述した JSON ファイル
  <template>    表データのテンプレート CSV ファイル

Examples:

- CSV ファイルを変換して標準出力に表示します

  python -m tablelinker -i sample/ma0300000.csv sample/task.json

  適用するコンバータやパラメータは <task> に JSON 形式で記述します。

- CSV ファイルをテンプレートに合わせるマッピング情報を生成します

  python -m tablelinker mapping \
-i sample/sakurai_sightseeing_spots_sjis.csv \
templates/sightseeing_spots.csv

  マッピング情報はタスクとして利用できる JSON 形式で出力されます。
""".format(p='tablelinker')

def convert(args: dict):
    import tablelinker.convertors.basics as basic_convertors
    import tablelinker.convertors.extras as extra_convertors
    basic_convertors.register()
    extra_convertors.register()

    taskfile = args['<task>']
    with open(taskfile, 'r') as jsonf:
        logger.debug("Reading tasks from '{}'.".format(
            taskfile))
        try:
            tasks = json.load(jsonf)
        except json.decoder.JSONDecodeError as e:
            logger.error((
                "タスクファイル '{}' の JSON 表記が正しくありません。"
                "json.decoder.JSONDecodeError: {}").format(taskfile, e))
            sys.exit(-1)

    with tempfile.TemporaryDirectory() as tmpdir:
        if args['--input'] is not None:
            csv_in = args['--input']
        else:
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

        # 結果を出力
        if args['--output'] is None:
            table.write(sys.stdout)
        else:
            table.save(args['--output'])

def mapping(args: dict):
    from tablelinker.convertors import core
    from tablelinker.convertors.core.mapping import ItemsPair
    from collections import OrderedDict

    with tempfile.TemporaryDirectory() as tmpdir:
        if args['--input'] is not None:
            csv_in = args['--input']
        else:
            logger.debug("Reading csv data from STDIN...")
            csv_in = os.path.join(tmpdir, 'input.csv')
            with open(csv_in, 'wb') as fout:
                fout.write(sys.stdin.buffer.read())

        # しきい値
        th = int(args['--th'])

        # 入力 CSV の見出し行を取得
        with core.CsvInputCollection(csv_in) as f:
            headers = f.next()

        # テンプレート CSV の見出し行を取得
        with open(args['<template>'], 'r', newline='') as f:
            reader = csv.reader(f)
            template_headers = reader.__next__()

        # 項目マッピング
        pair = ItemsPair(template_headers, headers)
        mapping = OrderedDict()
        for result in pair.mapping():
            output, header, score = result
            if output is None:
                # マッピングされなかったカラムは除去
                continue

            if score * 100.0 < th or \
                    header is None:
                mapping[output] = None
            else:
                mapping[output] = header

        # 結果出力
        result = json.dumps({
                "convertor":"mapping",
                "params":dict(mapping)
            }, indent=2, ensure_ascii=False)

        if args['--output']:
            with open(args['--output'], 'w') as f:
                print(result, file=f)
        else:
            print(result)


if __name__ == '__main__':
    import logging

    args = docopt(HELP)

    if args['--debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format='%(levelname)s:%(module)s:%(lineno)d:%(message)s')

    if args['--input'] is not None:
        if args['--input'].lower() in ('-', 'stdin'):
            args['--input'] = None

    if args['--output'] is not None:
        if args['--output'].lower() in ('-', 'stdout'):
            args['--output'] = None

    if args['mapping']:
        mapping(args)
    else:
        convert(args)
