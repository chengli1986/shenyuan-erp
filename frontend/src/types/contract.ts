// frontend/src/types/contract.ts
/**
 * 合同清单相关的TypeScript类型定义
 */

// 合同清单版本
export interface ContractFileVersion {
  id: number;
  project_id: number;
  version_number: number;
  upload_user_name: string;
  original_filename: string;
  stored_filename: string;
  file_size?: number;
  upload_time: string;
  upload_reason?: string;
  change_description?: string;
  is_optimized: boolean;
  change_evidence_file?: string;
  is_current: boolean;
  created_at: string;
  updated_at?: string;
}

// 创建合同清单版本
export interface ContractFileVersionCreate {
  project_id: number;
  upload_user_name: string;
  original_filename: string;
  upload_reason?: string;
  change_description?: string;
  is_optimized?: boolean;
  change_evidence_file?: string;
}

// 系统分类
export interface SystemCategory {
  id: number;
  project_id: number;
  version_id: number;
  category_name: string;
  category_code?: string;
  excel_sheet_name?: string;
  budget_amount?: number;
  description?: string;
  remarks?: string;
  total_items_count: number;
  created_at: string;
  updated_at?: string;
}

// 创建系统分类
export interface SystemCategoryCreate {
  project_id: number;
  version_id: number;
  category_name: string;
  category_code?: string;
  excel_sheet_name?: string;
  budget_amount?: number;
  description?: string;
  remarks?: string;
}

// 合同清单明细
export interface ContractItem {
  id: number;
  project_id: number;
  version_id: number;
  category_id?: number;
  serial_number?: string;
  item_name: string;
  brand_model?: string;
  specification?: string;
  unit?: string;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  origin_place?: string;
  item_type?: string;
  is_key_equipment?: boolean;
  technical_params?: string;
  optimization_reason?: string;
  remarks?: string;
  is_optimized: boolean;
  original_item_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// 创建合同清单明细
export interface ContractItemCreate {
  project_id: number;
  version_id: number;
  category_id?: number;
  serial_number?: string;
  item_name: string;
  brand_model?: string;
  specification?: string;
  unit?: string;
  quantity: number;
  unit_price?: number;
  origin_place?: string;
  item_type?: string;
  is_key_equipment?: boolean;
  technical_params?: string;
  optimization_reason?: string;
  remarks?: string;
}

// 更新合同清单明细
export interface ContractItemUpdate {
  serial_number?: string;
  item_name?: string;
  brand_model?: string;
  specification?: string;
  unit?: string;
  quantity?: number;
  unit_price?: number;
  origin_place?: string;
  item_type?: string;
  is_key_equipment?: boolean;
  technical_params?: string;
  optimization_reason?: string;
  remarks?: string;
}

// 合同清单明细列表响应
export interface ContractItemListResponse {
  items: ContractItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 合同清单汇总信息
export interface ContractSummary {
  project_id: number;
  current_version?: ContractFileVersion;
  total_versions: number;
  total_categories: number;
  total_items: number;
  total_amount?: number;
}

// Excel上传响应
export interface ExcelUploadResponse {
  success: boolean;
  message: string;
  version_id?: number;
  parsed_data?: {
    total_sheets: number;
    total_categories: number;
    total_items: number;
    imported_items: number;
    total_amount: number;
    categories: string[];
  };
  errors?: string[];
}

// 合同文件信息
export interface ContractFileInfo {
  version_id: number;
  version_number: number;
  original_filename: string;
  stored_filename: string;
  file_size?: number;
  upload_user_name: string;
  upload_time: string;
  upload_reason?: string;
  is_current: boolean;
  file_exists: boolean;
}

// 合同文件列表响应
export interface ContractFileListResponse {
  project_id: number;
  total_files: number;
  files: ContractFileInfo[];
}

// 查询参数
export interface ContractItemQueryParams {
  category_id?: number;
  item_type?: string;
  search?: string;
  page?: number;
  size?: number;
}

// 物料类型枚举
export enum ItemType {
  PRIMARY = '主材',
  AUXILIARY = '辅材'
}

// 文件上传表单数据
export interface FileUploadFormData {
  file: File;
  upload_user_name: string;
  upload_reason?: string;
  change_description?: string;
}