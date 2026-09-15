import axios from "axios";
import type { Permission, RoleName } from "../auth/roles";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  timeout: 8000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ntp_access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export type AuthResponse = {
  access_token: string;
  token_type: string;
  profile_completed: boolean;
  user: CurrentUser;
};

export type CurrentUser = {
  id: string;
  email: string;
  name: string;

  role: {
    id: string;
    name: RoleName;
  };

  permissions: Permission[];

  profile_completed: boolean;
};

export async function login(email: string, password: string) {
  const { data } = await api.post<AuthResponse>("/auth/login", {
    email,
    password,
  });
  localStorage.setItem("ntp_access_token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("ntp_access_token");
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem("ntp_access_token"));
}

export type VehicleStatus =
  | "AVAILABLE"
  | "BUSY"
  | "AVAILABLE_RETURN"
  | "NOT_READY"
  | "MAINTENANCE";

export type Candidate = {
  vehicle_id: string;
  vehicle_plate: string;
  employee_id: string | null;
  employee_name: string;
  operational_status: VehicleStatus;
  ready_from: string | null;
  current_destination: string | null;
  candidate_type: "available" | "return";
};

export type Dashboard = {
  counts: Record<VehicleStatus, number>;
  today_jobs: number;
  active_jobs: number;
  completed_jobs: number;
};

export type CreateJobPayload = {
  source: "EXTERNAL" | "INTERNAL";
  origin: string;
  destination: string;
  pickup_date: string;
  pickup_time: string;
  customer_reference?: string;
  notes?: string;
  job_type: "ONE_WAY" | "ROUND_TRIP";
};

export async function getDashboard() {
  const { data } = await api.get<Dashboard>("/dashboard/manager");
  return data;
}

export async function getCandidates(params: {
  origin: string;
  employee_name: string;
  vehicle_plate: string;
  status: string;
}) {
  const { data } = await api.get<{ items: Candidate[]; total: number }>(
    "/dispatch/candidates",
    { params },
  );
  return data;
}

export async function createJob(payload: CreateJobPayload) {
  const { data } = await api.post<{
    id: string;
    status: string;
    origin: string;
    destination: string;
  }>("/jobs", payload);
  return data;
}

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

export async function getAuditLogs() {
  const { data } = await api.get<
    Array<{
      id: string;
      actor_user_id: string | null;
      action: string;
      entity: string;
      entity_id: string | null;
      metadata: string | null;
      created_at: string;
    }>
  >("/audit-logs");
  return data;
}

export async function completeProfile(payload: {
  phone: string;
  address: string;
}) {
  const { data } = await api.post<{ profile_completed: boolean }>(
    "/profile/complete",
    payload,
  );
  return data;
}

export type UserProfile = CurrentUser & {
  employee_id: string | null;
  position: string | null;
  phone: string | null;
  address: string | null;
  vehicle: { plate: string; status: VehicleStatus } | null;
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
