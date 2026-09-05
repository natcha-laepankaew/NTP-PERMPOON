import { useMemo, useState } from "react";
import {
  Activity,
  ChevronRight,
  ClipboardList,
  Filter,
  MapPin,
  Plus,
  Search,
  Truck,
  UserRound,
} from "lucide-react";
import { PageHeading } from "../components/PageHeading";

type JobStatus =
  | "CREATED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "CANCELLED";
type JobType = "ONE_WAY" | "ROUND_TRIP";

type Job = {
  id: string;
  origin: string;
  destination: string;
  employee: string;
  vehicle: string;
  type: JobType;
  status: JobStatus;
  pickup: string;
};

const mockJobs: Job[] = [
  {
    id: "JOB-20260904-001",
    origin: "หาดใหญ่",
    destination: "พัทลุง",
    employee: "สมชาย ใจดี",
    vehicle: "70-1234",
    type: "ONE_WAY",
    status: "IN_PROGRESS",
    pickup: "10:30",
  },
  {
    id: "JOB-20260904-002",
    origin: "สงขลา",
    destination: "หาดใหญ่",
    employee: "วิชัย ขับดี",
    vehicle: "70-5678",
    type: "ROUND_TRIP",
    status: "ASSIGNED",
    pickup: "11:00",
  },
  {
    id: "JOB-20260904-003",
    origin: "หาดใหญ่",
    destination: "ตรัง",
    employee: "ประชา ตั้งใจ",
    vehicle: "70-9999",
    type: "ONE_WAY",
    status: "CREATED",
    pickup: "13:00",
  },
  {
    id: "JOB-20260904-004",
    origin: "พัทลุง",
    destination: "สงขลา",
    employee: "ยังไม่มอบหมาย",
    vehicle: "รอ Assign",
    type: "ONE_WAY",
    status: "CREATED",
    pickup: "14:30",
  },
  {
    id: "JOB-20260903-018",
    origin: "ตรัง",
    destination: "หาดใหญ่",
    employee: "สมชาย ใจดี",
    vehicle: "70-1234",
    type: "ROUND_TRIP",
    status: "COMPLETED",
    pickup: "09:15",
  },
  {
    id: "JOB-20260903-017",
    origin: "พัทลุง",
    destination: "สงขลา",
    employee: "กมล ส่งไว",
    vehicle: "70-1111",
    type: "ONE_WAY",
    status: "CANCELLED",
    pickup: "08:45",
  },
];

const statusMeta: Record<JobStatus, { label: string; color: string }> = {
  CREATED: { label: "CREATED", color: "slate" },
  ASSIGNED: { label: "ASSIGNED", color: "blue" },
  IN_PROGRESS: { label: "IN_PROGRESS", color: "amber" },
  COMPLETED: { label: "COMPLETED", color: "green" },
  CANCELLED: { label: "CANCELLED", color: "red" },
};

