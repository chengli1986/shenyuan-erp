"""
合同清单版本管理API接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.contract import ContractFileVersion
from app.schemas.contract import (
    ContractFileVersionCreate,
    ContractFileVersionResponse,
)

router = APIRouter()


@router.get("/projects/{project_id}/contract-versions", response_model=List[ContractFileVersionResponse])
async def get_contract_versions(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取项目的所有合同清单版本

    返回指定项目的所有合同清单版本列表，按版本号倒序排列
    """

    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")

    # 查询版本列表
    versions = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id
    ).order_by(ContractFileVersion.version_number.desc()).all()

    return versions


@router.get("/projects/{project_id}/contract-versions/current", response_model=ContractFileVersionResponse)
async def get_current_contract_version(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取项目的当前合同清单版本

    返回当前生效的合同清单版本
    """

    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")

    # 查询当前版本
    current_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()

    if not current_version:
        raise HTTPException(status_code=404, detail="该项目暂无当前生效的合同清单版本")

    return current_version


@router.post("/projects/{project_id}/contract-versions", response_model=ContractFileVersionResponse)
async def create_contract_version(
    version_data: ContractFileVersionCreate,
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    创建新的合同清单版本

    注意：创建新版本时，会自动将当前版本设为非当前状态
    """

    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")

    # 验证项目ID匹配
    if version_data.project_id != project_id:
        raise HTTPException(status_code=400, detail="请求路径中的项目ID与数据中的项目ID不匹配")

    try:
        # 获取下一个版本号
        latest_version = db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == project_id
        ).order_by(ContractFileVersion.version_number.desc()).first()

        next_version_number = (latest_version.version_number + 1) if latest_version else 1

        # 如果设为当前版本，需要将其他版本设为非当前
        if getattr(version_data, 'is_current', True):  # 默认新版本为当前版本
            db.query(ContractFileVersion).filter(
                ContractFileVersion.project_id == project_id,
                ContractFileVersion.is_current == True
            ).update({"is_current": False})

        # 创建新版本
        new_version = ContractFileVersion(
            project_id=project_id,
            version_number=next_version_number,
            upload_user_name=version_data.upload_user_name,
            original_filename=version_data.original_filename,
            stored_filename=f"contract_v{next_version_number}_{project_id}_{version_data.original_filename}",
            upload_reason=version_data.upload_reason,
            change_description=version_data.change_description,
            is_optimized=version_data.is_optimized,
            change_evidence_file=version_data.change_evidence_file,
            is_current=True  # 新版本默认为当前版本
        )

        db.add(new_version)
        db.commit()
        db.refresh(new_version)

        return new_version

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建合同清单版本失败：{str(e)}")
