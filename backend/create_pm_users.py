#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/shenyuan-erp/backend')
os.chdir('/home/ubuntu/shenyuan-erp/backend')

from app.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.core.security import get_password_hash
from app.schemas.user import UserRole

def create_project_managers():
    db = SessionLocal()
    
    try:
        # 检查现有项目
        projects = db.query(Project).all()
        print('现有项目：')
        for p in projects:
            print(f'  项目{p.id}: {p.project_name}, 项目经理: {p.project_manager}')
        
        # 创建两个项目经理账号
        pm_users = [
            {'username': 'sunyun', 'name': '孙赟', 'password': 'sunyun123'},
            {'username': 'liqiang', 'name': '李强', 'password': 'liqiang123'}
        ]
        
        for pm_data in pm_users:
            existing = db.query(User).filter(User.username == pm_data['username']).first()
            if existing:
                print(f'用户 {pm_data["username"]} 已存在，更新为项目经理角色')
                existing.role = UserRole.PROJECT_MANAGER
                existing.name = pm_data['name']
            else:
                user = User(
                    username=pm_data['username'],
                    name=pm_data['name'],
                    password_hash=get_password_hash(pm_data['password']),
                    role=UserRole.PROJECT_MANAGER,
                    is_active=True
                )
                db.add(user)
                print(f'创建项目经理: {pm_data["name"]} ({pm_data["username"]})')
        
        db.commit()
        
        # 分配项目管理权限
        # 孙赟负责项目1
        project1 = db.query(Project).filter(Project.id == 1).first()
        if project1:
            project1.project_manager = '孙赟'
            print(f'分配项目1《{project1.project_name}》给孙赟')
        
        # 李强负责项目2
        project2 = db.query(Project).filter(Project.id == 2).first()
        if project2:
            project2.project_manager = '李强'
            print(f'分配项目2《{project2.project_name}》给李强')
        
        db.commit()
        
        # 验证分配结果
        print('\n更新后的项目分配：')
        projects = db.query(Project).all()
        for p in projects:
            print(f'  项目{p.id}: {p.project_name}, 项目经理: {p.project_manager}')
        
        print('\n项目经理账号创建成功！')
        print('孙赟: sunyun/sunyun123 (负责项目1)')
        print('李强: liqiang/liqiang123 (负责项目2)')
        
    except Exception as e:
        print(f'错误: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_project_managers()