export function JobsPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<JobStatus | "">("");
  const [type, setType] = useState<JobType | "">("");
  const [showFilters, setShowFilters] = useState(false);

  const filteredJobs = useMemo(
    () =>
      mockJobs.filter((job) => {
        const searchable =
          `${job.id} ${job.origin} ${job.destination} ${job.employee} ${job.vehicle}`.toLowerCase();
        return (
          (!query || searchable.includes(query.toLowerCase())) &&
          (!status || job.status === status) &&
          (!type || job.type === type)
        );
      }),
    [query, status, type],
  );

  return (
    <>
      <PageHeading
        eyebrow="OPERATIONS / JOBS"
        title="Jobs"
        description="Create, review and track delivery jobs across today's operation."
        action={
          <button className="button button-primary">
            <Plus size={17} /> Create job
          </button>
        }
      />
      <section className="job-status-strip">
        <StatusSummary
          label="All jobs"
          value={mockJobs.length}
          active={!status}
          onClick={() => setStatus("")}
        />
        <StatusSummary
          label="Created"
          value={mockJobs.filter((job) => job.status === "CREATED").length}
          color="slate"
          active={status === "CREATED"}
          onClick={() => setStatus("CREATED")}
        />
        <StatusSummary
          label="Assigned"
          value={mockJobs.filter((job) => job.status === "ASSIGNED").length}
          color="blue"
          active={status === "ASSIGNED"}
          onClick={() => setStatus("ASSIGNED")}
        />
        <StatusSummary
          label="In progress"
          value={mockJobs.filter((job) => job.status === "IN_PROGRESS").length}
          color="amber"
          active={status === "IN_PROGRESS"}
          onClick={() => setStatus("IN_PROGRESS")}
        />
        <StatusSummary
          label="Completed"
          value={mockJobs.filter((job) => job.status === "COMPLETED").length}
          color="green"
          active={status === "COMPLETED"}
          onClick={() => setStatus("COMPLETED")}
        />
      </section>
      <section className="jobs-toolbar panel">
        <div className="jobs-search input-with-icon">
          <Search size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Job ID, route, employee or vehicle"
          />
        </div>
        <button
          className={`button button-outline ${showFilters ? "filter-active" : ""}`}
          onClick={() => setShowFilters((visible) => !visible)}
        >
          <Filter size={16} /> Filters
        </button>
        <span className="result-note">
          <Activity size={13} /> {filteredJobs.length} records
        </span>
      </section>
      {showFilters && (
        <section className="jobs-filter-panel panel">
          <label>
            <span>Status</span>
            <select
              value={status}
              onChange={(event) =>
                setStatus(event.target.value as JobStatus | "")
              }
            >
              <option value="">All statuses</option>
              {Object.entries(statusMeta).map(([value, meta]) => (
                <option key={value} value={value}>
                  {meta.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Job type</span>
            <select
              value={type}
              onChange={(event) => setType(event.target.value as JobType | "")}
            >
              <option value="">All types</option>
              <option value="ONE_WAY">ONE_WAY</option>
              <option value="ROUND_TRIP">ROUND_TRIP</option>
            </select>
          </label>
          <button
            className="text-button"
            onClick={() => {
              setStatus("");
              setType("");
              setQuery("");
            }}
          >
            Clear filters
          </button>
        </section>
      )}
      <section className="jobs-list">
        {filteredJobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
        {filteredJobs.length === 0 && (
          <div className="empty-state">
            <ClipboardList size={28} />
            <strong>No jobs found</strong>
            <span>Try clearing the current filters.</span>
          </div>
        )}
      </section>
    </>
  );
}

function StatusSummary({
  label,
  value,
  color,
  active,
  onClick,
}: Readonly<{
  label: string;
  value: number;
  color?: string;
  active: boolean;
  onClick: () => void;
}>) {
  return (
    <button
      className={`job-summary ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <span className={`summary-dot ${color ?? "navy"}`} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </button>
  );
}

function JobCard({ job }: Readonly<{ job: Job }>) {
  const meta = statusMeta[job.status];
  return (
    <article className="job-card panel">
      <div className="job-card-main">
        <div className="job-card-id">
          <span>{job.id}</span>
          <span className={`status-pill ${meta.color}`}>
            <i />
            {meta.label}
          </span>
        </div>
        <div className="job-route">
          <div>
            <MapPin size={15} />
            <span>
              Origin<strong>{job.origin}</strong>
            </span>
          </div>
          <ChevronRight size={17} className="route-chevron" />
          <div>
            <MapPin size={15} />
            <span>
              Destination<strong>{job.destination}</strong>
            </span>
          </div>
        </div>
      </div>
      <div className="job-card-assignment">
        <div>
          <UserRound size={14} />
          <span>
            Employee<strong>{job.employee}</strong>
          </span>
        </div>
        <div>
          <Truck size={14} />
          <span>
            Vehicle<strong>{job.vehicle}</strong>
          </span>
        </div>
      </div>
      <div className="job-card-meta">
        <span>{job.type}</span>
        <span>Pickup today, {job.pickup}</span>
        <button className="icon-button" aria-label={`View ${job.id}`}>
          <ChevronRight size={17} />
        </button>
      </div>
    </article>
  );
}
