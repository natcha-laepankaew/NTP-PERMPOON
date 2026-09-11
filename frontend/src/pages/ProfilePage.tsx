import { useEffect, useState } from "react";
import {
  BadgeCheck,
  Building2,
  CarFront,
  KeyRound,
  Mail,
  MapPin,
  Phone,
  Save,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { PageHeading } from "../components/PageHeading";
import {
  getMyProfile,
  updateMyProfile,
  type UserProfile,
} from "../services/api";

const roleLabel: Record<string, string> = {
  ADMINISTRATOR: "Administrator",
  ADMIN: "Admin",
  DRIVER: "Driver",
  MANAGER: "Manager",
};

export function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getMyProfile()
      .then((data) => {
        setProfile(data);
        setPhone(data.phone ?? "");
        setAddress(data.address ?? "");
      })
      .catch(() => setError("Unable to load your profile. Please try again."))
      .finally(() => setLoading(false));
  }, []);

  async function saveContact() {
    setError("");
    setMessage("");
    if (phone.trim().length < 3 || address.trim().length < 3) {
      setError("Please provide a phone number and address.");
      return;
    }
    setSaving(true);
    try {
      const updated = await updateMyProfile({ phone: phone.trim(), address: address.trim() });
      setProfile(updated);
      setMessage("Your contact information has been updated.");
    } catch {
      setError("Unable to save your changes. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  const isDriver = profile?.role.name === "DRIVER";
  const initials = profile?.name.slice(0, 2).toUpperCase() ?? "--";

  return (
    <>
      <PageHeading
        eyebrow="ACCOUNT SETTINGS"
        title="My profile"
        description="Review your account details and keep your contact information current."
        action={<span />}
      />
      {loading ? (
        <div className="panel profile-loading">Loading profile…</div>
      ) : !profile ? (
        <div className="panel profile-loading profile-error">{error}</div>
      ) : (
        <div className="profile-layout">
          <section className="panel profile-summary-card">
            <div className="profile-cover" />
            <div className="profile-summary-content">
              <div className="profile-avatar">{initials}</div>
              <div className="profile-name-row">
                <div>
                  <h2>{profile.name}</h2>
                  <p>{roleLabel[profile.role.name] ?? profile.role.name}</p>
                </div>
                <span className="profile-verified"><BadgeCheck size={15} /> Active account</span>
              </div>
              <dl className="profile-facts">
                <div><dt><Mail size={15} /> Email</dt><dd>{profile.email}</dd></div>
                <div><dt><ShieldCheck size={15} /> Role</dt><dd>{roleLabel[profile.role.name] ?? profile.role.name}</dd></div>
                <div><dt><KeyRound size={15} /> Account ID</dt><dd>{profile.id}</dd></div>
                {profile.employee_id && <div><dt><UserRound size={15} /> Employee ID</dt><dd>{profile.employee_id}</dd></div>}
              </dl>
            </div>
          </section>

          <section className="panel profile-details-card">
            <div className="profile-section-heading">
              <div>
                <p className="eyebrow">{isDriver ? "CONTACT INFORMATION" : "ACCOUNT ACCESS"}</p>
                <h2>{isDriver ? "Personal details" : "Administrator profile"}</h2>
              </div>
              <Building2 size={19} />
            </div>
            {isDriver ? (
              <div className="profile-form">
                <label className="profile-field"><span><Phone size={15} /> Phone number</span><input value={phone} onChange={(event) => setPhone(event.target.value)} /></label>
                <label className="profile-field"><span><MapPin size={15} /> Address</span><textarea value={address} onChange={(event) => setAddress(event.target.value)} rows={4} /></label>
                {error && <p className="profile-form-message error">{error}</p>}
                {message && <p className="profile-form-message success">{message}</p>}
                <button className="button button-primary profile-save" onClick={() => void saveContact()} disabled={saving}>
                  <Save size={16} /> {saving ? "Saving…" : "Save changes"}
                </button>
              </div>
            ) : (
              <div className="profile-admin-note">
                <ShieldCheck size={22} />
                <div><strong>System administrator account</strong><span>Your permissions are managed through Roles & Permissions. Contact details are not required for this account type.</span></div>
              </div>
            )}
            {isDriver && profile.vehicle && (
              <div className="profile-vehicle"><CarFront size={18} /><div><span>Assigned vehicle</span><strong>{profile.vehicle.plate}</strong></div><em>{profile.vehicle.status.replaceAll("_", " ")}</em></div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
