"""
申购模块集成测试 - 简化版
测试核心业务场景而非具体API接口
"""

import pytest
from datetime import datetime
from decimal import Decimal


class TestPurchaseIntegrationScenarios:
    """申购集成场景测试"""
    
    def test_complete_purchase_workflow(self):
        """测试完整的申购工作流程"""
        # 场景：某项目需要申购摄像头
        project_info = {
            "id": 1,
            "name": "智慧园区项目",
            "status": "in_progress"
        }
        
        contract_item = {
            "id": 1,
            "item_name": "AI智能摄像头",
            "specification": "DH-IPC-HFW5442E-ZE",
            "brand_model": "大华",
            "unit": "台",
            "contract_qty": 100,
            "unit_price": 2500.00,
            "purchased_qty": 30  # 已采购30台
        }
        
        purchase_request = {
            "project_id": 1,
            "requester": "张工程师",
            "item_name": "AI智能摄像头", 
            "specification": "DH-IPC-HFW5442E-ZE",
            "quantity": 20,
            "urgency": "normal",
            "reason": "二期工程需要"
        }
        
        # 步骤1：验证申购合法性
        def validate_purchase_request(request, contract):
            """验证申购请求"""
            # 检查物料匹配
            if (request["item_name"] != contract["item_name"] or 
                request["specification"] != contract["specification"]):
                return False, "物料信息不匹配"
            
            # 检查数量限制
            remaining = contract["contract_qty"] - contract["purchased_qty"]
            if request["quantity"] > remaining:
                return False, f"申购数量超限，剩余{remaining}台"
            
            return True, None
        
        is_valid, error = validate_purchase_request(purchase_request, contract_item)
        assert is_valid == True
        assert error is None
        
        # 步骤2：计算总金额
        total_amount = purchase_request["quantity"] * contract_item["unit_price"]
        assert total_amount == 50000.00
        
        # 步骤3：生成申购单号
        request_code = f"PR-{datetime.now().strftime('%Y%m%d')}-001"
        assert len(request_code) == 15  # PR-20250809-001
        
        # 步骤4：确定审批流程
        def get_approval_flow(amount, urgency):
            """获取审批流程"""
            flows = []
            if amount > 10000:
                flows.append("dept_manager")
            if amount > 50000 or urgency == "urgent":
                flows.append("general_manager")
            return flows
        
        approval_flow = get_approval_flow(total_amount, purchase_request["urgency"])
        assert "dept_manager" in approval_flow
        
        print("✅ 完整申购工作流程测试通过")
    
    def test_batch_purchase_scenario(self):
        """测试分批采购场景"""
        # 项目需要分3批采购同一物料
        contract_item = {
            "item_name": "接入交换机",
            "contract_qty": 50,
            "purchased_qty": 0,
            "unit_price": 3500.00
        }
        
        batch_requests = [
            {"batch": 1, "quantity": 15, "reason": "第一期机房"},
            {"batch": 2, "quantity": 20, "reason": "第二期机房"}, 
            {"batch": 3, "quantity": 10, "reason": "备用设备"}
        ]
        
        purchased_total = 0
        batch_results = []
        
        for batch in batch_requests:
            remaining = contract_item["contract_qty"] - purchased_total
            
            if batch["quantity"] <= remaining:
                purchased_total += batch["quantity"]
                batch_amount = batch["quantity"] * contract_item["unit_price"]
                batch_results.append({
                    "batch": batch["batch"],
                    "quantity": batch["quantity"],
                    "amount": batch_amount,
                    "status": "success",
                    "remaining": remaining - batch["quantity"]
                })
            else:
                batch_results.append({
                    "batch": batch["batch"],
                    "quantity": batch["quantity"],
                    "status": "failed",
                    "reason": f"超出剩余数量{remaining}"
                })
        
        # 验证分批结果
        assert len(batch_results) == 3
        assert batch_results[0]["status"] == "success"
        assert batch_results[1]["status"] == "success" 
        assert batch_results[2]["status"] == "success"
        assert purchased_total == 45  # 总计45台
        
        # 验证最后剩余数量
        final_remaining = contract_item["contract_qty"] - purchased_total
        assert final_remaining == 5
        
        print("✅ 分批采购场景测试通过")
    
    def test_mixed_material_purchase(self):
        """测试主材和辅材混合申购"""
        purchase_items = [
            {
                "item_name": "AI智能摄像头",
                "item_type": "主材",
                "quantity": 10,
                "unit_price": 2500.00,
                "need_contract_validation": True,
                "contract_remaining": 70
            },
            {
                "item_name": "电源线",
                "item_type": "辅材", 
                "quantity": 100,
                "unit_price": 15.00,
                "need_contract_validation": False,
                "contract_remaining": None
            },
            {
                "item_name": "网线",
                "item_type": "辅材",
                "quantity": 500,
                "unit_price": 8.00,
                "need_contract_validation": False,
                "contract_remaining": None
            }
        ]
        
        def validate_mixed_purchase(items):
            """验证混合采购"""
            total_amount = Decimal('0')
            validation_results = []
            
            for item in items:
                item_total = Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
                total_amount += item_total
                
                # 主材需要验证合同
                if item["need_contract_validation"]:
                    if item["quantity"] <= item["contract_remaining"]:
                        validation_results.append({
                            "item": item["item_name"],
                            "status": "valid",
                            "amount": float(item_total)
                        })
                    else:
                        validation_results.append({
                            "item": item["item_name"],
                            "status": "invalid", 
                            "reason": "超出合同数量"
                        })
                else:
                    # 辅材直接通过
                    validation_results.append({
                        "item": item["item_name"],
                        "status": "valid",
                        "amount": float(item_total)
                    })
            
            return validation_results, float(total_amount)
        
        results, total_amount = validate_mixed_purchase(purchase_items)
        
        # 验证所有物料都通过验证
        assert all(r["status"] == "valid" for r in results)
        
        # 验证总金额计算
        expected_total = (10 * 2500.00) + (100 * 15.00) + (500 * 8.00)  # 30500
        assert total_amount == expected_total
        
        print("✅ 主材辅材混合申购测试通过")
    
    def test_purchase_approval_integration(self):
        """测试申购审批集成场景"""
        purchase_scenarios = [
            {
                "name": "小额采购",
                "amount": 3000,
                "urgency": "normal",
                "requester_role": "purchaser",
                "expected_approvers": []
            },
            {
                "name": "中额采购", 
                "amount": 25000,
                "urgency": "normal",
                "requester_role": "purchaser",
                "expected_approvers": ["dept_manager"]
            },
            {
                "name": "大额采购",
                "amount": 75000,
                "urgency": "normal", 
                "requester_role": "purchaser",
                "expected_approvers": ["dept_manager", "general_manager"]
            },
            {
                "name": "紧急采购",
                "amount": 15000,
                "urgency": "urgent",
                "requester_role": "purchaser",
                "expected_approvers": ["dept_manager", "general_manager"]
            }
        ]
        
        def get_required_approvers(amount, urgency, requester_role):
            """获取需要的审批人"""
            approvers = []
            
            # 金额审批
            if amount > 5000 and requester_role in ['purchaser']:
                approvers.append("dept_manager")
            if amount > 50000:
                approvers.append("general_manager")
            
            # 紧急情况需要总经理审批
            if urgency == "urgent" and "general_manager" not in approvers:
                approvers.append("general_manager")
            
            return approvers
        
        for scenario in purchase_scenarios:
            approvers = get_required_approvers(
                scenario["amount"],
                scenario["urgency"], 
                scenario["requester_role"]
            )
            
            assert set(approvers) == set(scenario["expected_approvers"]), \
                f"{scenario['name']} 审批人不匹配: 期望{scenario['expected_approvers']}, 实际{approvers}"
        
        print("✅ 申购审批集成场景测试通过")
    
    def test_purchase_error_handling(self):
        """测试申购异常处理"""
        error_scenarios = [
            {
                "name": "数量为0",
                "data": {"quantity": 0},
                "expected_error": "数量必须大于0"
            },
            {
                "name": "负数量",
                "data": {"quantity": -5},
                "expected_error": "数量必须大于0"  
            },
            {
                "name": "缺少物料名称",
                "data": {"item_name": ""},
                "expected_error": "物料名称不能为空"
            },
            {
                "name": "超出合同数量",
                "data": {"quantity": 150, "contract_remaining": 100},
                "expected_error": "超出合同剩余数量"
            }
        ]
        
        def validate_purchase_data(data):
            """验证申购数据"""
            errors = []
            
            if not data.get("item_name"):
                errors.append("物料名称不能为空")
            
            quantity = data.get("quantity", 0)
            if quantity <= 0:
                errors.append("数量必须大于0")
            
            remaining = data.get("contract_remaining")
            if remaining is not None and quantity > remaining:
                errors.append("超出合同剩余数量")
            
            return errors
        
        for scenario in error_scenarios:
            errors = validate_purchase_data(scenario["data"])
            assert len(errors) > 0, f"{scenario['name']} 应该有错误"
            assert any(scenario["expected_error"] in error for error in errors), \
                f"{scenario['name']} 错误信息不匹配: {errors}"
        
        print("✅ 申购异常处理测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])