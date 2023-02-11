.. tablelinker documentation master file, created by
    sphinx-quickstart on Mon Jan 16 05:05:34 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Tablelinker ドキュメント
========================

Tablelinker は CSV や Excel ファイルなどの表データを読み込み、
さまざまな :ref:`convertor` を適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

表データの入力、変換、出力という処理はデータ解析の前処理として不可欠です。
しかし、実際の表データは CSV ファイルと書かれていても
文字エンコーディングや区切り文字がまちまちだったり、
同じシリーズの表データが作成者や作成時期によって
表記や列の並びが少し違うといった細かい問題に悩まされることが多く、
想定外の手間がかかります。

Tablelinker は、主にオープンデータを利用する上でよく利用される変換処理を
ライブラリ化し、オープンソースとして公開することで、
表データの利活用を促進することを目的としています。


.. toctree::
    :maxdepth: 2
    :caption: 目次

    quick_start
    install
    as_command
    as_library
    convertor
    api
