.. _install:

インストール手順
================

.. note::

    他の Python パッケージと同様に、 Tablelinker パッケージは
    多くの依存パッケージをインストールします。システムの
    Python 環境を汚さないように venv などで仮想環境を作成し、
    その仮想環境内にインストールすることをお勧めします。

Tablelinker パッケージのインストール
------------------------------------

Tablelinker は pip コマンドでインストールできます。 ::

    pip install tablelinker

ただし、 Python のバージョンが 3.7 以上、 3.10 以下である必要があります。

3.11 に対応していないのは、 `pytorch が 3.11 をまだサポートしていない
<https://github.com/pytorch/pytorch/issues/86566>`_ ためですので、
そのうちこの問題は解消される予定です。

Mac の場合
^^^^^^^^^^

MacOS Ventura で Xcode をインストールすると Python 3.11 が
インストールされますので、 Tablelinker はインストールできません。

お手数ですが `pyenv <https://github.com/pyenv/pyenv>`_ などを利用して
Python 3.10 をインストールの上でご利用ください。

Windows の場合
^^^^^^^^^^^^^^

Microsoft Store から Python 3.10 をインストールし、
PowerShell を開いて上記の pip コマンドを利用すれば
Tablelinker をインストールできます。

Linux の場合
^^^^^^^^^^^^

Linux ディストリビューションごとのパッケージ管理ツールで
Python と pip をインストールして、ターミナル上で上記の pip コマンドを
利用すれば Tablelinker をインストールできます。


住所辞書データのインストール
----------------------------

住所ジオコーディング機能が必要なコンバータを利用するには、
別途住所辞書データをダウンロード・インストールする必要があります。
住所ジオコーディング機能を利用しない場合は住所辞書データは不要です。 ::

    python -m jageocoder download-dictionary
    python -m jageocoder install-dictionary jusho-20220519.zip

詳細は `jageocoderのインストール手順 <https://jageocoder.readthedocs.io/ja/latest/install.html#install-dictionary>`_ を参照してください。


アンインストール手順
--------------------

住所辞書データをインストールした場合、 Tablelinker パッケージを
アンインストールする前に辞書をアンインストールしてください。 ::

    python -m jageocoder uninstall-dictionary

Tablelinker パッケージは pip uninstall でアンインストールできます。 ::

    pip uninstall tablelinker

