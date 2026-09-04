import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  timeout: 8000,
});

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
