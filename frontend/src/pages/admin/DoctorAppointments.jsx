import { useCallback, useEffect, useState } from "react";
import { cancelAppointment, completeAppointment, doctorAppointments } from "../../api/appointments";
import Alert from "../../components/Alert";
import DoctorPicker from "../../components/DoctorPicker";
import { formatTime, todayISO } from "../../lib/format";

export default function DoctorAppointments() {
  const [doctor, setDoctor] = useState(null);
  const [date, setDate] = useState(todayISO());
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    if (!doctor) return setItems([]);
    doctorAppointments(doctor.id, date).then((d) => { setItems(d); setError(""); }).catch((e) => setError(e.message));
  }, [doctor, date]);
  useEffect(load, [load]);

  const act = (fn) => async (id) => {
    try { await fn(id); load(); } catch (e) { setError(e.message); }
  };

  return (
    <div className="card">
      <h2>Appointments by doctor</h2>
      <div className="row-inline">
        <DoctorPicker value={doctor?.id} onChange={setDoctor} />
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      </div>
      <Alert>{error}</Alert>
      {doctor && items.length === 0 && <p className="muted">No appointments on this day.</p>}
      {items.map((a) => (
        <div key={a.id} className="row appt-row">
          <div>
            <strong>{formatTime(a.start_time)}</strong> - {a.patient.full_name}
            {a.patient.phone && <span className="muted"> ({a.patient.phone})</span>}
            {a.reason && <div className="muted">{a.reason}</div>}
          </div>
          <div className="actions">
            <span className={`status status-${a.status}`}>{a.status}</span>
            {a.status === "booked" && (
              <>
                <button className="btn" onClick={() => act(completeAppointment)(a.id)}>Complete</button>
                <button className="btn btn-outline" onClick={() => act(cancelAppointment)(a.id)}>Cancel</button>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
