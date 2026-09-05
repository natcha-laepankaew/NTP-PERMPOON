import { useEffect, useState } from "react";
import { ClipboardList, Search, ShieldCheck, Truck } from "lucide-react";
import {
  canMutateOperations,
  getCandidates,
  type Candidate,
} from "../services/api";
import { AssignModal } from "../components/AssignModal";
import { CandidateCard } from "../components/CandidateCard";
import { CreateJobModal } from "../components/CreateJobModal";
import { PageHeading } from "../components/PageHeading";

export function DispatchPage() {
  const canCreateJob = canMutateOperations();
  const [origin, setOrigin] = useState("หาดใหญ่");
  const [employee, setEmployee] = useState("");
  const [plate, setPlate] = useState("");
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [createJobOpen, setCreateJobOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  async function search() {
    setLoading(true);
    setSearched(true);
    try {
      const response = await getCandidates({
        origin,
        employee_name: employee,
        vehicle_plate: plate,
        status,
      });
      setItems(response.items);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    search();
  }, []);
  function renderResults() {
    if (loading)
      return (
        <div className="empty-state">
          <div className="spinner" /> Loading candidates
        </div>
      );
    if (searched && items.length === 0)
      return (
        <div className="empty-state">
          <Truck size={28} />
          <strong>No vehicles found</strong>
          <span>Try clearing a filter or choosing another origin.</span>
        </div>
      );
    return (
      <div className="candidate-grid">
        {items.map((item) => (
          <CandidateCard
            key={item.vehicle_id}
            candidate={item}
            onAssign={() => setSelected(item)}
          />
        ))}
      </div>
    );
  }
  return (
    <>
      <PageHeading
        eyebrow="OPERATIONS / DISPATCH"
        title="Dispatch Board"
        description="Find the right vehicle for an external job in seconds."
        action={
          canCreateJob ? (
            <button
              className="button button-primary"
              onClick={() => setCreateJobOpen(true)}
            >
              <ClipboardList size={17} /> Create job
            </button>
          ) : undefined
        }
      />
      <section className="dispatch-search panel">
        <div className="search-title">
          <div className="search-icon">
            <Search size={20} />
          </div>
          <div>
            <h2>Find candidate vehicles</h2>
            <p>
              Search the backend for vehicles that can start from your origin.
            </p>
          </div>
        </div>
        <div className="filters">
          <label>
            <span>Origin</span>
            <input
              value={origin}
              onChange={(event) => setOrigin(event.target.value)}
              placeholder="e.g. หาดใหญ่"
            />
          </label>
          <label>
            <span>Employee name</span>
            <input
              value={employee}
              onChange={(event) => setEmployee(event.target.value)}
              placeholder="Search employee"
            />
          </label>
          <label>
            <span>Vehicle plate</span>
            <input
              value={plate}
              onChange={(event) => setPlate(event.target.value)}
              placeholder="e.g. 70-1234"
            />
          </label>
          <label>
            <span>Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="AVAILABLE">Available</option>
              <option value="AVAILABLE_RETURN">Return-ready</option>
              <option value="BUSY">Busy</option>
            </select>
          </label>
          <button className="button button-dark filter-button" onClick={search}>
            <Search size={17} /> Search
          </button>
        </div>
        <div className="filter-hints">
          <span>
            <i className="legend-dot green" /> Available + Ready From ={" "}
            {origin || "origin"}
          </span>
          <span>
            <i className="legend-dot blue" /> Return-ready + Current Destination
            = {origin || "origin"}
          </span>
        </div>
      </section>
      <section className="candidate-section">
        <div className="section-header">
          <div>
            <p className="eyebrow">CANDIDATE VEHICLES</p>
            <h2>
              {loading
                ? "Searching..."
                : `${items.length} vehicles can take this job`}
            </h2>
          </div>
          <span className="result-note">
            <ShieldCheck size={12} /> Backend filtered · Updated just now
          </span>
        </div>
        {renderResults()}
      </section>
      {successMessage && (
        <output className="toast-success">✓ {successMessage}</output>
      )}
      {selected && (
        <AssignModal candidate={selected} onClose={() => setSelected(null)} />
      )}
      {createJobOpen && (
        <CreateJobModal
          onClose={() => setCreateJobOpen(false)}
          onCreated={(jobId) => {
            setCreateJobOpen(false);
            setSuccessMessage(`Job ${jobId} created successfully`);
            setTimeout(() => setSuccessMessage(""), 4000);
          }}
        />
      )}
    </>
  );
}
