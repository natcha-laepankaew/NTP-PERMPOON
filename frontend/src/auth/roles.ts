export const ROLE_NAMES = [
  "ADMINISTRATOR",
  "ADMIN",
  "MANAGER",
  "DRIVER",
] as const;

export type RoleName = (typeof ROLE_NAMES)[number];

export const ROLE_ACCESS = {
  all: ROLE_NAMES,
  operations: ["ADMINISTRATOR", "ADMIN", "MANAGER"],
  administrator: ["ADMINISTRATOR"],
} as const satisfies Record<string, readonly RoleName[]>;

export function hasAllowedRole(
  role: RoleName | undefined,
  allowedRoles: readonly RoleName[],
) {
  return role !== undefined && allowedRoles.includes(role);
}
