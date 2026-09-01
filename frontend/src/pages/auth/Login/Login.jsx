import "../../../styles/login.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../../hooks/useAuth";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const loggedInUser = await login(username, password);

      /*
       * Redirect the user based on their role.
       *
       * Employee -> /
       * Manager  -> /manager
       * Admin    -> /admin
       */

      if (loggedInUser?.role === "Admin") {
        navigate("/admin", { replace: true });
      } else if (loggedInUser?.role === "Manager") {
        navigate("/manager", { replace: true });
      } else {
        navigate("/", { replace: true });
      }

    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Invalid username or password."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-card">

        {/* Brand */}
        <div className="login-brand">
          <div className="login-brand-mark">
            CT
          </div>

          <div>
            <h1>ChronoTrack</h1>
            <p>Time & Productivity</p>
          </div>
        </div>

        {/* Header */}
        <div className="login-header">
          <p className="login-eyebrow">
            Welcome back
          </p>

          <h2>
            Sign in to your account
          </h2>

          <p>
            Enter your credentials to continue to ChronoTrack.
          </p>
        </div>

        {/* Login Form */}
        <form
          className="login-form"
          onSubmit={handleSubmit}
        >

          {/* Username */}
          <div className="login-field">
            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Enter your username"
              autoComplete="username"
              required
            />
          </div>

          {/* Password */}
          <div className="login-field">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </div>

          {/* Error */}
          {error && (
            <p className="login-error">
              {error}
            </p>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="login-button"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Signing in..."
              : "Sign In"}
          </button>

        </form>

        {/* Footer */}
        <p className="login-footer">
          ChronoTrack · Time & Productivity Management
        </p>

      </section>
    </main>
  );
}

export default Login;