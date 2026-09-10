import { useState } from "react";
import {
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  Truck,
  UserRound,
} from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLocation, useNavigate } from "react-router-dom";
import { login } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address."),
  password: z.string().min(6, "Password must be at least 6 characters."),
});

type LoginForm = z.infer<typeof loginSchema>;
type RedirectState = {
  from?: { pathname: string; search?: string; hash?: string };
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { refresh } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(values: LoginForm) {
    setSubmitError("");
    try {
      const session = await login(values.email, values.password);
      await refresh();
      const from = (location.state as RedirectState | null)?.from;
      const destination = from
        ? `${from.pathname}${from.search ?? ""}${from.hash ?? ""}`
        : "/";
      navigate(session.profile_completed ? destination : "/complete-profile", {
        replace: true,
      });
    } catch {
      setSubmitError("Invalid email or password.");
    }
  }

  return (
    <main className="login-shell">
      <section className="login-visual" aria-label="NTP PERMPOON operations">
        <div className="login-visual-top">
          <div className="brand-mark">N</div>
          <span>NTP / PERMPOON</span>
        </div>
        <div className="login-visual-copy">
          <p className="eyebrow">DELIVERY OPERATIONS PLATFORM</p>
          <h1>
            Move every job
            <br />
            <strong>with confidence.</strong>
          </h1>
          <p>
            One control center for your fleet, people and daily dispatch
            decisions.
          </p>
        </div>
        <div className="login-visual-footer">
          <span>
            <i /> System operational
          </span>
          <span>v0.1.0</span>
        </div>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <div className="login-heading">
            <div className="login-icon">
              <Truck size={22} />
            </div>
            <p className="eyebrow">WELCOME BACK</p>
            <h2>Sign in to control center</h2>
            <p>Use your NTP PERMPOON account to continue.</p>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <label className="login-field">
              <span>Email address</span>
              <div className="input-with-icon">
                <UserRound size={17} />
                <input
                  type="email"
                  autoComplete="email"
                  placeholder="name@ntp-permpoon.com"
                  {...register("email")}
                />
              </div>
              {errors.email && (
                <small className="field-error">{errors.email.message}</small>
              )}
            </label>
            <label className="login-field">
              <span>Password</span>
              <div className="input-with-icon">
                <LockKeyhole size={17} />
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  {...register("password")}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((visible) => !visible)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
              {errors.password && (
                <small className="field-error">{errors.password.message}</small>
              )}
            </label>
            {submitError && <p className="login-error">{submitError}</p>}
            <div className="login-options">
              <label>
                <input type="checkbox" /> <span>Remember me</span>
              </label>
              <button type="button" className="text-button">
                Forgot password?
              </button>
            </div>
            <button
              className="button button-login"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <div className="login-security">
            <ShieldCheck size={15} />
            <span>Secure access for authorized operations staff</span>
          </div>
        </div>
        <p className="login-copyright">
          © 2026 NTP PERMPOON · Internal operations platform
        </p>
      </section>
    </main>
  );
}
