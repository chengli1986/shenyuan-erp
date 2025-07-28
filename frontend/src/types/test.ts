/**
 * 测试相关类型定义
 */

export interface TestResult {
  id: number;
  test_run_id: string;
  test_type: 'unit' | 'integration';
  test_suite: string;
  test_name: string;
  status: 'passed' | 'failed' | 'skipped' | 'error';
  duration?: number;
  error_message?: string;
  stack_trace?: string;
  created_at: string;
}

export interface TestRun {
  id: number;
  run_id: string;
  run_type: 'scheduled' | 'manual';
  start_time: string;
  end_time?: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  skipped_tests: number;
  error_tests: number;
  duration?: number;
  status: 'running' | 'completed' | 'failed';
  trigger_user?: string;
  environment?: Record<string, any>;
  created_at: string;
  success_rate: number;
}

export interface TestRunListResponse {
  items: TestRun[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TestRunDetailResponse {
  run: TestRun;
  results: Record<string, TestResult[]>;
}

export interface TestStatistics {
  summary: {
    total_runs: number;
    total_tests: number;
    total_passed: number;
    total_failed: number;
    success_rate: number;
  };
  daily_stats: Array<{
    date: string;
    runs: number;
    tests: number;
    passed: number;
    failed: number;
  }>;
}

export interface LatestTestStatus {
  has_run: boolean;
  message?: string;
  latest_run?: TestRun;
  failed_tests?: TestResult[];
}