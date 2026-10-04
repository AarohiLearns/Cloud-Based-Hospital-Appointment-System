import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { cancelAppointment, myAppointments } from "../api/appointments";
import Alert from "../components/Alert";
import { formatDateTime } from "../lib/format";

export default function MyAppointments() {
  const location = useLocation();
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  const load = () => myAppointments().then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const cancel = async (id) => {
    if (!window.confirm("Cancel this appointment?")) return;
    try {
      await cancelAppointment(id);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <h1>My appointments</h1>
      {location.state?.booked && <Alert type="success">Appointment booked successfully!</Alert>}
      <Alert>{error}</Alert>
      {items === null && !error && <p className="muted">Loading...</p>}
      {items?.length === 0 && <p className="muted">You have no appointments yet.</p>}
      <div className="list">
        {items?.map((a) => (
          <div key={a.id} className="card row">
            <div>
              <h3>{a.doctor.full_name} <span className="badge">{a.doctor.specialization}</span></h3>
              <p>{formatDateTime(a.start_time)}</p>
              {a.reason && <p className="muted">Reason: {a.reason}</p>}
            </div>
            <div className="actions">
              <span className={`status status-${a.status}`}>{a.status}</span>
              {a.status === "booked" && new Date(a.start_time) > new Date() && (
                <button className="btn btn-outline" onClick={() => cancel(a.id)}>Cancel</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
