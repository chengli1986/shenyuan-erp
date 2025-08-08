/**
 * 采购请购相关的TypeScript类型定义
 */

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

// 供应商相关类型
export interface Supplier {
  id: number;
  supplier_name: string;
  supplier_code?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  business_license?: string;
  tax_number?: string;
  bank_account?: string;
  rating?: number;
  remarks?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SupplierCreate {
  supplier_name: string;
  supplier_code?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  business_license?: string;
  tax_number?: string;
  bank_account?: string;
  rating?: number;
  remarks?: string;
}

export interface SupplierUpdate {
  supplier_name?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  rating?: number;
  is_active?: boolean;
  remarks?: string;
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
  supplier_info?: Record<string, any>;
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

// 辅材模板相关类型
export interface AuxiliaryTemplateItem {
  item_name: string;
  specification?: string;
  unit?: string;
  ratio?: number;
  is_required: boolean;
  reference_price?: number;
  remarks?: string;
  sort_order: number;
}

export interface AuxiliaryTemplate {
  id: number;
  template_name: string;
  project_type?: string;
  description?: string;
  usage_count: number;
  created_at: string;
  updated_at?: string;
  items: AuxiliaryTemplateItem[];
}

export interface AuxiliaryTemplateCreate {
  template_name: string;
  project_type?: string;
  description?: string;
  items: AuxiliaryTemplateItem[];
}

// 辅材智能推荐类型
export interface AuxiliaryRecommendation {
  item_name: string;
  specification?: string;
  unit?: string;
  brand?: string;
  ratio?: number;
  is_required?: boolean;
  reference_price?: number;
  source: string;
  confidence: number;
  count?: number;
  avg_quantity?: number;
}

// 入库批次相关类型
export interface InboundBatch {
  id: number;
  batch_number: string;
  purchase_request_item_id: number;
  inbound_quantity: number;
  unit_price?: number;
  quality_status: string;
  quality_check_notes?: string;
  storage_location?: string;
  supplier_batch_info?: Record<string, any>;
  inbound_date: string;
  operator_id?: number;
  remarks?: string;
  created_at: string;
}

export interface InboundBatchCreate {
  purchase_request_item_id: number;
  inbound_quantity: number;
  unit_price?: number;
  quality_status?: string;
  quality_check_notes?: string;
  storage_location?: string;
  supplier_batch_info?: Record<string, any>;
  remarks?: string;
}

// 列表响应类型
export interface PurchaseRequestListResponse {
  items: PurchaseRequestWithItems[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SupplierListResponse {
  items: Supplier[];
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

// 查询参数类型
export interface PurchaseRequestQueryParams {
  page?: number;
  size?: number;
  project_id?: number;
  status?: PurchaseStatus;
  requester_id?: number;
  search?: string;
}

export interface SupplierQueryParams {
  page?: number;
  size?: number;
  search?: string;
  is_active?: boolean;
}