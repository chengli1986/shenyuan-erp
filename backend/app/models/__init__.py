# backend/app/models/__init__.py
# 数据库模型导入文件
# 导入所有数据库模型，确保SQLAlchemy能够发现和创建对应的数据表

# 导入项目相关模型
from .project import Project  # 项目基础信息模型
from .project_file import ProjectFile  # 项目文件管理模型

# 导入合同清单相关模型
from .contract import (
    ContractFileVersion,  # 合同清单版本管理
    SystemCategory,       # 系统分类管理
    ContractItem         # 合同清单明细项
)

# 导出所有模型，方便其他模块导入
__all__ = [
    "Project",
    "ProjectFile", 
    "ContractFileVersion",
    "SystemCategory",
    "ContractItem"
]