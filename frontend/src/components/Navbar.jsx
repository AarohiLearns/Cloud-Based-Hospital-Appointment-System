import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="navbar">
      <Link to="/" className="brand">+ City Hospital</Link>
      <nav>
        <NavLink to="/">Doctors</NavLink>
        {user?.role === "patient" && <NavLink to="/appointments">My Appointments</NavLink>}
        {user?.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
        {user ? (
          <>
            <span className="muted">{user.full_name}</span>
            <button className="btn btn-outline" onClick={() => { logout(); navigate("/login"); }}>Logout</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register" className="btn">Sign up</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
