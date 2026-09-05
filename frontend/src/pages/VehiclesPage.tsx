import { useMemo, useState } from "react";
import {
  CarFront,
  ChevronRight,
  Filter,
  MapPin,
  Plus,
  Search,
  UserRound,
  Wrench,
  X,
} from "lucide-react";
import { PageHeading } from "../components/PageHeading";

type VehicleStatus =
  | "AVAILABLE"
  | "BUSY"
  | "AVAILABLE_RETURN"
  | "NOT_READY"
  | "MAINTENANCE";
type Vehicle = {
  id: string;
  plate: string;
  employee: string;
  employeeId: string;
  status: VehicleStatus;
  location: string;
  destination: string;
  type: string;
  lastService: string;
};

const vehicles: Vehicle[] = [
  {
    id: "V001",
    plate: "70-1234",
    employee: "สมชาย ใจดี",
    employeeId: "E001",
    status: "AVAILABLE",
    location: "หาดใหญ่",
    destination: "-",
    type: "6-wheel truck",
    lastService: "20 Aug 2026",
  },
  {
    id: "V002",
    plate: "70-5678",
    employee: "วิชัย ขับดี",
    employeeId: "E002",
    status: "BUSY",
    location: "สงขลา",
    destination: "หาดใหญ่",
    type: "6-wheel truck",
    lastService: "18 Aug 2026",
  },
  {
    id: "V003",
    plate: "70-9999",
    employee: "ประชา ตั้งใจ",
    employeeId: "E003",
    status: "AVAILABLE_RETURN",
    location: "ตรัง",
    destination: "ตรัง",
    type: "4-wheel truck",
    lastService: "12 Aug 2026",
  },
  {
    id: "V004",
    plate: "70-1111",
    employee: "กมล ส่งไว",
    employeeId: "E004",
    status: "MAINTENANCE",
    location: "ศูนย์ซ่อมบำรุง",
    destination: "-",
    type: "6-wheel truck",
    lastService: "01 Sep 2026",
  },
  {
    id: "V005",
    plate: "70-2222",
    employee: "ธนา เส้นทางดี",
    employeeId: "E006",
    status: "AVAILABLE",
    location: "พัทลุง",
    destination: "-",
    type: "4-wheel truck",
    lastService: "24 Aug 2026",
  },
  {
    id: "V006",
    plate: "70-3333",
    employee: "ยังไม่มอบหมาย",
    employeeId: "-",
    status: "NOT_READY",
    location: "หาดใหญ่",
    destination: "-",
    type: "10-wheel truck",
    lastService: "28 Jul 2026",
  },
];

const statusMeta: Record<
  VehicleStatus,
  { label: string; color: string; detail: string }
> = {
  AVAILABLE: { label: "AVAILABLE", color: "green", detail: "พร้อมรับงาน" },
  BUSY: { label: "BUSY", color: "amber", detail: "กำลังทำงาน" },
  AVAILABLE_RETURN: {
    label: "AVAILABLE_RETURN",
    color: "blue",
    detail: "พร้อมรับงานขากลับ",
  },
  NOT_READY: { label: "NOT_READY", color: "red", detail: "ไม่พร้อมรับงาน" },
  MAINTENANCE: { label: "MAINTENANCE", color: "slate", detail: "ซ่อมบำรุง" },
};

