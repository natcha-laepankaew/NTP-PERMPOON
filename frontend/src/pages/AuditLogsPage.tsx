import { useEffect, useState } from "react";
import { Activity, Clock3, ShieldCheck } from "lucide-react";
import { PageHeading } from "../components/PageHeading";
import { getAuditLogs } from "../services/api";

export function AuditLogsPage() {
  const [logs, setLogs] = useState<Awaited<ReturnType<typeof getAuditLogs>>>(
    [],
  );
  useEffect(() => {
    getAuditLogs().then(setLogs);
  }, []);
  return (
    <>
      <PageHeading
        eyebrow="SYSTEM / SECURITY"
        title="Audit Logs"
        description="Track authentication and administrative changes across the system."
        action={
          <span className="system-role-badge">
            <ShieldCheck size={14} /> SUPER_ADMIN ONLY
          </span>
        }
      />
      <section className="audit-panel panel">
        <div className="table-heading">
          <div>
            <p className="eyebrow">SECURITY EVENTS</p>
            <h2>{logs.length} recent events</h2>
          </div>
          <span className="result-note">
            <Activity size={13} /> Live from API
          </span>
        </div>
        <div className="audit-list">
          {logs.map((log) => (
            <div className="audit-row" key={log.id}>
              <div className="audit-icon">
                <Clock3 size={16} />
              </div>
              <div>
                <strong>{log.action}</strong>
                <span>
                  {log.entity}
                  {log.entity_id ? ` · ${log.entity_id}` : ""}
                </span>
              </div>
              <div className="audit-actor">
                {log.actor_user_id ?? "system"}
                <small>{new Date(log.created_at).toLocaleString()}</small>
              </div>
            </div>
          ))}
          {logs.length === 0 && (
            <div className="empty-state">
              <Activity size={28} />
              <strong>No audit events</strong>
              <span>Events will appear after an authorized action.</span>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
