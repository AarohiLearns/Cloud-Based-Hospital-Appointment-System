import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { bookAppointment } from "../api/appointments";
import { getAvailability, getDoctor } from "../api/doctors";
import Alert from "../components/Alert";
import { MAX_BOOKING_DAYS_AHEAD } from "../config";
import { useAuth } from "../context/AuthContext";
import { addDaysISO, formatDateTime, formatTime, todayISO } from "../lib/format";

export default function DoctorDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [doctor, setDoctor] = useState(null);
  const [date, setDate] = useState(todayISO());
  const [availability, setAvailability] = useState(null);
  const [selected, setSelected] = useState(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getDoctor(id).then(setDoctor).catch((e) => setError(e.message));
  }, [id]);

  const loadSlots = () =>
    getAvailability(id, date)
      .then((a) => { setAvailability(a); setError(""); })
      .catch((e) => setError(e.message));

  useEffect(() => {
    setSelected(null);
    setAvailability(null);
    if (date) loadSlots();
  }, [id, date]); // eslint-disable-line react-hooks/exhaustive-deps

  const book = async () => {
    setBusy(true);
    setError("");
    try {
      await bookAppointment({ doctor_id: id, start_time: selected.start_time, reason: reason || null });
      navigate("/appointments", { state: { booked: true } });
    } catch (e) {
      setError(e.message);
      setSelected(null);
      loadSlots(); // slot may have just been taken - refresh
    } finally {
      setBusy(false);
    }
  };

  if (!doctor) return <Alert>{error}</Alert>;

  return (
    <>
      <Link to="/" className="muted">&larr; All doctors</Link>
      <div className="card">
        <h1>{doctor.full_name}</h1>
        <span className="badge">{doctor.specialization}</span>
        {doctor.department && <p className="muted">{doctor.department}</p>}
        {doctor.bio && <p>{doctor.bio}</p>}
      </div>

      <div className="card">
        <h2>Choose a date &amp; time</h2>
        <input type="date" value={date} min={todayISO()} max={addDaysISO(todayISO(), MAX_BOOKING_DAYS_AHEAD)}
               onChange={(e) => setDate(e.target.value)} />
        <Alert>{error}</Alert>
        {availability && availability.slots.length === 0 && <p className="muted">No free slots on this day.</p>}
        <div className="slots">
          {availability?.slots.map((s) => (
            <button key={s.start_time} type="button"
                    className={`slot ${selected?.start_time === s.start_time ? "selected" : ""}`}
                    onClick={() => setSelected(s)}>
              {formatTime(s.start_time, availability.timezone)}
            </button>
          ))}
        </div>

        {selected && (
          user ? (
            user.role === "patient" ? (
              <div className="form">
                <p>Selected: <strong>{formatDateTime(selected.start_time, availability.timezone)}</strong></p>
                <label>Reason for visit (optional)
                  <textarea rows={2} maxLength={500} value={reason} onChange={(e) => setReason(e.target.value)} />
                </label>
                <button className="btn" onClick={book} disabled={busy}>{busy ? "Booking..." : "Confirm booking"}</button>
              </div>
            ) : <p className="muted">Only patient accounts can book appointments.</p>
          ) : (
            <p><Link to="/login" state={{ from: `/doctors/${id}` }}>Login</Link> or <Link to="/register">sign up</Link> to book this slot.</p>
          )
        )}
      </div>
    </>
  );
}
