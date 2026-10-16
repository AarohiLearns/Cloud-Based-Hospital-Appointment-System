import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listDoctors } from "../api/doctors";
import Alert from "../components/Alert";

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [q, setQ] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {   // small debounce while typing
      listDoctors({ q, specialization })
        .then((d) => { setDoctors(d); setError(""); })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [q, specialization]);

  return (
    <>
      <h1>Find a doctor</h1>
      <p className="muted">Check availability and book instantly - no waiting in queues.</p>
      <div className="toolbar">
        <input placeholder="Search by name" value={q} onChange={(e) => setQ(e.target.value)} />
        <input placeholder="Specialization (e.g. Cardiology)" value={specialization} onChange={(e) => setSpecialization(e.target.value)} />
      </div>
      <Alert>{error}</Alert>
      {loading && <p className="muted">Loading...</p>}
      {!loading && !error && doctors.length === 0 && <p className="muted">No doctors found.</p>}
      <div className="grid">
        {doctors.map((d) => (
          <Link key={d.id} to={`/doctors/${d.id}`} className="card doctor-card">
            <h3>{d.full_name}</h3>
            <span className="badge">{d.specialization}</span>
            {d.department && <p className="muted">{d.department}</p>}
            <p className="muted">{d.slot_minutes}-minute consultations</p>
          </Link>
        ))}
      </div>
    </>
  );
}
/*Doctors.jsx is the frontend page that displays doctors and lets the user search/filter them.*/
/*Doctors.jsx → gets doctors from the backend, provides name/specialization search,
 handles loading/errors, and displays each doctor as a clickable card. */
