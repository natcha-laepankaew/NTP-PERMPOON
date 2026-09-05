import { useMemo, useState } from "react";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Download,
  Filter,
  Search,
} from "lucide-react";
import { PageHeading } from "../components/PageHeading";

type HistoryStatus = "COMPLETED" | "IN_PROGRESS" | "CANCELLED";
type JobType = "ONE_WAY" | "ROUND_TRIP";

type HistoryJob = {
  id: string;
  employee: string;
  vehicle: string;
  origin: string;
  destination: string;
  type: JobType;
  status: HistoryStatus;
  date: string;
  duration: string;
};

const jobs: HistoryJob[] = [
  {
    id: "JOB-20260904-001",
    employee: "สมชาย ใจดี",
    vehicle: "70-1234",
    origin: "หาดใหญ่",
    destination: "พัทลุง",
    type: "ONE_WAY",
    status: "COMPLETED",
    date: "04 Sep 2026",
    duration: "02h 14m",
  },
  {
    id: "JOB-20260904-002",
    employee: "วิชัย ขับดี",
    vehicle: "70-5678",
    origin: "สงขลา",
    destination: "หาดใหญ่",
    type: "ROUND_TRIP",
    status: "IN_PROGRESS",
    date: "04 Sep 2026",
    duration: "01h 32m",
  },
  {
    id: "JOB-20260903-018",
    employee: "ประชา ตั้งใจ",
    vehicle: "70-9999",
    origin: "หาดใหญ่",
    destination: "ตรัง",
    type: "ONE_WAY",
    status: "COMPLETED",
    date: "03 Sep 2026",
    duration: "03h 08m",
  },
  {
    id: "JOB-20260903-017",
    employee: "กมล ส่งไว",
    vehicle: "70-1111",
    origin: "พัทลุง",
    destination: "สงขลา",
    type: "ROUND_TRIP",
    status: "CANCELLED",
    date: "03 Sep 2026",
    duration: "--",
  },
  {
    id: "JOB-20260902-014",
    employee: "สมชาย ใจดี",
    vehicle: "70-1234",
    origin: "ตรัง",
    destination: "หาดใหญ่",
    type: "ROUND_TRIP",
    status: "COMPLETED",
    date: "02 Sep 2026",
    duration: "04h 22m",
  },
  {
    id: "JOB-20260901-009",
    employee: "วิชัย ขับดี",
    vehicle: "70-5678",
    origin: "หาดใหญ่",
    destination: "สงขลา",
    type: "ONE_WAY",
    status: "COMPLETED",
    date: "01 Sep 2026",
    duration: "01h 46m",
  },
];

const statusClass: Record<HistoryStatus, string> = {
  COMPLETED: "green",
  IN_PROGRESS: "amber",
  CANCELLED: "red",
};

