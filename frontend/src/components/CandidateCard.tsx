import { ChevronRight, ShieldCheck, Truck } from "lucide-react";
import { statusMeta } from "./StatusMeta";
import type { Candidate } from "../services/api";

export function CandidateCard({
  candidate,
  onAssign,
}: Readonly<{ candidate: Candidate; onAssign: () => void }>) {
  const meta = statusMeta[candidate.operational_status];
  return (
    <article className="candidate-card">
      <div className="candidate-top">
        <div className="vehicle-icon">
          <Truck size={21} />
        </div>
        <div>
          <h3>{candidate.vehicle_plate}</h3>
          <p>{candidate.employee_name}</p>
        </div>
        <span className={`status-pill ${meta.color}`}>
          <i />
          {meta.label}
        </span>
      </div>
      <div className="candidate-context">
        <div>
          <span>
            {candidate.candidate_type === "return"
              ? "Current destination"
              : "Ready from"}
          </span>
          <strong>
            {candidate.current_destination ??
              candidate.ready_from ??
              "ยังไม่ระบุ"}
          </strong>
        </div>
        <div>
          <span>Candidate type</span>
          <strong>
            {candidate.candidate_type === "return"
              ? "ONE_WAY return"
              : "New job"}
          </strong>
        </div>
      </div>
      <div className="candidate-foot">
        <span className="explain">
          <ShieldCheck size={15} /> {meta.sub}
        </span>
        <button className="button button-outline" onClick={onAssign}>
          Assign job <ChevronRight size={15} />
        </button>
      </div>
    </article>
  );
}
