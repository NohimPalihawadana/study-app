
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { apiRequest } from "../api";

function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    apiRequest("/auth/me")
      .then((data) => {
        if (active) setUser(data);
      })
      .catch(() => {
        if (active) navigate("/login", { replace: true });
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  async function handleLogout() {
    try {
      setError("");
      await apiRequest("/auth/logout", { method: "POST" });
      navigate("/login", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  if (!user) {
    return <main className="auth-page">Checking login...</main>;
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h1>Welcome, {user.username}!</h1>

        <p>You have successfully logged in.</p>

        <p><strong>University:</strong> {user.university}</p>

        <p>
          <strong>Field of Study:</strong> {user.field_of_study}
        </p>

        {error && <p className="auth-error" role="alert">{error}</p>}

        <button onClick={handleLogout}>Logout</button>
      </div>
    </main>
  );
}

export default Dashboard;
