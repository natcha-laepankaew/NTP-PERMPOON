import { ShieldCheck, Truck, X } from "lucide-react";
import { statusMeta } from "./StatusMeta";
import type { Candidate } from "../services/api";

type AssignModalProps = Readonly<{
  candidate: Candidate;
  onClose: () => void;
}>;

export function AssignModal({ candidate, onClose }: AssignModalProps) {
  return (
    <dialog open className="modal-backdrop" aria-labelledby="assign-title">
      <div className="modal">
        <div className="modal-heading">
          <div>
            <p className="eyebrow">ASSIGNMENT REVIEW</p>
            <h2 id="assign-title">Assign this vehicle?</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close assignment dialog"
          >
            <X size={19} />
          </button>
        </div>
        <div className="route-preview">
          <div>
            <span>ORIGIN</span>
            <strong>หาดใหญ่</strong>
          </div>
          <div className="route-line">
            <Truck size={18} />
          </div>
          <div>
            <span>DESTINATION</span>
            <strong>พัทลุง</strong>
          </div>
        </div>
        <dl className="detail-list">
          <div>
            <dt>Employee</dt>
            <dd>{candidate.employee_name}</dd>
          </div>
          <div>
            <dt>Vehicle</dt>
            <dd>{candidate.vehicle_plate}</dd>
          </div>
          <div>
            <dt>Vehicle status</dt>
            <dd>
              <span
                className={`status-pill ${statusMeta[candidate.operational_status].color}`}
              >
                <i />
                {candidate.operational_status}
              </span>
            </dd>
          </div>
        </dl>
        <div className="modal-warning">
          <ShieldCheck size={17} />
          <span>
            Availability will be checked again by the backend before assignment.
          </span>
        </div>
        <div className="modal-actions">
          <button className="button button-quiet" onClick={onClose}>
            Cancel
          </button>
          <button className="button button-primary" onClick={onClose}>
            Confirm assignment
          </button>
        </div>
      </div>
    </dialog>
  );
}
