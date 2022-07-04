from typing import Dict, List, Optional
from pydantic import BaseModel
import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2
)
from cdk_template_v2.lib.common import CommonContext, CommonStack

class NetworkPublicSubnets(BaseModel):
    cidr: str
    az: str

class NetworkPrivateSubnets(BaseModel):
    cidr: str
    az: str
    ngw_idx: int

class NetworkContext(CommonContext):
    network_vpc_cidr: str
    network_public_subnets: List[NetworkPublicSubnets]
    network_private_subnets: List[NetworkPrivateSubnets]


class NetworkStack(CommonStack):
    STACK_NAME = "network"
    context: NetworkContext

    def _resources(self):
        # VPC
        vpc = ec2.CfnVPC(
            self, self._get_resource_id("vpc"),
            cidr_block=self.context.network_vpc_cidr,
            tags=[
                cdk.CfnTag(key="Name", value=self._get_resource_name("vpc"))
            ]
        )

        # インターネットゲートウェイ
        igw = ec2.CfnInternetGateway(
            self, self._get_resource_id("igw"),
            tags=[
                cdk.CfnTag(key="Name", value=self._get_resource_name(f"igw"))
            ]
        )

        ec2.CfnVPCGatewayAttachment(
            self, self._get_resource_id("vpcGatewayAttachment"),
            vpc_id=vpc.ref,
            internet_gateway_id=igw.ref
        )

        # パブリックルートテーブル
        public_route_table = ec2.CfnRouteTable(
            self, self._get_resource_id("rtPublic"),
            vpc_id=vpc.ref,
            tags=[
                cdk.CfnTag(key="Name", value=self._get_resource_name("rtPublic"))
            ]
        )
        ec2.CfnRoute(
            self, self._get_resource_id(f"routePublic"),
            route_table_id=public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.ref,
        )

        ngw_list = []
        for (i, info) in enumerate(self.context.network_public_subnets):
            # パブリックサブネット
            public_subnet = ec2.CfnSubnet(
                self, self._get_resource_id(f"public{i}"),
                vpc_id=vpc.ref,
                cidr_block=info.cidr,
                availability_zone=info.az,
                map_public_ip_on_launch=False,
                tags=[
                    cdk.CfnTag(key="Name", value=self._get_resource_name(f"public{i}"))
                ]
            )

            # NATGateway作成
            ngw = ec2.CfnNatGateway(
                self, self._get_resource_id(f"ngw{i}"),
                subnet_id=public_subnet.ref,
                allocation_id = ec2.CfnEIP(
                    self, self._get_resource_id(f"eipNgw{i}"),
                    domain="vpc",
                    tags=[
                        cdk.CfnTag(key="Name", value=self._get_resource_name(f"eipNgw{i}"))
                    ]
                ).attr_allocation_id,
                tags=[
                    cdk.CfnTag(key="Name", value=self._get_resource_name(f"ngw{i}"))
                ]
            )
            ngw_list.append(ngw)

            # ルートテーブルをパブリックサブネットに紐づけ
            ec2.CfnSubnetRouteTableAssociation(
                self, self._get_resource_id(f"assocPublicSubnetRouteTable{i}"),
                route_table_id=public_route_table.ref,
                subnet_id=public_subnet.ref
            )

        for (i, info) in enumerate(self.context.network_private_subnets):
            # プライベートサブネット
            private_subnet = ec2.CfnSubnet(
                self, self._get_resource_id(f"private{i}"),
                vpc_id=vpc.ref,
                cidr_block=info.cidr,
                availability_zone=info.az,
                map_public_ip_on_launch=False,
                tags=[
                    cdk.CfnTag(key="Name", value=self._get_resource_name(f"private{i}"))
                ]
            )

            # プライベートサブネット用のルートテーブル作成
            private_route_table = ec2.CfnRouteTable(
                self, self._get_resource_id(f"rtPrivate{i}"),
                vpc_id=vpc.ref,
                tags=[
                    cdk.CfnTag(key="Name", value=self._get_resource_name(f"rtPrivate{i}"))
                ]
            )
            ec2.CfnRoute(
                self, self._get_resource_id(f"routePrivate{i}"),
                route_table_id=private_route_table.ref,
                destination_cidr_block="0.0.0.0/0",
                nat_gateway_id=ngw_list[info.ngw_idx].ref
            )

            # ルートテーブルをプライベートサブネットに紐づけ
            ec2.CfnSubnetRouteTableAssociation(
                self, self._get_resource_id(f"assocPrivateSubnetRouteTable{i}"),
                route_table_id=private_route_table.ref,
                subnet_id=private_subnet.ref
            )
