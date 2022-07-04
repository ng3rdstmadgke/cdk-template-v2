#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_template_v2.stack.network_stack import NetworkStack, NetworkContext
from cdk_template_v2.lib.base import ContextLoader

app = cdk.App()
default_context = app.node.try_get_context("default")
overwrite_context = app.node.try_get_context("overwrite")
stage = app.node.try_get_context("stage")

level = 0
if stage:
    level = len(stage.split("."))

if level >= 1:
    network_context = ContextLoader(
        default_context=default_context,
        overwrite_context=overwrite_context,
        stage=stage
    ).get_context(NetworkContext)
    NetworkStack(app, network_context)

if level >= 2:
    pass

#CdkTemplateStack(app, "cdk-template")

app.synth()
