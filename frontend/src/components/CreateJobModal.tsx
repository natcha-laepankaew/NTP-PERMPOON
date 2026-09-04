import { X } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { createJob, type CreateJobPayload } from "../services/api";

const createJobSchema = z.object({
  source: z.enum(["EXTERNAL", "INTERNAL"]),
  origin: z.string().min(1, "Origin is required."),
  destination: z.string().min(1, "Destination is required."),
  pickup_date: z.string().min(1, "Pickup date is required."),
  pickup_time: z.string().min(1, "Pickup time is required."),
  customer_reference: z.string().optional(),
  notes: z.string().optional(),
  job_type: z.enum(["ONE_WAY", "ROUND_TRIP"]),
});

export function CreateJobModal({
  onClose,
  onCreated,
}: Readonly<{ onClose: () => void; onCreated: (jobId: string) => void }>) {
  const [submitError, setSubmitError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateJobPayload>({
    resolver: zodResolver(createJobSchema),
    defaultValues: { source: "EXTERNAL", job_type: "ONE_WAY" },
  });
  async function submit(payload: CreateJobPayload) {
    setSubmitError("");
    try {
      const job = await createJob(payload);
      onCreated(job.id);
    } catch {
      setSubmitError("Unable to create this job. Please try again.");
    }
  }
  return (
    <dialog open className="modal-backdrop" aria-labelledby="create-job-title">
      <div className="modal create-job-modal">
        <div className="modal-heading">
          <div>
            <p className="eyebrow">NEW OPERATION</p>
            <h2 id="create-job-title">Create job</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close create job dialog"
          >
            <X size={19} />
          </button>
        </div>
        <form className="job-form" onSubmit={handleSubmit(submit)}>
          <fieldset>
            <legend>Job source</legend>
            <label className="radio-option">
              <input type="radio" value="EXTERNAL" {...register("source")} />{" "}
              External job
            </label>
            <label className="radio-option">
              <input type="radio" value="INTERNAL" {...register("source")} />{" "}
              Internal job
            </label>
          </fieldset>
          <div className="job-form-grid">
            <FormField label="Origin" error={errors.origin?.message}>
              <input placeholder="e.g. หาดใหญ่" {...register("origin")} />
            </FormField>
            <FormField label="Destination" error={errors.destination?.message}>
              <input placeholder="e.g. พัทลุง" {...register("destination")} />
            </FormField>
            <FormField label="Pickup date" error={errors.pickup_date?.message}>
              <input type="date" {...register("pickup_date")} />
            </FormField>
            <FormField label="Pickup time" error={errors.pickup_time?.message}>
              <input type="time" {...register("pickup_time")} />
            </FormField>
          </div>
          <FormField label="Customer / reference">
            <input
              placeholder="Optional reference"
              {...register("customer_reference")}
            />
          </FormField>
          <FormField label="Job type">
            <select {...register("job_type")}>
              <option value="ONE_WAY">ONE_WAY</option>
              <option value="ROUND_TRIP">ROUND_TRIP</option>
            </select>
          </FormField>
          <FormField label="Notes">
            <textarea
              rows={3}
              placeholder="Optional notes"
              {...register("notes")}
            />
          </FormField>
          {submitError && <p className="login-error">{submitError}</p>}
          <div className="modal-actions">
            <button
              type="button"
              className="button button-quiet"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="button button-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating..." : "Create job"}
            </button>
          </div>
        </form>
      </div>
    </dialog>
  );
}

function FormField({
  label,
  error,
  children,
}: Readonly<{ label: string; error?: string; children: React.ReactNode }>) {
  return (
    <label className="job-form-field">
      <span>{label}</span>
      {children}
      {error && <small className="field-error">{error}</small>}
    </label>
  );
}