export function HistoryPage() {
  const [query, setQuery] = useState("");
  const [employee, setEmployee] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [status, setStatus] = useState<HistoryStatus | "">("");
  const [type, setType] = useState<JobType | "">("");
  const [page, setPage] = useState(1);

  const filteredJobs = useMemo(
    () =>
      jobs.filter((job) => {
        const text = `${job.id} ${job.origin} ${job.destination}`.toLowerCase();
        return (
          (!query || text.includes(query.toLowerCase())) &&
          (!employee || job.employee === employee) &&
          (!vehicle || job.vehicle === vehicle) &&
          (!status || job.status === status) &&
          (!type || job.type === type)
        );
      }),
    [employee, query, status, type, vehicle],
  );

  function resetFilters() {
    setQuery("");
    setEmployee("");
    setVehicle("");
    setStatus("");
    setType("");
    setPage(1);
  }

  return (
    <>
      <PageHeading
        eyebrow="OPERATIONS / HISTORY"
        title="Job History"
        description="Review completed and active delivery jobs across your operation."
        action={
          <button className="button button-outline">
            <Download size={16} /> Export report
          </button>
        }
      />
      <section className="history-summary">
        <div>
          <span>Total jobs</span>
          <strong>1,284</strong>
          <small>All recorded jobs</small>
        </div>
        <div>
          <span>Completed</span>
          <strong className="summary-green">1,201</strong>
          <small>93.5% completion rate</small>
        </div>
        <div>
          <span>In progress</span>
          <strong className="summary-amber">15</strong>
          <small>Active right now</small>
        </div>
        <div>
          <span>Showing</span>
          <strong>{filteredJobs.length}</strong>
          <small>Mock records</small>
        </div>
      </section>
      <section className="history-panel panel">
        <div className="history-filter-heading">
          <div>
            <div className="search-title compact">
              <div className="search-icon">
                <Filter size={18} />
              </div>
              <div>
                <h2>Filter job history</h2>
                <p>Search by job, route or filter by operational details.</p>
              </div>
            </div>
          </div>
          <button className="text-button" onClick={resetFilters}>
            Clear all
          </button>
        </div>
        <div className="history-filters">
          <label className="history-search">
            <span>Search</span>
            <div className="input-with-icon">
              <Search size={15} />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPage(1);
                }}
                placeholder="Job ID, origin or destination"
              />
            </div>
          </label>
          <label>
            <span>Employee</span>
            <select
              value={employee}
              onChange={(event) => setEmployee(event.target.value)}
            >
              <option value="">All employees</option>
              {Array.from(new Set(jobs.map((job) => job.employee))).map(
                (name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ),
              )}
            </select>
          </label>
          <label>
            <span>Vehicle</span>
            <select
              value={vehicle}
              onChange={(event) => setVehicle(event.target.value)}
            >
              <option value="">All vehicles</option>
              {Array.from(new Set(jobs.map((job) => job.vehicle))).map(
                (plate) => (
                  <option key={plate} value={plate}>
                    {plate}
                  </option>
                ),
              )}
            </select>
          </label>
          <label>
            <span>Status</span>
            <select
              value={status}
              onChange={(event) =>
                setStatus(event.target.value as HistoryStatus | "")
              }
            >
              <option value="">All statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="IN_PROGRESS">In progress</option>
              <option value="CANCELLED">Cancelled</option>
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
          <div className="history-filter-field">
            <span>Date range</span>
            <button className="date-filter">
              <CalendarDays size={15} /> This month
            </button>
          </div>
        </div>
      </section>
      <section className="history-table-panel panel">
        <div className="table-heading">
          <div>
            <p className="eyebrow">JOB RECORDS</p>
            <h2>{filteredJobs.length} recent jobs</h2>
          </div>
          <span className="result-note">
            Mock data · API integration pending
          </span>
        </div>
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Employee / Vehicle</th>
                <th>Route</th>
                <th>Type</th>
                <th>Status</th>
                <th>Date</th>
                <th>Duration</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {filteredJobs.map((job) => (
                <tr key={job.id}>
                  <td>
                    <strong className="job-link">{job.id}</strong>
                  </td>
                  <td>
                    <strong>{job.employee}</strong>
                    <span>{job.vehicle}</span>
                  </td>
                  <td>
                    <strong>
                      {job.origin} <span className="route-arrow">→</span>{" "}
                      {job.destination}
                    </strong>
                  </td>
                  <td>
                    <span className="type-label">{job.type}</span>
                  </td>
                  <td>
                    <span className={`status-pill ${statusClass[job.status]}`}>
                      <i />
                      {job.status}
                    </span>
                  </td>
                  <td>
                    <span className="date-label">{job.date}</span>
                  </td>
                  <td>
                    <span className="duration-label">{job.duration}</span>
                  </td>
                  <td>
                    <button
                      className="icon-button"
                      aria-label={`View ${job.id}`}
                    >
                      <ChevronRight size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredJobs.length === 0 && (
            <div className="empty-state history-empty">
              <Search size={26} />
              <strong>No matching jobs</strong>
              <span>Try clearing one or more filters.</span>
            </div>
          )}
        </div>
        <div className="table-footer">
          <span>
            Showing {filteredJobs.length ? 1 : 0}–{filteredJobs.length} of 1,284
            results
          </span>
          <div className="pagination">
            <button
              className="icon-button"
              disabled={page === 1}
              onClick={() => setPage(Math.max(1, page - 1))}
            >
              <ChevronLeft size={16} />
            </button>
            <button className="page-number active">{page}</button>
            <button className="page-number" onClick={() => setPage(page + 1)}>
              {page + 1}
            </button>
            <button className="icon-button" onClick={() => setPage(page + 1)}>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </section>
    </>
  );
}
