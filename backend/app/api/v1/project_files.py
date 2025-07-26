# 1. 修复 backend/app/api/v1/project_files.py

# 问题1: 缺少文件预览接口
# 问题2: UploadFile.size 在某些版本中不可用
# 问题3: 缺少批量操作接口

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import mimetypes

from app.core.database import get_db
from app.models.project import Project
from app.models.project_file import ProjectFile, FileType
from app.schemas.project_file import (
    ProjectFileResponse, 
    ProjectFileListResponse,
    FileUploadResult,
    ALLOWED_FILE_EXTENSIONS,
    MAX_FILE_SIZE,
    FILE_TYPE_CONFIG
)

router = APIRouter()

# 文件存储目录
UPLOAD_DIRECTORY = Path("uploads/projects")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


@router.get("/{project_id}/files", response_model=ProjectFileListResponse)
async def get_project_files(
    project_id: int,
    file_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取项目文件列表"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 构建查询
    query = db.query(ProjectFile).filter(ProjectFile.project_id == project_id)
    
    # 文件类型筛选
    if file_type:
        try:
            file_type_enum = FileType(file_type)
            query = query.filter(ProjectFile.file_type == file_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的文件类型")
    
    files = query.order_by(ProjectFile.upload_time.desc()).all()
    
    return ProjectFileListResponse(
        items=files,
        total=len(files)
    )


@router.post("/{project_id}/files/upload", response_model=FileUploadResult)
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    description: Optional[str] = Form(None),
    uploaded_by: str = Form("系统管理员"),
    db: Session = Depends(get_db)
):
    """上传项目文件 - 修复版本"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证文件类型枚举
    try:
        file_type_enum = FileType(file_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的文件类型")
    
    # 获取文件扩展名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    file_extension = Path(file.filename).suffix.lower()
    
    # 检查文件格式是否支持
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式: {file_extension}。支持的格式: {', '.join(ALLOWED_FILE_EXTENSIONS.keys())}"
        )
    
    # 读取文件内容并检查大小
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制。最大允许: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="文件不能为空")
    
    # 检查该类型文件数量限制
    existing_count = db.query(ProjectFile).filter(
        ProjectFile.project_id == project_id,
        ProjectFile.file_type == file_type_enum
    ).count()
    
    max_count = FILE_TYPE_CONFIG[file_type_enum]["max_count"]
    if existing_count >= max_count:
        raise HTTPException(
            status_code=400,
            detail=f"{FILE_TYPE_CONFIG[file_type_enum]['name']}最多只能上传{max_count}个文件"
        )
    
    try:
        # 生成唯一文件名
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIRECTORY / str(project_id)
        file_path.mkdir(parents=True, exist_ok=True)
        full_path = file_path / stored_filename
        
        # 保存文件
        with open(full_path, "wb") as buffer:
            buffer.write(content)
        
        # 创建数据库记录
        db_file = ProjectFile(
            project_id=project_id,
            file_name=file.filename,
            file_type=file_type_enum,
            file_size=file_size,
            file_extension=file_extension,
            mime_type=ALLOWED_FILE_EXTENSIONS.get(file_extension),
            stored_filename=stored_filename,
            file_path=str(full_path),
            description=description,
            uploaded_by=uploaded_by
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return FileUploadResult(
            success=True,
            message="文件上传成功",
            file_id=db_file.id,
            file_info=db_file
        )
        
    except Exception as e:
        # 如果数据库操作失败，删除已上传的文件
        if 'full_path' in locals() and full_path.exists():
            full_path.unlink()
        
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/{project_id}/files/{file_id}/download")
async def download_project_file(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """下载项目文件"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = Path(file_record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    return FileResponse(
        path=file_path,
        filename=file_record.file_name,
        media_type=file_record.mime_type
    )


@router.get("/{project_id}/files/{file_id}/preview")
async def preview_project_file(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """预览项目文件 - 新增接口"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = Path(file_record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    # 对于图片和PDF，返回文件流用于预览
    if file_record.file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf']:
        return FileResponse(
            path=file_path,
            media_type=file_record.mime_type,
            headers={"Content-Disposition": "inline"}  # 在浏览器中直接显示
        )
    else:
        raise HTTPException(status_code=400, detail="该文件类型不支持预览")


@router.delete("/{project_id}/files/{file_id}")
async def delete_project_file(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """删除项目文件"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        # 删除磁盘文件
        file_path = Path(file_record.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # 删除数据库记录
        db.delete(file_record)
        db.commit()
        
        return {"message": f"文件 '{file_record.file_name}' 删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@router.get("/{project_id}/files/{file_id}")
async def get_file_info(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """获取文件详细信息 - 新增接口"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return file_record


@router.patch("/{project_id}/files/{file_id}")
async def update_file_info(
    project_id: int,
    file_id: int,
    description: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """更新文件信息 - 新增接口"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 更新描述
    if description is not None:
        file_record.description = description
    
    # 更新文件类型
    if file_type:
        try:
            file_type_enum = FileType(file_type)
            file_record.file_type = file_type_enum
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的文件类型")
    
    try:
        db.commit()
        db.refresh(file_record)
        return file_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新文件信息失败: {str(e)}")


@router.head("/{project_id}/files/{file_id}")
async def check_file_exists(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """检查文件是否存在 - 新增接口"""
    file_record = db.query(ProjectFile).filter(
        ProjectFile.id == file_id,
        ProjectFile.project_id == project_id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = Path(file_record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    return {"status": "exists"}


@router.get("/file-types")
async def get_file_types():
    """获取支持的文件类型配置"""
    return {
        "file_types": [
            {
                "value": file_type.value,
                "label": config["name"],
                "icon": config["icon"],
                "color": config["color"],
                "max_count": config["max_count"],
                "description": config["description"]
            }
            for file_type, config in FILE_TYPE_CONFIG.items()
        ],
        "allowed_extensions": list(ALLOWED_FILE_EXTENSIONS.keys()),
        "max_file_size": MAX_FILE_SIZE,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }