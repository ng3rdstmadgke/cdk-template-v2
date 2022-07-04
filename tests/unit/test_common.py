import pytest
import aws_cdk as cdk
from cdk_template_v2.lib.base import (
    ContextLoader,
)
from cdk_template_v2.lib.common import (
    CommonContext,
    CommonStack,
)


def test_common_context_1():
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

        # === === common parameter === ===
        "vpc_id": "vpc-xxxxxxxxxxxxxxxxx",
        "subnet_ids": [],
        "http_proxy": "http://xxx.jp:7080",
        "https_proxy": "http://xxx.jp:7080",
        "no_proxy": [],
        "cidr_internal_network": "10.0.0.0/8",
    }
    overwrite_context = {
        "dev": {
            "aws_account_id": "abc",
            "aws_region": "def",
        },
        "dev.l1": {
            "http_proxy": "",
            "https_proxy": "",
        }
    }
    context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(CommonContext)
    assert context.stage == "dev.l1"
    assert context.aws_account_id == "abc"
    assert context.aws_region == "def"
    assert context.app_name == "sample"
    assert context.termination_protection == False
    assert context.tags == { "Billing Destination": "SAMPLE", "SYS_STACK_APP": "SAMPLE" }
    assert context.vpc_id == "vpc-xxxxxxxxxxxxxxxxx"
    assert context.subnet_ids == []
    assert context.http_proxy == ""
    assert context.https_proxy == ""
    assert context.no_proxy == []
    assert context.cidr_internal_network ==  "10.0.0.0/8"
    assert context.get_resource_name("common") == "sample-common-dev-l1"
    assert context.get_resource_id("common") == "SampleCommonDevL1"


class Stack1(CommonStack):
    STACK_NAME = "common"
    def _resources(self):
        pass

def test_common_stack_1():
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

        # === === common parameter === ===
        "vpc_id": "vpc-xxxxxxxxxxxxxxxxx",
        "subnet_ids": [],
        "http_proxy": "http://xxx.jp:7080",
        "https_proxy": "http://xxx.jp:7080",
        "no_proxy": [],
        "cidr_internal_network": "10.0.0.0/8",
    }
    overwrite_context = {
        "dev": {
            "aws_account_id": "abc",
            "aws_region": "def",
        },
        "dev.l1": {
            "http_proxy": "",
            "https_proxy": "",
        }
    }
    context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(CommonContext)
    stack = Stack1(cdk.App(), context)
    assert stack._get_resource_name("common") == "sample-common-dev-l1"
    assert stack._get_resource_id("common") == "SampleCommonDevL1"
    assert stack.STACK_NAME == "common"