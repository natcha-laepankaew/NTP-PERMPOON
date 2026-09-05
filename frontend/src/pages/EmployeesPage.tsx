import { useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  CarFront,
  ChevronRight,
  Filter,
  Phone,
  Plus,
  Search,
  UserRound,
  X,
} from "lucide-react";
import { PageHeading } from "../components/PageHeading";

type EmployeeStatus = "READY" | "BUSY" | "AVAILABLE_RETURN" | "NOT_READY";
type Employee = {
  id: string;
  name: string;
  position: string;
  phone: string;
  vehicle: string;
  status: EmployeeStatus;
  readyFrom: string;
  currentJob: string;
};

const employees: Employee[] = [
  {
    id: "E001",
    name: "สมชาย ใจดี",
    position: "DRIVER",
    phone: "081-000-1001",
    vehicle: "70-1234",
    status: "READY",
    readyFrom: "หาดใหญ่",
    currentJob: "Available",
  },
  {
    id: "E002",
    name: "วิชัย ขับดี",
    position: "DRIVER",
    phone: "081-000-1002",
    vehicle: "70-5678",
    status: "BUSY",
    readyFrom: "สงขลา",
    currentJob: "JOB-20260904-002",
  },
  {
    id: "E003",
    name: "ประชา ตั้งใจ",
    position: "DRIVER",
    phone: "081-000-1003",
    vehicle: "70-9999",
    status: "AVAILABLE_RETURN",
    readyFrom: "-",
    currentJob: "Returned from ตรัง",
  },
  {
    id: "E004",
    name: "กมล ส่งไว",
    position: "DRIVER",
    phone: "081-000-1004",
    vehicle: "70-1111",
    status: "NOT_READY",
    readyFrom: "-",
    currentJob: "Off duty",
  },
  {
    id: "E005",
    name: "นภา รอบคอบ",
    position: "COORDINATOR",
    phone: "081-000-1005",
    vehicle: "-",
    status: "READY",
    readyFrom: "สำนักงาน",
    currentJob: "Available",
  },
  {
    id: "E006",
    name: "ธนา เส้นทางดี",
    position: "DRIVER",
    phone: "081-000-1006",
    vehicle: "70-2222",
    status: "READY",
    readyFrom: "พัทลุง",
    currentJob: "Available",
  },
];

const statusMeta: Record<
  EmployeeStatus,
  { label: string; color: string; detail: string }
> = {
  READY: { label: "READY", color: "green", detail: "พร้อมรับงาน" },
  BUSY: { label: "BUSY", color: "amber", detail: "กำลังทำงาน" },
  AVAILABLE_RETURN: {
    label: "AVAILABLE_RETURN",
    color: "blue",
    detail: "พร้อมรับงานขากลับ",
  },
  NOT_READY: { label: "NOT_READY", color: "red", detail: "ไม่พร้อมรับงาน" },
};

