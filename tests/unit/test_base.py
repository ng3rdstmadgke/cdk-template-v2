import pytest
import aws_cdk as cdk
from cdk_template_v2.lib.base import (
    ContextBase,
    StackBase,
    ContextLoader,
)

def test_overwrite_context_1():
    """Stageレイヤのコンテキストの上書きのテスト"""
    stage = "dev"
    default_context = {
        "k1": True,
        "k2": 1,
        "k3": "hello",
        "k4": ["hoge", "fuga", "piyo"],
        "k5": {"foo": "bar"},
        "k6": "abc"
    }
    overwrite_context = {
        "dev": {
            "k1": False,
            "k2": 0,
            "k3": "world",
            "k4": [],
            "k5": {},
        },
    }

    expect = {
        "stage": "dev",
        "k1": False,
        "k2": 0,
        "k3": "world",
        "k4": [],
        "k5": {},
        "k6": "abc"
    }
    result = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    )
    assert result.context_src == expect

def test_overwrite_context_2():
    """Stageレイヤのコンテキストの上書きのテスト"""
    stage = "dev.l1.l2"
    default_context = {
        "k1": "a",
        "k2": "a",
        "k3": "a",
        "k4": "a",
        "k5": "a",
    }
    overwrite_context = {
        "dev": {
            "k1": "b",
        },
        "dev.l1": {
            "k2": "c",
            "k3": "d"
        },
        "dev.l1.l2": {
            "k3": "e",
            "k4": "f"
        }
    }
    expect = {
        "stage": "dev.l1.l2",
        "k1": "b",
        "k2": "c",
        "k3": "e",
        "k4": "f",
        "k5": "a",
    }

    result = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    )

    assert result.context_src == expect

def test_overwrite_context_error_1():
    stage = "dev.l1"
    default_context = {"k1": "a"}
    overwrite_context = {
        "dev": {"k1": "b"}
    }
    with pytest.raises(Exception) as e:
        ContextLoader(
            default_context=default_context,
            overwrite_context=overwrite_context,
            stage=stage
        )
    assert str(e.value) == "overwrite context に dev.l1 が存在しません"

def test_overwrite_context_error_2():
    stage = "dev.l1"
    default_context = {"k1": "a"}
    overwrite_context = {
        "dev": {"k1": "b"},
        "dev.l1": {"k2": "c"}
    }
    with pytest.raises(Exception) as e:
        ContextLoader(
            default_context=default_context,
            overwrite_context=overwrite_context,
            stage=stage
        )

    assert str(e.value) == "default context に k2 が存在しません"

def test_context_base_1():
    stage = "dev.l1"
    default_context = {
        "aws_account_id": "xxxxxxxxxxxx",
        "aws_region": "ap-northeast-1",
        "app_name": "sample",
        "termination_protection": False,
        "tags": {
          "Billing Destination": "SAMPLE",
          "SYS_STACK_APP": "SAMPLE"
        },
    }
    overwrite_context = {
        "dev": {
            "aws_account_id": "abc",
            "aws_region": "def",
        },
        "dev.l1": {}
    }
    context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(ContextBase)
    assert context.stage == "dev.l1"
    assert context.aws_account_id == "abc"
    assert context.aws_region == "def"
    assert context.app_name == "sample"
    assert context.termination_protection == False
    assert context.tags == { "Billing Destination": "SAMPLE", "SYS_STACK_APP": "SAMPLE" }
    assert context.get_resource_name("base") == "sample-base-dev-l1"
    assert context.get_resource_id("base") == "SampleBaseDevL1"


class Stack1(StackBase):
    STACK_NAME = "base"
    def _resources(self):
        pass

def test_stack_base_1():
    stage = "dev.l1"
    default_context = {
        "aws_account_id": "xxxxxxxxxxxx",
        "aws_region": "ap-northeast-1",
        "app_name": "sample",
        "termination_protection": False,
        "tags": {
          "Billing Destination": "SAMPLE",
          "SYS_STACK_APP": "SAMPLE"
        },
    }
    overwrite_context = {
        "dev": {
            "aws_account_id": "abc",
            "aws_region": "def",
        },
        "dev.l1": {}
    }
    context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(ContextBase)
    stack = Stack1(cdk.App(), context)
    assert stack._get_resource_name("base") == "sample-base-dev-l1"
    assert stack._get_resource_id("base") == "SampleBaseDevL1"
    assert stack.STACK_NAME == "base"