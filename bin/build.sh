#!/bin/bash
function usage {
cat >&2 <<EOS
dockerイメージビルドコマンド

[usage]
 $0 [options]

[options]
 -h | --help:
   ヘルプを表示
 --no-cache:
   キャッシュを使わないでビルド
 --proxy:
   プロキシ設定を有効化
EOS
exit 1
}

PROJECT_ROOT=$(cd $(dirname $0)/..; pwd)
cd ${PROJECT_ROOT}


OPTIONS=
args=()
while [ "$#" != 0 ]; do
  case $1 in
    -h | --help ) usage;;
    --no-cache  ) OPTIONS="$OPTIONS --no-cache";;
    --proxy     ) OPTIONS="$OPTIONS --build-arg proxy=http://xxx.jp:7080";
                  OPTIONS="$OPTIONS --build-arg no_proxy=xxx.xxx.xxx.xxx,yyy.yyy.yyy.yyy";;
    -* | --*    ) error "$1 : 不正なオプションです" ;;
    *           ) args+=("$1");;
  esac
  shift
done

[ "${#args[@]}" != 0 ] && usage

set -e
trap 'echo "[$BASH_SOURCE:$LINENO] - "$BASH_COMMAND" returns not zero status"' ERR

docker build --rm -f docker/Dockerfile -t cdk-template-v2:latest .