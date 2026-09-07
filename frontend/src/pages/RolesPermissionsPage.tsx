import { useEffect, useMemo, useState } from "react";
import { Check, LockKeyhole, ShieldCheck } from "lucide-react";
import { PageHeading } from "../components/PageHeading";
import {
  getPermissions,
  getRoles,
  type PermissionRecord,
  type RoleRecord,
} from "../services/api";

export function RolesPermissionsPage() {
  const [roles, setRoles] = useState<RoleRecord[]>([]);
  const [permissions, setPermissions] = useState<PermissionRecord[]>([]);
  const [selected, setSelected] = useState("SUPER_ADMIN");
  useEffect(() => {
    Promise.all([getRoles(), getPermissions()]).then(
      ([roleData, permissionData]) => {
        setRoles(roleData);
        setPermissions(permissionData);
      },
    );
  }, []);
  const role = roles.find((item) => item.name === selected);
  const grouped = useMemo(
    () =>
      permissions.reduce<Record<string, PermissionRecord[]>>(
        (groups, permission) => {
          const modulePermissions = groups[permission.module] ?? [];
          modulePermissions.push(permission);
          groups[permission.module] = modulePermissions;
          return groups;
        },
        {},
      ),
    [permissions],
  );
  return (
    <>
      <PageHeading
        eyebrow="SYSTEM / ACCESS CONTROL"
        title="Roles & Permissions"
        description="Review the permissions assigned to each system role."
        action={
          <span className="system-role-badge">
            <LockKeyhole size={14} /> SUPER_ADMIN ONLY
          </span>
        }
      />
      <div className="rbac-layout">
        <aside className="role-list panel">
          <div className="table-heading">
            <div>
              <p className="eyebrow">SYSTEM ROLES</p>
              <h2>{roles.length} roles</h2>
            </div>
          </div>
          {roles.map((item) => (
            <button
              key={item.name}
              className={`role-list-item ${item.name === selected ? "active" : ""}`}
              onClick={() => setSelected(item.name)}
            >
              <div className="role-list-icon">
                <ShieldCheck size={17} />
              </div>
              <div>
                <strong>{item.name}</strong>
                <span>{item.description}</span>
              </div>
              <small>{item.permissions.length}</small>
            </button>
          ))}
        </aside>
        <section className="permission-panel panel">
          <div className="table-heading">
            <div>
              <p className="eyebrow">ROLE DETAIL</p>
              <h2>{role?.name ?? selected}</h2>
              <span className="role-description">
                {role?.description ?? "Loading role..."}
              </span>
            </div>
            <span className="system-role-badge">
              <LockKeyhole size={13} /> System role
            </span>
          </div>
          <div className="permission-grid">
            {Object.entries(grouped).map(([module, items]) => (
              <div className="permission-module" key={module}>
                <div className="permission-module-heading">
                  <span>{module.replace("_", " ")}</span>
                  <small>
                    {
                      items.filter((item) =>
                        role?.permissions.includes(item.code),
                      ).length
                    }
                    /{items.length}
                  </small>
                </div>
                {items.map((permission) => {
                  const enabled = role?.permissions.includes(permission.code);
                  return (
                    <div
                      className={`permission-row ${enabled ? "enabled" : ""}`}
                      key={permission.code}
                    >
                      <span className="permission-check">
                        {enabled && <Check size={13} />}
                      </span>
                      <div>
                        <strong>{permission.code}</strong>
                        <small>{permission.description}</small>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
