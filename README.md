# cdk.sh用のイメージビルド

```bash
./bin/build.sh
```

# デプロイ


## 設定ファイルの修正

```bash
vim cdk.json
```

## cdkコマンドの実行
引数として指定するコンテキスト

```
-c stage={stage_name} : ステージ名を指定します。"." で区切ることでパラメータの階層を指定することができます。 (dev, dev.l1.l2)
```

```bash
# デプロイできるスタック一覧
./cdk.sh list -c stage=dev

# cfn出力
./cdk.sh synth -c stage=dev.l1 cdktpl-network-dev-l1

# bootstrap
./cdk.sh bootstrap -c stage=dev.l1

# デプロイ
./cdk.sh deploy -c stage=dev.l1 cdktpl-network-dev-l1

# 削除
./cdk.sh destroy -c stage=dev.l1 cdktpl-network-dev-l1
```

# プロジェクト構成

- cdk_template_v2
  - lib/  
  Stack, Contextの基底クラス、共通利用クラスを定義します
  - stack/  
  Stack, Context の実装ディレクトリです
    - stack_base.py  
    `Stack` が継承すべき基底クラスが定義されています。
- docker/  
CDKを実行するためのdockerイメージの定義が格納されています
- tests/  
単体テスト
- .cdk_version  
node.jsとpythonでcdkのバージョンを一致させるためのバージョン定義ファイルです。  
このファイルは `docker/Dockerfile` , `setup.py` にてcdkのバージョン指定に利用されています。
- app.py  
CDKのエントリーポイントです
- cdk.json  
CDKの変数定義ファイルです。  
`context.default` にはデフォルトの設定値を定義します。  
`context.overwrite` にはstage, lineレイヤで上書きするための設定を記述します。
- setup.py  
依存パッケージが定義されています。`.cdk_version` ファイルを読み込んでインストールするcdkバージョンを決定しています。



# 新しいスタックの追加

```bash
touch cdk_template_v2/stack/additonal_stack.py
```

## cdk.json にパラメータを追加

新しく追加するスタックで利用するパラメータを `context.default` 配下に定義します。

```js:cdk.json
{
  "app": "python3 app.py",
  "watch": {
    // ...
  },
  "context": {
    "default": {
      "additional_param_1": "hogehoge@example.com",
      "additional_param_2": [1, 2, 3],
      "additional_param_3": {"a": True, "b": False},
      // ...
    }
    // ...
  }
}
```

### パラメータを上書きしたい場合

```js:cdk.json
{
  "app": "python3 app.py",
  "watch": {
    // ...
  },
  "context": {
    "default": {
      "additional_param_1": "hogehoge@example.com",
      "additional_param_2": [1, 2, 3],
      "additional_param_3": {"a": True, "b": False},
      // ...
    },
    "overwrite": {
        "dev": { // -c stage=... で指定される value をキーに設定して上書きするパラメータを指定する
            "additional_param_1": "HOGEHOGE@example.com",
            "additional_param_2": [],
        },
        "dev.l1": { // -c stage=dev.l1 と指定した場合は "dev.l1" と "dev" に定義したパラメータが上書きされる
            "additional_param_3": {},
        }
    }
    // ...
  }
}

```

## コンテキストの実装

Contextクラスにはcdk.jsonで定義したパラメータをプロパティとして定義します。

```python:cdk_template_v2/stack/additonal_stack.py
from cdk_template_v2.lib.common import CommonContext, CommonStack

class AdditionalContext(CommonContext):
    additional_param_1: str
    additional_param_2: List[str]
    additional_param_3: Dict[str, bool]
```


## スタックの実装

`cdk_template_v2/stack/{stack_name}_stack.py` では、awsのリソースを定義します。

- `STACK_NAME` プロパティ  
他のスタックと重複しない、ユニークなスタック名を付けます。
- `context` プロパティ  
先ほど定義したコンテキストクラス( `AdditionalContext` )を型として指定します
- `_resources(self)` メソッド  
AWSのリソースを定義しますのリソースを定義します。

```python:cdk_template_v2/stack/additonal_stack.py
from cdk_template_v2.lib.common import CommonContext, CommonStack

class AdditionalStack(CommonStack):
    STACK_NAME = "additional"
    context: AdditionalContext

    def _resources(self):
        """AWSのリソースを定義します。"""
        topic = sns.Topic(
            self, self._get_resource_id("sampleTopic"),
            topic_name=self._get_resource_name("sampleTopic")
        )

        topic.add_subscription(subs.EmailSubscription(
            self.context.additional_param_1
        ))
```

## app.py に Stack を実装

コンテキストとスタックの実装が終わったら、 `app.py` にスタックを追加します。  
※ レベルは `-c stage=...` で指定される値が `.` 区切りで何階層あるかを表しています。  
例) `-c stage=dev` ならレベル1の分岐が実行されます。 `-c stage=dev.l1` ならレベル１と2の分岐が実行されます。



```python:app.py
import aws_cdk as cdk
from cdk_template_v2.stack.additional_stack import AdditionalStack, AdditionalContext

app = cdk.App()
default_context = app.node.try_get_context("default")
overwrite_context = app.node.try_get_context("overwrite")
stage = app.node.try_get_context("stage")

if not stage:
    raise Exception("-c stage=<STAGE> が指定されていません")

level = len(stage.split("."))
if level >= 1:
    # レベル1のスタック
    additional_context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(AdditionalContext)
    AdditionalStack(app, ecr_context)

if level >= 2:
    # レベル2のスタック
    pass

# ...
```