export function EmployeesPage() {
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState("");
  const [status, setStatus] = useState<EmployeeStatus | "">("");
  const [selected, setSelected] = useState<Employee | null>(null);
  const filteredEmployees = useMemo(
    () =>
      employees.filter((employee) => {
        const searchable =
          `${employee.id} ${employee.name} ${employee.phone} ${employee.vehicle}`.toLowerCase();
        return (
          (!query || searchable.includes(query.toLowerCase())) &&
          (!position || employee.position === position) &&
          (!status || employee.status === status)
        );
      }),
    [position, query, status],
  );

  return (
    <>
      <PageHeading
        eyebrow="RESOURCES / PEOPLE"
        title="Employees"
        description="Manage employee profiles and monitor operational availability."
        action={
          <button className="button button-primary">
            <Plus size={17} /> Add employee
          </button>
        }
      />
      <section className="employee-summary">
        <SummaryItem label="Total employees" value={employees.length} />
        <SummaryItem
          label="Ready now"
          value={
            employees.filter((employee) => employee.status === "READY").length
          }
          color="green"
        />
        <SummaryItem
          label="Working"
          value={
            employees.filter((employee) => employee.status === "BUSY").length
          }
          color="amber"
        />
        <SummaryItem
          label="Return-ready"
          value={
            employees.filter(
              (employee) => employee.status === "AVAILABLE_RETURN",
            ).length
          }
          color="blue"
        />
      </section>
      <section className="employee-toolbar panel">
        <div className="employee-search input-with-icon">
          <Search size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search name, Employee ID, phone or vehicle"
          />
        </div>
        <label>
          <span>Position</span>
          <select
            value={position}
            onChange={(event) => setPosition(event.target.value)}
          >
            <option value="">All positions</option>
            <option value="DRIVER">DRIVER</option>
            <option value="COORDINATOR">COORDINATOR</option>
          </select>
        </label>
        <label>
          <span>Status</span>
          <select
            value={status}
            onChange={(event) =>
              setStatus(event.target.value as EmployeeStatus | "")
            }
          >
            <option value="">All statuses</option>
            {Object.entries(statusMeta).map(([key, meta]) => (
              <option key={key} value={key}>
                {meta.label}
              </option>
            ))}
          </select>
        </label>
        <button className="button button-outline">
          <Filter size={15} /> More filters
        </button>
      </section>
      <section className="employee-table-panel panel">
        <div className="table-heading">
          <div>
            <p className="eyebrow">EMPLOYEE DIRECTORY</p>
            <h2>{filteredEmployees.length} employees</h2>
          </div>
          <span className="result-note">
            Mock data · API integration pending
          </span>
        </div>
        <div className="employee-table-wrap">
          <table className="employee-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Position</th>
                <th>Vehicle</th>
                <th>Status</th>
                <th>Ready from</th>
                <th>Current job</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.map((employee) => (
                <tr key={employee.id}>
                  <td>
                    <div className="employee-cell">
                      <div className="employee-avatar">
                        {employee.name.slice(0, 1)}
                      </div>
                      <div>
                        <strong>{employee.name}</strong>
                        <span>
                          {employee.id} · {employee.phone}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="position-label">
                      <BriefcaseBusiness size={13} />
                      {employee.position}
                    </span>
                  </td>
                  <td>
                    <span className="vehicle-label">
                      <CarFront size={14} />
                      {employee.vehicle}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`status-pill ${statusMeta[employee.status].color}`}
                    >
                      <i />
                      {statusMeta[employee.status].label}
                    </span>
                    <small className="status-detail">
                      {statusMeta[employee.status].detail}
                    </small>
                  </td>
                  <td>{employee.readyFrom}</td>
                  <td>
                    <span className="current-job">{employee.currentJob}</span>
                  </td>
                  <td>
                    <button
                      className="button button-outline view-button"
                      onClick={() => setSelected(employee)}
                    >
                      View <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredEmployees.length === 0 && (
            <div className="empty-state employee-empty">
              <UserRound size={27} />
              <strong>No employees found</strong>
              <span>Try clearing the current filters.</span>
            </div>
          )}
        </div>
      </section>
      {selected && (
        <EmployeeDrawer employee={selected} onClose={() => setSelected(null)} />
      )}
    </>
  );
}

function SummaryItem({
  label,
  value,
  color = "navy",
}: Readonly<{ label: string; value: number; color?: string }>) {
  return (
    <div>
      <span className={`summary-dot ${color}`} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function EmployeeDrawer({
  employee,
  onClose,
}: Readonly<{ employee: Employee; onClose: () => void }>) {
  const meta = statusMeta[employee.status];
  return (
    <div className="drawer-backdrop">
      <aside className="employee-drawer">
        <div className="drawer-heading">
          <div>
            <p className="eyebrow">EMPLOYEE PROFILE</p>
            <h2>Employee details</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close employee profile"
          >
            <X size={19} />
          </button>
        </div>
        <div className="drawer-profile">
          <div className="drawer-avatar">{employee.name.slice(0, 1)}</div>
          <h3>{employee.name}</h3>
          <p>
            {employee.id} · {employee.position}
          </p>
          <span className={`status-pill ${meta.color}`}>
            <i />
            {meta.label}
          </span>
        </div>
        <dl className="employee-details">
          <div>
            <dt>Phone</dt>
            <dd>
              <Phone size={14} />
              {employee.phone}
            </dd>
          </div>
          <div>
            <dt>Assigned vehicle</dt>
            <dd>
              <CarFront size={14} />
              {employee.vehicle}
            </dd>
          </div>
          <div>
            <dt>Ready from</dt>
            <dd>{employee.readyFrom}</dd>
          </div>
          <div>
            <dt>Current job</dt>
            <dd>{employee.currentJob}</dd>
          </div>
        </dl>
        <button
          className="button button-primary drawer-action"
          onClick={onClose}
        >
          View full profile <ChevronRight size={15} />
        </button>
      </aside>
    </div>
  );
}
