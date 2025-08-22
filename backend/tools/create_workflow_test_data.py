#!/usr/bin/env python3
"""
申购单工作流测试数据创建脚本
创建不同工作流状态的申购单，用于测试工作流历史记录和状态显示功能
"""

import sys
import os

# 添加项目路径
sys.path.append('/home/ubuntu/shenyuan-erp/backend')

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import SessionLocal
from app.models.purchase import PurchaseRequest, PurchaseRequestItem, WorkflowLog
from app.models.user import User
from app.models.project import Project
from app.core.security import get_password_hash

def create_workflow_test_data():
    """创建完整的工作流测试数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始创建申购单工作流测试数据...")
        
        # 获取测试用户
        admin = db.query(User).filter(User.username == "admin").first()
        sunyun = db.query(User).filter(User.username == "sunyun").first()
        liqiang = db.query(User).filter(User.username == "liqiang").first()
        purchaser = db.query(User).filter(User.username == "purchaser").first()
        dept_manager = db.query(User).filter(User.username == "dept_manager").first()
        general_manager = db.query(User).filter(User.username == "general_manager").first()
        
        # 获取项目信息
        project2 = db.query(Project).filter(Project.id == 2).first()
        project3 = db.query(Project).filter(Project.id == 3).first()
        
        print(f"📊 找到用户: admin={admin.name if admin else None}, "
              f"sunyun={sunyun.name if sunyun else None}, "
              f"liqiang={liqiang.name if liqiang else None}")
        print(f"📊 找到项目: 项目2={project2.project_name if project2 else None}, "
              f"项目3={project3.project_name if project3 else None}")
        
        # 测试数据配置
        test_scenarios = [
            {
                "name": "草稿状态申购单",
                "project_id": 2,
                "requester": sunyun,
                "status": "draft",
                "current_step": "project_manager",
                "items": [
                    {"item_name": "测试物料A", "quantity": 10, "unit": "个"},
                    {"item_name": "测试物料B", "quantity": 5, "unit": "台"}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager", 
                        "operation_type": "create",
                        "operator": sunyun,
                        "notes": "创建测试申购单"
                    }
                ]
            },
            {
                "name": "已提交待询价申购单",
                "project_id": 2,
                "requester": sunyun,
                "status": "submitted",
                "current_step": "purchaser",
                "items": [
                    {"item_name": "监控摄像头", "quantity": 20, "unit": "台"},
                    {"item_name": "网络交换机", "quantity": 2, "unit": "台"}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager",
                        "operation_type": "create", 
                        "operator": sunyun,
                        "notes": "创建监控设备申购单"
                    },
                    {
                        "from_step": "project_manager",
                        "to_step": "purchaser",
                        "operation_type": "submit",
                        "operator": sunyun,
                        "notes": "提交申购单给采购员询价"
                    }
                ]
            },
            {
                "name": "已询价待部门审批申购单",
                "project_id": 3,
                "requester": liqiang,
                "status": "price_quoted",
                "current_step": "dept_manager",
                "items": [
                    {"item_name": "门禁控制器", "quantity": 5, "unit": "台", "unit_price": 1200.00},
                    {"item_name": "读卡器", "quantity": 10, "unit": "个", "unit_price": 300.00}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager",
                        "operation_type": "create",
                        "operator": liqiang,
                        "notes": "创建门禁设备申购单"
                    },
                    {
                        "from_step": "project_manager", 
                        "to_step": "purchaser",
                        "operation_type": "submit",
                        "operator": liqiang,
                        "notes": "提交给采购部门询价"
                    },
                    {
                        "from_step": "purchaser",
                        "to_step": "dept_manager", 
                        "operation_type": "quote",
                        "operator": purchaser,
                        "notes": "完成询价，推荐供应商A",
                        "operation_data": {
                            "quote_price": 9000.00,
                            "payment_method": "预付30%，货到付70%",
                            "estimated_delivery": "2024-09-01T00:00:00"
                        }
                    }
                ]
            },
            {
                "name": "部门已批待总经理审批申购单",
                "project_id": 2,
                "requester": sunyun,
                "status": "dept_approved", 
                "current_step": "general_manager",
                "items": [
                    {"item_name": "高清摄像机", "quantity": 15, "unit": "台", "unit_price": 2500.00},
                    {"item_name": "录像主机", "quantity": 1, "unit": "台", "unit_price": 8000.00}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager",
                        "operation_type": "create",
                        "operator": sunyun,
                        "notes": "创建高清监控系统申购单"
                    },
                    {
                        "from_step": "project_manager",
                        "to_step": "purchaser", 
                        "operation_type": "submit",
                        "operator": sunyun,
                        "notes": "申购高清监控设备"
                    },
                    {
                        "from_step": "purchaser",
                        "to_step": "dept_manager",
                        "operation_type": "quote",
                        "operator": purchaser,
                        "notes": "询价完成，价格合理",
                        "operation_data": {
                            "quote_price": 45500.00,
                            "payment_method": "分期付款",
                            "estimated_delivery": "2024-09-15T00:00:00"
                        }
                    },
                    {
                        "from_step": "dept_manager",
                        "to_step": "general_manager",
                        "operation_type": "approve", 
                        "operator": dept_manager,
                        "notes": "部门审批通过，设备规格符合项目需求",
                        "operation_data": {
                            "approval_notes": "设备配置合理，供应商信誉良好"
                        }
                    }
                ]
            },
            {
                "name": "最终批准完成申购单",
                "project_id": 3,
                "requester": liqiang,
                "status": "final_approved",
                "current_step": "completed",
                "items": [
                    {"item_name": "智能锁", "quantity": 50, "unit": "把", "unit_price": 800.00},
                    {"item_name": "指纹识别器", "quantity": 10, "unit": "台", "unit_price": 1500.00}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager",
                        "operation_type": "create",
                        "operator": liqiang,
                        "notes": "创建智能门锁系统申购单"
                    },
                    {
                        "from_step": "project_manager",
                        "to_step": "purchaser",
                        "operation_type": "submit", 
                        "operator": liqiang,
                        "notes": "批量采购智能门锁"
                    },
                    {
                        "from_step": "purchaser",
                        "to_step": "dept_manager",
                        "operation_type": "quote",
                        "operator": purchaser,
                        "notes": "多家供应商比价，选择性价比最高方案",
                        "operation_data": {
                            "quote_price": 55000.00,
                            "payment_method": "货到付款",
                            "estimated_delivery": "2024-08-25T00:00:00"
                        }
                    },
                    {
                        "from_step": "dept_manager", 
                        "to_step": "general_manager",
                        "operation_type": "approve",
                        "operator": dept_manager,
                        "notes": "部门审批通过，建议尽快采购",
                        "operation_data": {
                            "approval_notes": "急需物料，建议加急处理"
                        }
                    },
                    {
                        "from_step": "general_manager",
                        "to_step": "completed",
                        "operation_type": "final_approve",
                        "operator": general_manager,
                        "notes": "最终审批通过，授权采购执行",
                        "operation_data": {
                            "approval_notes": "预算充足，供应商可靠，同意采购"
                        }
                    }
                ]
            },
            {
                "name": "被拒绝的申购单",
                "project_id": 2,
                "requester": sunyun,
                "status": "rejected",
                "current_step": "dept_manager",
                "items": [
                    {"item_name": "昂贵设备X", "quantity": 1, "unit": "台", "unit_price": 50000.00}
                ],
                "workflow_logs": [
                    {
                        "from_step": None,
                        "to_step": "project_manager",
                        "operation_type": "create",
                        "operator": sunyun,
                        "notes": "申购高端设备"
                    },
                    {
                        "from_step": "project_manager",
                        "to_step": "purchaser",
                        "operation_type": "submit",
                        "operator": sunyun,
                        "notes": "需要采购高端设备"
                    },
                    {
                        "from_step": "purchaser",
                        "to_step": "dept_manager",
                        "operation_type": "quote",
                        "operator": purchaser,
                        "notes": "询价完成，价格较高",
                        "operation_data": {
                            "quote_price": 50000.00,
                            "payment_method": "一次性付款",
                            "estimated_delivery": "2024-10-01T00:00:00"
                        }
                    },
                    {
                        "from_step": "dept_manager",
                        "to_step": "project_manager",
                        "operation_type": "reject",
                        "operator": dept_manager,
                        "notes": "预算不足，建议寻找性价比更高的替代方案",
                        "operation_data": {
                            "approval_notes": "当前预算无法支撑，建议重新评估需求"
                        }
                    }
                ]
            }
        ]
        
        created_requests = []
        
        # 创建测试申购单
        for i, scenario in enumerate(test_scenarios):
            print(f"\n📝 创建测试场景 {i+1}: {scenario['name']}")
            
            # 计算总金额
            total_amount = sum(
                Decimal(str(item.get('unit_price', 0))) * Decimal(str(item['quantity'])) 
                for item in scenario['items']
            )
            
            # 生成申购单编码
            request_code = f"WORKFLOW-TEST-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            
            # 创建申购单
            purchase_request = PurchaseRequest(
                request_code=request_code,
                project_id=scenario['project_id'],
                requester_id=scenario['requester'].id,
                status=scenario['status'],
                current_step=scenario['current_step'],
                total_amount=total_amount if total_amount > 0 else None,
                request_date=datetime.now() - timedelta(days=len(scenario['workflow_logs'])),
                required_date=datetime.now() + timedelta(days=30),
                remarks=f"工作流测试数据 - {scenario['name']}"
            )
            
            db.add(purchase_request)
            db.flush()  # 获取ID
            
            print(f"   ✅ 申购单: {request_code}, 状态: {scenario['status']}")
            
            # 创建申购明细
            for j, item_data in enumerate(scenario['items']):
                item = PurchaseRequestItem(
                    request_id=purchase_request.id,
                    item_name=item_data['item_name'],
                    quantity=Decimal(str(item_data['quantity'])),
                    unit=item_data['unit'],
                    unit_price=Decimal(str(item_data.get('unit_price', 0))),
                    total_price=Decimal(str(item_data.get('unit_price', 0))) * Decimal(str(item_data['quantity'])),
                    item_type='auxiliary'  # 测试数据标记为辅材
                )
                db.add(item)
                print(f"      - {item_data['item_name']}: {item_data['quantity']}{item_data['unit']}")
            
            # 创建工作流日志
            for k, log_data in enumerate(scenario['workflow_logs']):
                # 计算日志时间（按时间顺序）
                log_time = purchase_request.request_date + timedelta(hours=k*2)
                
                workflow_log = WorkflowLog(
                    purchase_request_id=purchase_request.id,
                    from_step=log_data['from_step'],
                    to_step=log_data['to_step'],
                    operation_type=log_data['operation_type'],
                    operator_id=log_data['operator'].id,
                    operator_name=log_data['operator'].name,
                    operator_role=log_data['operator'].role.value,
                    operation_notes=log_data['notes'],
                    operation_data=log_data.get('operation_data'),
                    created_at=log_time
                )
                db.add(workflow_log)
                print(f"      📊 {log_data['operation_type']}: {log_data['operator'].name} -> {log_data['notes'][:30]}...")
            
            created_requests.append(purchase_request)
            
        # 提交所有更改
        db.commit()
        
        print(f"\n🎉 工作流测试数据创建完成!")
        print(f"📊 总计创建: {len(created_requests)} 个申购单")
        print(f"📊 涵盖状态: draft, submitted, price_quoted, dept_approved, final_approved, rejected")
        
        # 验证创建结果
        print("\n🔍 验证创建结果:")
        for req in created_requests:
            db.refresh(req)
            logs_count = db.query(WorkflowLog).filter(WorkflowLog.purchase_request_id == req.id).count()
            items_count = db.query(PurchaseRequestItem).filter(PurchaseRequestItem.request_id == req.id).count()
            print(f"   {req.request_code}: {req.status} | {logs_count} 条日志 | {items_count} 个明细")
            
        print(f"\n🚀 可以在前端测试以下功能:")
        print(f"   1. 工作流状态显示组件")
        print(f"   2. 工作流历史记录功能")
        print(f"   3. 不同角色的操作权限")
        print(f"   4. 工作流按钮和操作流程")
        
    except Exception as e:
        print(f"❌ 创建测试数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_workflow_test_data()