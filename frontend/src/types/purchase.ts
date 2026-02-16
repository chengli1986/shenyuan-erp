/**
 * 采购请购相关的TypeScript类型定义
 */

// 供应商、辅材模板、入库批次类型 — 从子模块导入并重新导出
export type {
  Supplier,
  SupplierCreate,
  SupplierUpdate,
  SupplierListResponse,
  SupplierQueryParams,
  AuxiliaryTemplateItem,
  AuxiliaryTemplate,
  AuxiliaryTemplateCreate,
  AuxiliaryRecommendation,
  InboundBatch,
  InboundBatchCreate,
} from './purchase-supplier';

// 枚举类型
export enum PurchaseStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  PRICE_QUOTED = 'price_quoted',
  DEPT_APPROVED = 'dept_approved',
  FINAL_APPROVED = 'final_approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed'
}

export enum ItemType {
  MAIN_MATERIAL = 'main',
  AUXILIARY_MATERIAL = 'auxiliary'
}

export enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected'
}

export enum UserRole {
  ADMIN = 'admin',
  GENERAL_MANAGER = 'general_manager',
  DEPT_MANAGER = 'dept_manager',
  PROJECT_MANAGER = 'project_manager',
  PURCHASER = 'purchaser',
  WAREHOUSE_KEEPER = 'warehouse_keeper',
  FINANCE = 'finance',
  WORKER = 'worker'
}

// 申购明细相关类型
export interface PurchaseItem {
  id: number;
  request_id: number;
  contract_item_id?: number;
  item_name: string;
  specification?: string;
  brand?: string;
  unit: string;
  quantity: number;
  item_type: ItemType;
  unit_price?: number;
  total_price?: number;
  supplier_id?: number;
  supplier_name?: string;
  supplier_contact?: string;
  supplier_info?: Record<string, unknown>;
  estimated_delivery?: string;
  received_quantity: number;
  remaining_quantity: number;
  status: string;
  remarks?: string;
}

export interface PurchaseItemCreate {
  contract_item_id?: number;
  item_name: string;
  specification?: string;
  brand?: string;
  unit: string;
  quantity: number;
  item_type: ItemType;
  remarks?: string;
}

export interface PurchaseItemPriceQuote {
  item_id: number;
  unit_price: number;
  total_price?: number;
  supplier_id?: number;
  supplier_name?: string;
  supplier_contact?: string;
  estimated_delivery?: string;
}

export interface PurchaseItemWithoutPrice {
  id: number;
  request_id: number;
  contract_item_id?: number;
  item_name: string;
  specification?: string;
  brand?: string;
  unit: string;
  quantity: number;
  item_type: ItemType;
  supplier_name?: string;
  estimated_delivery?: string;
  received_quantity: number;
  remaining_quantity: number;
  status: string;
  remarks?: string;
}

// 申购单相关类型
export interface PurchaseRequest {
  id: number;
  request_code: string;
  project_id: number;
  request_date: string;
  requester_id: number;
  required_date?: string;
  status: PurchaseStatus;
  total_amount?: number;
  approval_notes?: string;
  remarks?: string;
  created_at: string;
  updated_at?: string;
}

export interface PurchaseRequestCreate {
  project_id: number;
  required_date?: string;
  remarks?: string;
  items: PurchaseItemCreate[];
}

export interface PurchaseRequestUpdate {
  required_date?: string;
  remarks?: string;
  status?: PurchaseStatus;
}

export interface PurchaseRequestWithItems extends PurchaseRequest {
  items: PurchaseItem[];
  requester_name?: string;
  project_name?: string;
}

export interface PurchaseRequestWithoutPrice extends Omit<PurchaseRequest, 'total_amount'> {
  items: PurchaseItemWithoutPrice[];
  requester_name?: string;
  project_name?: string;
  total_amount?: null;
}

export interface PurchaseRequestSubmit {
  // 提交申购单不需要额外参数
}

export interface PurchaseRequestQuote {
  items: PurchaseItemPriceQuote[];
}

export interface PurchaseRequestApprove {
  approval_status: ApprovalStatus;
  approval_notes?: string;
}

// 审批记录相关类型
export interface ApprovalRecord {
  id: number;
  request_id: number;
  approver_id: number;
  approver_name?: string;
  approver_role: string;
  approval_level: number;
  approval_status: ApprovalStatus;
  approval_notes?: string;
  approval_date: string;
  can_view_price: boolean;
}

// 列表响应类型
export interface PurchaseRequestListResponse {
  items: PurchaseRequestWithItems[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 统计信息类型
export interface PurchaseStatistics {
  total_requests: number;
  pending_approval: number;
  approved: number;
  total_amount: number;
  main_material_amount: number;
  auxiliary_material_amount: number;
}

// 申购单详情数据（API返回的完整数据）
export interface PurchaseDetailData {
  id: number;
  request_code: string;
  project_id: number;
  project_name?: string;
  requester_id: number;
  requester_name?: string;
  request_date: string;
  required_date?: string;
  status: string;
  current_step?: string;
  current_approver_id?: number;
  total_amount?: number;
  approval_notes?: string;
  remarks?: string;
  payment_method?: string;
  estimated_delivery_date?: string;
  quote_date?: string;
  system_category?: string;
  created_at: string;
  updated_at?: string;
  items: PurchaseDetailItem[];
}

// 申购明细项（API返回的完整数据，含询价信息）
export interface PurchaseDetailItem {
  id: number;
  request_id: number;
  contract_item_id?: number;
  system_category_id?: number;
  system_category_name?: string;
  item_name: string;
  specification?: string;
  brand_model?: string;
  brand?: string;
  unit: string;
  quantity: number;
  item_type: string;
  unit_price?: number;
  total_price?: number;
  supplier_name?: string;
  supplier_contact?: string;
  supplier_info?: { payment_method?: string; [key: string]: string | undefined };
  payment_method?: string;
  estimated_delivery?: string;
  estimated_delivery_date?: string;
  remaining_quantity?: number;
  received_quantity?: number;
  status?: string;
  remarks?: string;
  availableSystemCategories?: SystemCategoryOption[];
}

// 系统分类选项
export interface SystemCategoryOption {
  id: number;
  category_name: string;
  category_code?: string;
  description?: string;
  is_suggested?: boolean;
  items_count?: number;
}

// 规格选项
export interface SpecificationOption {
  specification: string;
  brand_model: string;
  unit: string;
  remaining_quantity: number;
  contract_item_id: number;
  total_quantity: number;
}

// 申购单编辑表单项
export interface PurchaseEditItem {
  id: string;
  item_type: string;
  item_name: string;
  specification: string;
  brand_model: string;
  unit: string;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  remarks: string;
  contract_item_id?: number;
  system_category_id?: number;
  system_category_name?: string;
  remaining_quantity?: number;
  max_quantity?: number;
  availableSpecifications?: SpecificationOption[];
  availableSystemCategories?: SystemCategoryOption[];
}

// API错误响应
export interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

// 查询参数类型
export interface PurchaseRequestQueryParams {
  page?: number;
  size?: number;
  project_id?: number;
  status?: PurchaseStatus;
  requester_id?: number;
  search?: string;
}
