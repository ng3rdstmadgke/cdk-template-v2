import re
import copy
from typing import Any, Dict, Iterable, List, Type, Optional
from abc import abstractmethod
import aws_cdk as cdk
from pydantic import BaseModel

class ContextLoader():
    """レイヤ共通で利用するメソッドやメンバが定義されたContextLoaderのベースクラス"""
    context_src: Dict

    def __init__(self, default_context: dict, overwrite_context: dict, stage: str):
        context_src = default_context
        for stage_sub in ContextLoader._stage_iter(stage):
            if stage_sub not in overwrite_context:
                raise Exception(f"overwrite context に {stage_sub} が存在しません")
            context_src = ContextLoader._overwrite_context(
                context_src,
                overwrite_context[stage_sub]
            )
        context_src["stage"] = stage
        self.context_src = context_src

    @staticmethod
    def _stage_iter(stage: str) -> Iterable:
        """stage名を階層でイテレートする
        Args:
          stage (str): ステージ名。"dev.bu1.line1"
        Return:
          "dev.bu1.line1"なら ["dev", "dev.bu1", "dev.bu1.line1"]
        """
        tmp = []
        for v in stage.split("."):
            tmp.append(v)
            yield ".".join(tmp)

    @staticmethod
    def _overwrite_context(base_context: dict, overwrite_context: dict) -> dict:
        copy_base_context = copy.deepcopy(base_context)
        for k, v in overwrite_context.items():
            if k not in copy_base_context:
                raise Exception(f"default context に {k} が存在しません")
            copy_base_context[k] = v
        return copy.deepcopy(copy_base_context)

    def get_context(self, model: Type["BaseModel"]) -> Any:
        return model.parse_obj(self.context_src)


class ContextBase(BaseModel):
    """レイヤ共通で利用するメソッドやメンバが定義されたContextのベースクラス"""
    stage: str
    aws_account_id: str
    aws_region: str
    app_name: str
    termination_protection: bool
    tags: Dict[str, str]

    def get_resource_name(self, name: str) -> str:
        """CFnのスタック名やリソース名を生成するメソッド。ケバブケース"""
        return f"{self.app_name}-{name}-{self.stage.replace('.', '-')}"
        
    def get_resource_id(self, name: str) -> str:
        """CFnのリソースidを生成するメソッド。パスカルケース"""
        resource_name = self.get_resource_name(name)
        return "".join(
            map(
                lambda e: e.capitalize(),
                re.split("[-_]", resource_name)
            )
        )


class StackBase(cdk.Stack):
    """レイヤ共通で利用するメソッドやメンバが定義されたStackのベースクラス

    core.Stack: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/Stack.html
    """

    STACK_NAME: str
    context: ContextBase

    def __init__(self, scope: cdk.Stage, context: ContextBase):
        self.context = context
        super().__init__(
            scope,
            self._get_resource_name(self.STACK_NAME),
            env=cdk.Environment( # スタックがデプロイされるaccountとregionを指定する
                account=self.context.aws_account_id if (self.context.aws_account_id) else None,
                region=self.context.aws_region if (self.context.aws_region) else None,
            ),
            termination_protection=self.context.termination_protection,
        )
        self._add_default_tag()
        self._resources()

    # AWS Resourceについてをデプロイするメソッド
    @abstractmethod
    def _resources(self):
        raise NotImplementedError

    def _get_resource_name(self, name: str) -> str:
        """CFnのスタック名やリソース名を生成するメソッド。ケバブケース"""
        return self.context.get_resource_name(name)

    def _get_resource_id(self, name: str) -> str:
        """CFnのリソースidを生成するメソッド。パスカルケース"""
        return self.context.get_resource_id(name)

    def _add_default_tag(self):
        for k, v in self.context.tags.items():
            cdk.Tags.of(self).add(k, v)