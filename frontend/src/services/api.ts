import axios from "axios";
import type { RoleName } from "../auth/roles";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  timeout: 8000,
  headers: {
    "Content-Type": "application/json",
  },
});

// =========================================================
// Axios Request Interceptor
// =========================================================

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ntp_access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// =========================================================
// Auth
// =========================================================

export type CurrentUser = {
  // users.id
  id: string;

  email: string;
  name: string;

  role: {
    id: string;
    name: RoleName;
  };

  // Backend ส่งกลับเป็น string[]
  permissions: string[];

  profile_completed: boolean;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  profile_completed: boolean;
  user: CurrentUser;
};

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", {
    email: email.trim().toLowerCase(),
    password,
  });

  // เก็บ JWT
  localStorage.setItem("ntp_access_token", data.access_token);

  return data;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const { data } = await api.get<CurrentUser>("/users/me");

  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } finally {
    localStorage.removeItem("ntp_access_token");
  }
}

export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem("ntp_access_token"));
}

// =========================================================
// Vehicle
// =========================================================

export type VehicleStatus =
  | "AVAILABLE"
  | "BUSY"
  | "AVAILABLE_RETURN"
  | "NOT_READY"
  | "MAINTENANCE";

// =========================================================
// Dispatch Candidate
// =========================================================

export type Candidate = {
  vehicle_id: string;
  vehicle_plate: string;

  // Driver DB ID
  driver_id: string | null;

  // User account ID
  user_id?: string | null;

  driver_name: string;

  operational_status: VehicleStatus;

  ready_from: string | null;
  current_destination: string | null;

  candidate_type: "available" | "return";
};

export async function getCandidates(params: {
  origin: string;
  driver_name?: string;
  vehicle_plate?: string;
  status?: string;
}) {
  const { data } = await api.get<{
    items: Candidate[];
    total: number;
  }>("/dispatch/candidates", {
    params,
  });

  return data;
}

// =========================================================
// Dashboard
// =========================================================

export type Dashboard = {
  role?: RoleName;

  counts?: Record<VehicleStatus, number>;

  today_jobs?: number;
  active_jobs?: number;
  completed_jobs?: number;

  created_jobs?: number;
  vehicle_counts?: Record<VehicleStatus, number>;

  my_jobs?: unknown[];
  vehicle?: VehicleStatus | null;
};

export async function getDashboard() {
  const { data } = await api.get<Dashboard>("/dashboard");

  return data;
}

// =========================================================
// Jobs
// =========================================================

export type JobSource = "EXTERNAL" | "INTERNAL";

export type JobType = "ONE_WAY" | "ROUND_TRIP";

export type JobStatus =
  | "CREATED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "CANCELLED";

export type CreateJobPayload = {
  source: JobSource;
  origin: string;
  destination: string;
  pickup_date: string;
  pickup_time: string;
  customer_reference?: string;
  notes?: string;
  job_type: JobType;
};

export type JobRecord = {
  id: string;
  source: JobSource;
  origin: string;
  destination: string;
  pickup_date: string;
  pickup_time: string;
  job_type: JobType;
  status: JobStatus;

  // Driver DB ID
  driver_id: string | null;

  vehicle_id: string | null;
};

export async function getJobs() {
  const { data } = await api.get<JobRecord[]>("/jobs");

  return data;
}

export async function createJob(payload: CreateJobPayload) {
  const { data } = await api.post<JobRecord>("/jobs", payload);

  return data;
}

// =========================================================
// Roles / Permissions
// =========================================================

export type RoleRecord = {
  id: string;
  name: string;
  description: string;
  is_system_role: boolean;
  users_count: number;
  permissions: string[];
};

export type PermissionRecord = {
  code: string;
  module: string;
  action: string;
  scope: string | null;
  description: string;
};

export async function getRoles() {
  const { data } = await api.get<RoleRecord[]>("/roles");

  return data;
}

export async function getPermissions() {
  const { data } = await api.get<PermissionRecord[]>("/permissions");

  return data;
}

// =========================================================
// Audit Logs
// =========================================================

export type AuditLogRecord = {
  id: string;
  actor_user_id: string | null;
  action: string;
  entity: string;
  entity_id: string | null;
  metadata?: string | null;
  created_at: string;
};

export async function getAuditLogs() {
  const { data } = await api.get<AuditLogRecord[]>("/audit-logs");

  return data;
}

// =========================================================
// Profile
// =========================================================

export type CompleteProfilePayload = {
  phone: string;
  address: string;
  driver_id: string;
  vehicle_plate: string;
};

export async function completeProfile(payload: CompleteProfilePayload) {
  const { data } = await api.post<{
    profile_completed: boolean;
  }>("/profile/complete", payload);

  return data;
}

export type UserProfile = CurrentUser & {
  // drivers.id
  driver_id: string | null;

  position: string | null;

  phone: string | null;

  address: string | null;

  vehicle: {
    id: string;
    plate: string;
    status: VehicleStatus;
  } | null;

  last_login_at: string | null;
};

export async function getMyProfile() {
  const { data } = await api.get<UserProfile>("/profile/me");

  return data;
}

export async function updateMyProfile(payload: {
  phone: string;
  address: string;
}) {
  const { data } = await api.patch<UserProfile>("/profile/me", payload);

  return data;
}
