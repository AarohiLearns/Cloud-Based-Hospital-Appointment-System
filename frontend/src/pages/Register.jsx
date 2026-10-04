import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import * as authApi from "../api/auth";
import Alert from "../components/Alert";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await authApi.register({ ...form, phone: form.phone || null });
      await login(form.email, form.password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card form narrow" onSubmit={submit}>
      <h2>Create your account</h2>
      <Alert>{error}</Alert>
      <label>Full name<input value={form.full_name} onChange={set("full_name")} required minLength={2} /></label>
      <label>Email<input type="email" value={form.email} onChange={set("email")} required /></label>
      <label>Phone (optional)<input value={form.phone} onChange={set("phone")} maxLength={20} /></label>
      <label>Password (min 8 characters)<input type="password" value={form.password} onChange={set("password")} required minLength={8} maxLength={72} /></label>
      <button className="btn" disabled={busy}>{busy ? "Creating..." : "Sign up"}</button>
      <p className="muted">Already registered? <Link to="/login">Login</Link></p>
    </form>
  );
}
