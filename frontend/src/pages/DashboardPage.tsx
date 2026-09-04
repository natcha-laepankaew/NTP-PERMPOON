import { useEffect, useState } from "react";
import {
  Activity,
  ChevronRight,
  ClipboardList,
  Search,
  Truck,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getDashboard, type Dashboard } from "../services/api";
import {
  JobRow,
  MetricCard,
  ReadinessBar,
} from "../components/DashboardWidgets";
import { PageHeading } from "../components/PageHeading";

const fallbackDashboard: Dashboard = {
  counts: {
    AVAILABLE: 24,
    BUSY: 15,
    AVAILABLE_RETURN: 6,
    NOT_READY: 8,
    MAINTENANCE: 3,
  },
  today_jobs: 42,
  active_jobs: 15,
  completed_jobs: 27,
};

export function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const navigation = useNavigate();
  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setData(fallbackDashboard));
  }, []);
  const counts = data?.counts;
  return (
    <>
      <PageHeading
        eyebrow="FRIDAY, 04 SEP 2026"
        title="Good morning, Somchai"
        description="Here is today's operational pulse across your fleet."
        action={
          <button
            className="button button-primary"
            onClick={() => navigation("/dispatch")}
          >
            <Search size={17} /> Find a vehicle
          </button>
        }
      />
      <section className="metrics-grid">
        <MetricCard
          label="Available now"
          value={counts?.AVAILABLE ?? "--"}
          detail="พร้อมรับงาน"
          tone="green"
          icon={<Truck size={20} />}
        />
        <MetricCard
          label="In operation"
          value={counts?.BUSY ?? "--"}
          detail="กำลังทำงาน"
          tone="amber"
          icon={<Activity size={20} />}
        />
        <MetricCard
          label="Return-ready"
          value={counts?.AVAILABLE_RETURN ?? "--"}
          detail="พร้อมรับงานขากลับ"
          tone="blue"
          icon={<Truck size={20} />}
        />
        <MetricCard
          label="Today's jobs"
          value={data?.today_jobs ?? "--"}
          detail="งานทั้งหมดวันนี้"
          tone="navy"
          icon={<ClipboardList size={20} />}
        />
      </section>
      <section className="dashboard-grid">
        <div className="panel active-jobs">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">LIVE OPERATIONS</p>
              <h2>Today's active jobs</h2>
            </div>
            <a href="/jobs">
              View all <ChevronRight size={15} />
            </a>
          </div>
          <div className="job-list">
            <JobRow
              id="JOB-20260904-001"
              route="หาดใหญ่ → พัทลุง"
              employee="สมชาย ใจดี"
              vehicle="70-1234"
              status="IN_PROGRESS"
            />
            <JobRow
              id="JOB-20260904-002"
              route="สงขลา → หาดใหญ่"
              employee="วิชัย ขับดี"
              vehicle="70-5678"
              status="ASSIGNED"
            />
            <JobRow
              id="JOB-20260904-003"
              route="หาดใหญ่ → ตรัง"
              employee="ประชา ตั้งใจ"
              vehicle="70-9999"
              status="IN_PROGRESS"
            />
          </div>
        </div>
        <div className="panel readiness">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">FLEET HEALTH</p>
              <h2>Fleet readiness</h2>
            </div>
            <span className="live-badge">
              <i /> LIVE
            </span>
          </div>
          <div className="readiness-bars">
            <ReadinessBar
              label="Available"
              value={counts?.AVAILABLE ?? 0}
              total={56}
              color="green"
            />
            <ReadinessBar
              label="In operation"
              value={counts?.BUSY ?? 0}
              total={56}
              color="amber"
            />
            <ReadinessBar
              label="Return-ready"
              value={counts?.AVAILABLE_RETURN ?? 0}
              total={56}
              color="blue"
            />
            <ReadinessBar
              label="Maintenance"
              value={counts?.MAINTENANCE ?? 0}
              total={56}
              color="slate"
            />
          </div>
          <div className="fleet-total">
            <span>Total fleet</span>
            <strong>56 vehicles</strong>
          </div>
        </div>
      </section>
    </>
  );
}
