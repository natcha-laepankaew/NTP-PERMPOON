import { useState } from "react";
import { MapPin, Phone, ShieldCheck } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { completeProfile } from "../services/api";

const profileSchema = z.object({
  phone: z.string().min(3, "Phone is required."),
  address: z.string().min(3, "Address is required."),
});
type ProfileForm = z.infer<typeof profileSchema>;

export function CompleteProfilePage() {
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileForm>({ resolver: zodResolver(profileSchema) });
  async function submit(values: ProfileForm) {
    try {
      await completeProfile(values);
      navigate("/", { replace: true });
    } catch {
      setSubmitError("Unable to complete profile. Please try again.");
    }
  }
  return (
    <main className="profile-complete-shell">
      <div className="profile-complete-card">
        <div className="login-icon">
          <ShieldCheck size={22} />
        </div>
        <p className="eyebrow">FIRST LOGIN</p>
        <h1>Complete your profile</h1>
        <p className="profile-intro">
          Your administrator created this account. Add the required personal
          information before continuing.
        </p>
        <form onSubmit={handleSubmit(submit)}>
          <label className="login-field">
            <span>Phone</span>
            <div className="input-with-icon">
              <Phone size={17} />
              <input {...register("phone")} placeholder="08X-XXX-XXXX" />
            </div>
            {errors.phone && (
              <small className="field-error">{errors.phone.message}</small>
            )}
          </label>
          <label className="login-field">
            <span>Address</span>
            <div className="input-with-icon">
              <MapPin size={17} />
              <input {...register("address")} placeholder="Current address" />
            </div>
            {errors.address && (
              <small className="field-error">{errors.address.message}</small>
            )}
          </label>
          {submitError && <p className="login-error">{submitError}</p>}
          <button
            type="submit"
            className="button button-login"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Saving..." : "Complete profile"}
          </button>
        </form>
      </div>
    </main>
  );
}
