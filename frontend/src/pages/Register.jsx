
import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { apiRequest } from "../api";
import "../Auth.css";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
    confirm_password: "",
    university: "",
    field_of_study: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });

      navigate("/login", {
        state: { message: "Account created! You can now log in." },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-brand">
          ✦ study-app
        </Link>

        <h1>Create your account</h1>
        <p className="auth-subtitle">
          Start building your personal learning workspace.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="reg-username">Username</label>
          <input
            id="reg-username"
            name="username"
            value={form.username}
            onChange={handleChange}
            autoComplete="username"
            minLength={3}
            maxLength={30}
            pattern="[A-Za-z0-9_]+"
            title="Use letters, numbers, or underscores."
            required
          />

          <label htmlFor="reg-password">Password</label>
          <input
            id="reg-password"
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
          />

          <label htmlFor="reg-confirm">Confirm Password</label>
          <input
            id="reg-confirm"
            type="password"
            name="confirm_password"
            value={form.confirm_password}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />

          <label htmlFor="university">University</label>
          <input
            id="university"
            name="university"
            value={form.university}
            onChange={handleChange}
            maxLength={120}
            required
          />

          <label htmlFor="field">Your Field of Study</label>
          <input
            id="field"
            name="field_of_study"
            value={form.field_of_study}
            onChange={handleChange}
            maxLength={120}
            placeholder="e.g. Software Engineering"
            required
          />

          {error && <p className="auth-error" role="alert">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login">Login</Link>
        </p>
      </div>
    </main>
  );
}

export default Register;