export function VehiclesPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<VehicleStatus | "">("");
  const [selected, setSelected] = useState<Vehicle | null>(null);
  const filteredVehicles = useMemo(
    () =>
      vehicles.filter((vehicle) => {
        const searchable =
          `${vehicle.id} ${vehicle.plate} ${vehicle.employee} ${vehicle.location}`.toLowerCase();
        return (
          (!query || searchable.includes(query.toLowerCase())) &&
          (!status || vehicle.status === status)
        );
      }),
    [query, status],
  );

  return (
    <>
      <PageHeading
        eyebrow="RESOURCES / FLEET"
        title="Vehicles"
        description="Monitor fleet availability, assignments and maintenance status."
        action={
          <button className="button button-primary">
            <Plus size={17} /> Add vehicle
          </button>
        }
      />
      <section className="vehicle-summary">
        <SummaryItem label="Total fleet" value={vehicles.length} />
        <SummaryItem
          label="Available"
          value={
            vehicles.filter((vehicle) => vehicle.status === "AVAILABLE").length
          }
          color="green"
        />
        <SummaryItem
          label="In operation"
          value={vehicles.filter((vehicle) => vehicle.status === "BUSY").length}
          color="amber"
        />
        <SummaryItem
          label="Maintenance"
          value={
            vehicles.filter((vehicle) => vehicle.status === "MAINTENANCE")
              .length
          }
          color="slate"
        />
      </section>
      <section className="vehicle-toolbar panel">
        <div className="vehicle-search input-with-icon">
          <Search size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search vehicle plate, employee or location"
          />
        </div>
        <label>
          <span>Status</span>
          <select
            value={status}
            onChange={(event) =>
              setStatus(event.target.value as VehicleStatus | "")
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
      <section className="vehicle-table-panel panel">
        <div className="table-heading">
          <div>
            <p className="eyebrow">FLEET DIRECTORY</p>
            <h2>{filteredVehicles.length} vehicles</h2>
          </div>
          <span className="result-note">
            Mock data · API integration pending
          </span>
        </div>
        <div className="vehicle-table-wrap">
          <table className="vehicle-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Employee</th>
                <th>Status</th>
                <th>Current location</th>
                <th>Destination</th>
                <th>Last service</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {filteredVehicles.map((vehicle) => (
                <tr key={vehicle.id}>
                  <td>
                    <div className="vehicle-cell">
                      <div className="vehicle-avatar">
                        <CarFront size={17} />
                      </div>
                      <div>
                        <strong>{vehicle.plate}</strong>
                        <span>
                          {vehicle.id} · {vehicle.type}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="vehicle-employee">
                      <UserRound size={13} />
                      {vehicle.employee}
                    </span>
                    <small>{vehicle.employeeId}</small>
                  </td>
                  <td>
                    <span
                      className={`status-pill ${statusMeta[vehicle.status].color}`}
                    >
                      <i />
                      {statusMeta[vehicle.status].label}
                    </span>
                    <small className="status-detail">
                      {statusMeta[vehicle.status].detail}
                    </small>
                  </td>
                  <td>
                    <span className="location-label">
                      <MapPin size={13} />
                      {vehicle.location}
                    </span>
                  </td>
                  <td>{vehicle.destination}</td>
                  <td>
                    <span className="service-date">{vehicle.lastService}</span>
                  </td>
                  <td>
                    <button
                      className="button button-outline view-button"
                      onClick={() => setSelected(vehicle)}
                    >
                      View <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredVehicles.length === 0 && (
            <div className="empty-state vehicle-empty">
              <CarFront size={27} />
              <strong>No vehicles found</strong>
              <span>Try clearing the current filters.</span>
            </div>
          )}
        </div>
      </section>
      {selected && (
        <VehicleDrawer vehicle={selected} onClose={() => setSelected(null)} />
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

function VehicleDrawer({
  vehicle,
  onClose,
}: Readonly<{ vehicle: Vehicle; onClose: () => void }>) {
  const meta = statusMeta[vehicle.status];
  return (
    <div className="drawer-backdrop">
      <aside className="employee-drawer vehicle-drawer">
        <div className="drawer-heading">
          <div>
            <p className="eyebrow">VEHICLE PROFILE</p>
            <h2>Vehicle details</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close vehicle profile"
          >
            <X size={19} />
          </button>
        </div>
        <div className="drawer-profile">
          <div className="drawer-avatar vehicle-drawer-avatar">
            <CarFront size={25} />
          </div>
          <h3>{vehicle.plate}</h3>
          <p>
            {vehicle.id} · {vehicle.type}
          </p>
          <span className={`status-pill ${meta.color}`}>
            <i />
            {meta.label}
          </span>
        </div>
        <dl className="employee-details">
          <div>
            <dt>Assigned employee</dt>
            <dd>
              <UserRound size={14} />
              {vehicle.employee}
            </dd>
          </div>
          <div>
            <dt>Current location</dt>
            <dd>
              <MapPin size={14} />
              {vehicle.location}
            </dd>
          </div>
          <div>
            <dt>Current destination</dt>
            <dd>{vehicle.destination}</dd>
          </div>
          <div>
            <dt>Last service</dt>
            <dd>
              <Wrench size={14} />
              {vehicle.lastService}
            </dd>
          </div>
        </dl>
        <button
          className="button button-primary drawer-action"
          onClick={onClose}
        >
          View full vehicle profile <ChevronRight size={15} />
        </button>
      </aside>
    </div>
  );
}
