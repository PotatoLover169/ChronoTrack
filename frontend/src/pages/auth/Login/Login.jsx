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
      await login(username, password);

      navigate("/");
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
        <div className="login-brand">
          <div className="login-brand-mark">
            CT
          </div>

          <div>
            <h1>ChronoTrack</h1>
            <p>Time & Productivity</p>
          </div>
        </div>

        <div className="login-header">
          <p className="login-eyebrow">
            Welcome back
          </p>

          <h2>Sign in to your account</h2>

          <p>
            Enter your credentials to continue to ChronoTrack.
          </p>
        </div>

        <form
          className="login-form"
          onSubmit={handleSubmit}
        >
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

          {error && (
            <p className="login-error">
              {error}
            </p>
          )}

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

        <p className="login-footer">
          ChronoTrack · Time & Productivity Management
        </p>
      </section>
    </main>
  );
}

export default Login;