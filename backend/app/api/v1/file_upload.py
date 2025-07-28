# backend/app/api/v1/file_upload.py
"""
文件上传API接口

提供Excel文件上传和解析功能，支持合同清单的批量导入
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.models.project import Project
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem
from app.schemas.contract import ExcelUploadResponse
from app.utils.excel_parser import ContractExcelParser

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 文件上传配置
UPLOAD_DIR = Path("uploads/contracts")
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 确保上传目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_file(file: UploadFile) -> None:
    """
    验证上传的文件
    
    Args:
        file: 上传的文件
        
    Raises:
        HTTPException: 文件验证失败时抛出异常
    """
    # 检查文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件扩展名
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型 {file_extension}，只支持 {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 检查文件大小
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"文件大小超过限制 {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )

def save_uploaded_file(file: UploadFile, project_id: int) -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件
        project_id: 项目ID
        
    Returns:
        str: 保存的文件路径
    """
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    stored_filename = f"contract_project_{project_id}_{timestamp}{file_extension}"
    
    # 完整路径
    file_path = UPLOAD_DIR / stored_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"文件保存成功: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"保存文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

@router.post("/projects/{project_id}/upload-contract-excel", response_model=ExcelUploadResponse)
async def upload_contract_excel(
    project_id: int,
    file: UploadFile = File(..., description="Excel合同清单文件"),
    upload_user_name: str = Form(..., description="上传人员姓名"),
    upload_reason: Optional[str] = Form(None, description="上传原因说明"),
    change_description: Optional[str] = Form(None, description="变更详细说明"),
    db: Session = Depends(get_db)
):
    """
    上传并解析合同清单Excel文件
    
    此接口会：
    1. 验证和保存Excel文件
    2. 解析Excel文件内容
    3. 创建新的合同清单版本
    4. 导入系统分类和设备明细
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 验证文件
    validate_file(file)
    
    # 保存文件
    file_path = save_uploaded_file(file, project_id)
    
    try:
        # 解析Excel文件
        parser = ContractExcelParser()
        parser.load_excel_file(file_path)
        parsed_result = parser.parse_all_sheets()
        
        # SQLAlchemy会自动管理事务，不需要手动begin()
        
        # 创建合同清单版本
        latest_version = db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == project_id
        ).order_by(ContractFileVersion.version_number.desc()).first()
        
        next_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        # 设置之前的版本为非当前版本
        db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == project_id,
            ContractFileVersion.is_current == True
        ).update({"is_current": False})
        
        # 创建新版本记录
        new_version = ContractFileVersion(
            project_id=project_id,
            version_number=next_version_number,
            upload_user_name=upload_user_name,
            original_filename=file.filename,
            stored_filename=Path(file_path).name,
            file_size=Path(file_path).stat().st_size,
            upload_reason=upload_reason,
            change_description=change_description,
            is_current=True
        )
        
        db.add(new_version)
        db.flush()  # 获取版本ID
        
        # 导入系统分类
        category_id_mapping = {}  # 用于映射分类名称到ID
        
        for category_data in parsed_result['categories']:
            new_category = SystemCategory(
                project_id=project_id,
                version_id=new_version.id,
                category_name=category_data['category_name'],
                category_code=category_data['category_code'],
                excel_sheet_name=category_data['excel_sheet_name'],
                budget_amount=category_data.get('budget_amount'),
                description=category_data.get('description'),
                total_items_count=category_data['total_items_count']
            )
            
            db.add(new_category)
            db.flush()  # 获取分类ID
            
            category_id_mapping[category_data['category_name']] = new_category.id
        
        # 导入设备明细
        imported_items_count = 0
        import_errors = []
        
        for item_data in parsed_result['items']:
            try:
                # 获取分类ID
                category_id = category_id_mapping.get(item_data.get('category_name'))
                
                new_item = ContractItem(
                    project_id=project_id,
                    version_id=new_version.id,
                    category_id=category_id,
                    serial_number=item_data.get('serial_number'),
                    item_name=item_data['item_name'],
                    brand_model=item_data.get('brand_model'),
                    specification=item_data.get('specification'),
                    unit=item_data.get('unit', '台'),
                    quantity=item_data['quantity'],
                    unit_price=item_data.get('unit_price'),
                    origin_place=item_data.get('origin_place', '中国'),
                    item_type=item_data.get('item_type', '主材'),
                    remarks=item_data.get('remarks')
                )
                
                # 计算总价
                new_item.calculate_total_price()
                
                db.add(new_item)
                imported_items_count += 1
                
            except Exception as e:
                error_msg = f"导入设备 '{item_data.get('item_name', '未知')}' 失败: {str(e)}"
                import_errors.append(error_msg)
                logger.warning(error_msg)
        
        # 提交事务
        db.commit()
        
        # 关闭解析器
        parser.close()
        
        # 构建响应
        response = ExcelUploadResponse(
            success=True,
            message=f"Excel文件上传和解析成功！导入了 {imported_items_count} 个设备明细",
            version_id=new_version.id,
            parsed_data={
                "total_sheets": parsed_result['summary']['total_sheets'],
                "total_categories": len(parsed_result['categories']),
                "total_items": len(parsed_result['items']),
                "imported_items": imported_items_count,
                "total_amount": float(parsed_result['summary']['total_amount']),
                "categories": [cat['category_name'] for cat in parsed_result['categories']]
            },
            errors=import_errors if import_errors else None
        )
        
        logger.info(f"项目 {project_id} 的Excel文件上传成功，版本ID: {new_version.id}")
        
        return response
        
    except Exception as e:
        # 回滚事务
        db.rollback()
        
        # 删除上传的文件
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        error_msg = f"解析Excel文件失败: {str(e)}"
        logger.error(error_msg)
        
        return ExcelUploadResponse(
            success=False,
            message=error_msg,
            version_id=None,
            parsed_data=None,
            errors=[error_msg]
        )

@router.get("/projects/{project_id}/contract-files")
async def list_contract_files(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目的所有合同清单文件列表
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 查询文件版本列表
    versions = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id
    ).order_by(ContractFileVersion.version_number.desc()).all()
    
    file_list = []
    for version in versions:
        file_info = {
            "version_id": version.id,
            "version_number": version.version_number,
            "original_filename": version.original_filename,
            "stored_filename": version.stored_filename,
            "file_size": version.file_size,
            "upload_user_name": version.upload_user_name,
            "upload_time": version.upload_time,
            "upload_reason": version.upload_reason,
            "is_current": version.is_current,
            "file_exists": os.path.exists(UPLOAD_DIR / version.stored_filename) if version.stored_filename else False
        }
        file_list.append(file_info)
    
    return {
        "project_id": project_id,
        "total_files": len(file_list),
        "files": file_list
    }

@router.delete("/projects/{project_id}/contract-files/{version_id}")
async def delete_contract_file(
    project_id: int,
    version_id: int,
    db: Session = Depends(get_db)
):
    """
    删除合同清单文件和相关数据
    
    注意：此操作将删除指定版本的所有数据，包括系统分类和设备明细
    """
    
    # 查找版本记录
    version = db.query(ContractFileVersion).filter(
        ContractFileVersion.id == version_id,
        ContractFileVersion.project_id == project_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="指定的合同清单版本不存在")
    
    # 检查是否为当前版本
    if version.is_current:
        raise HTTPException(status_code=400, detail="不能删除当前生效的版本")
    
    try:
        # 删除设备明细
        db.query(ContractItem).filter(ContractItem.version_id == version_id).delete()
        
        # 删除系统分类
        db.query(SystemCategory).filter(SystemCategory.version_id == version_id).delete()
        
        # 删除版本记录
        db.delete(version)
        
        # 删除文件
        if version.stored_filename:
            file_path = UPLOAD_DIR / version.stored_filename
            if file_path.exists():
                file_path.unlink()
        
        # 提交事务
        db.commit()
        
        logger.info(f"删除合同清单版本成功: 项目 {project_id}, 版本 {version_id}")
        
        return {
            "success": True,
            "message": f"合同清单版本 {version.version_number} 删除成功"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = f"删除合同清单版本失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)