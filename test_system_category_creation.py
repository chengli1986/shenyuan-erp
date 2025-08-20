#!/usr/bin/env python3
"""
测试系统分类在新申购单中的保存和显示
"""
import sys
import os
import json
sys.path.append('/home/ubuntu/shenyuan-erp')

from backend.app.database import get_db
from backend.app.models.purchase import PurchaseRequest, PurchaseRequestItem
from backend.app.models.contract import SystemCategory
from backend.app.models.project import Project

def test_system_category_data():
    """检查系统分类数据"""
    db = next(get_db())
    
    print("=== 系统分类数据检查 ===")
    
    # 1. 检查系统分类表
    categories = db.query(SystemCategory).all()
    print(f"系统分类总数: {len(categories)}")
    for cat in categories[:3]:
        print(f"  - ID: {cat.id}, 名称: {cat.category_name}")
    
    # 2. 检查最新申购单的系统分类数据
    print("\n=== 最新申购单的系统分类数据 ===")
    latest_requests = db.query(PurchaseRequest).order_by(PurchaseRequest.id.desc()).limit(5).all()
    
    for req in latest_requests:
        print(f"\n申购单 {req.request_code} (ID: {req.id}):")
        for item in req.items:
            print(f"  明细ID: {item.id}")
            print(f"  物料名称: {item.item_name}")
            print(f"  system_category_id: {item.system_category_id}")
            
            # 如果有系统分类ID，查询分类名称
            if item.system_category_id:
                category = db.query(SystemCategory).filter(
                    SystemCategory.id == item.system_category_id
                ).first()
                print(f"  系统分类名称: {category.category_name if category else 'Not Found'}")
            else:
                print(f"  系统分类名称: null")
    
    db.close()

if __name__ == "__main__":
    test_system_category_data()