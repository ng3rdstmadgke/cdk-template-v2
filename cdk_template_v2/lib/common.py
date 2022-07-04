from typing import Dict, Optional, List
from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
)
from cdk_template_v2.lib.base import ContextBase, StackBase


class CommonContext(ContextBase):
    """レイヤ共通で利用するメソッドやメンバが定義されたContextのベースクラス"""
    vpc_id: str
    subnet_ids: List[str]
    http_proxy: str
    https_proxy: str
    no_proxy: List[str]
    cidr_internal_network: str

class CommonStack(StackBase):
    STACK_NAME: str
    context: CommonContext

    vpc_ref: Optional[ec2.IVpc] = None
    subnet_refs: Dict[str, ec2.ISubnet] = {}
    role_refs: Dict[str, iam.IRole] = {}

    def _get_vpc(self) -> ec2.IVpc:
        """cdk.jsonのvpc_idに指定されているVPCの参照を取得"""
        if self.vpc_ref is None:
            self.vpc_ref = ec2.Vpc.from_lookup(
                self, self._get_resource_id("defaultVpcRef"),
                vpc_id=self.context.vpc_id,
            )
        return self.vpc_ref

    def _get_subnet(self, subnet_id: str) -> ec2.ISubnet:
        """指定されたsubnet_idからsubnetの参照を取得"""
        if subnet_id not in self.subnet_refs:
            self.subnet_refs[subnet_id] = ec2.Subnet.from_subnet_id(
                self, self._get_resource_id(f"{subnet_id}Ref"),
                subnet_id=subnet_id,
            )
        return self.subnet_refs[subnet_id]

    def _get_subnet_selection(self, subnet_ids: List[str]) -> ec2.SubnetSelection:
        subnets = [self._get_subnet(subnet_id) for subnet_id in subnet_ids]
        return ec2.SubnetSelection(subnets=subnets)

    def _get_role(self, role_name: str) -> iam.IRole:
        """指定されたIAM Role名からRoleの参照を取得"""
        if role_name not in self.role_refs:
            self.role_refs[role_name] = iam.Role.from_role_arn(
                self, self._get_resource_id(f"{role_name}Ref"),
                role_arn=f"arn:aws:iam::{self.context.aws_account_id}:role/{role_name}",
            )
        return self.role_refs[role_name]