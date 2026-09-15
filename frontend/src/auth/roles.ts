export const ROLE_NAMES = [
  "ADMINISTRATOR",
  "ADMIN",
  "MANAGER",
  "DRIVER",
] as const;

export type RoleName = (typeof ROLE_NAMES)[number];

/**
 * Role-level access
 *
 * ใช้สำหรับกำหนดว่า Role ไหนสามารถเข้า Page นั้นได้
 */
export const ROLE_ACCESS = {
  all: ROLE_NAMES,

  operations: ["ADMINISTRATOR", "ADMIN", "MANAGER"],

  administrator: ["ADMINISTRATOR"],

  driver: ["DRIVER"],
} as const satisfies Record<string, readonly RoleName[]>;

/**
 * Fine-grained permissions
 *
 * ใช้ควบคุม Section / Button / Action ภายใน Page
 */
export const PERMISSIONS = {
  // Dashboard
  DASHBOARD_VIEW: "dashboard.view",

  // Jobs
  JOBS_VIEW: "jobs.view",
  JOBS_VIEW_OWN: "jobs.view_own",
  JOBS_CREATE: "jobs.create",
  JOBS_UPDATE: "jobs.update",
  JOBS_ASSIGN: "jobs.assign",
  JOBS_DELETE: "jobs.delete",

  // Dispatch
  DISPATCH_VIEW: "dispatch.view",
  DISPATCH_ASSIGN: "dispatch.assign",

  // History
  HISTORY_VIEW: "history.view",

  // Employees
  EMPLOYEES_VIEW: "employees.view",
  EMPLOYEES_CREATE: "employees.create",
  EMPLOYEES_UPDATE: "employees.update",
  EMPLOYEES_DELETE: "employees.delete",

  // Vehicles
  VEHICLES_VIEW: "vehicles.view",
  VEHICLES_CREATE: "vehicles.create",
  VEHICLES_UPDATE: "vehicles.update",
  VEHICLES_DELETE: "vehicles.delete",

  // Profile
  PROFILE_VIEW: "profile.view",
  PROFILE_UPDATE: "profile.update",

  // Driver Job actions
  JOB_READY: "job.ready",
  JOB_START: "job.start",
  JOB_DESTINATION_UPDATE: "job.destination_update",
  JOB_COMPLETE: "job.complete",
  JOB_UPLOAD_DOCUMENT: "job.upload_document",

  // System
  ROLES_PERMISSIONS_VIEW: "roles_permissions.view",
  AUDIT_LOGS_VIEW: "audit_logs.view",
} as const;

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

/**
 * Check Role
 */
export function hasAllowedRole(
  role: RoleName | undefined,
  allowedRoles: readonly RoleName[],
): boolean {
  return role !== undefined && allowedRoles.includes(role);
}

/**
 * Check Permission
 */
export function hasPermission(
  permissions: readonly string[] | undefined,
  permission: Permission,
): boolean {
  return permissions?.includes(permission) ?? false;
}
