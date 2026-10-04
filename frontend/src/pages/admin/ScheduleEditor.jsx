import { useState } from "react";
import { setSchedule } from "../../api/doctors";
import Alert from "../../components/Alert";
import DoctorPicker from "../../components/DoctorPicker";
import { WEEKDAYS } from "../../lib/format";

const hhmm = (t) => t.slice(0, 5);

export default function ScheduleEditor() {
  const [doctor, setDoctor] = useState(null);
  const [rows, setRows] = useState([]);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const pick = (d) => {
    setDoctor(d);
    setMsg({ type: "", text: "" });
    setRows(d ? d.schedules.map((s) => ({ weekday: s.weekday, start_time: hhmm(s.start_time), end_time: hhmm(s.end_time) })) : []);
  };
  const update = (i, k, v) => setRows(rows.map((r, idx) => (idx === i ? { ...r, [k]: k === "weekday" ? Number(v) : v } : r)));

  const save = async () => {
    try {
      const updated = await setSchedule(doctor.id, rows);
      setDoctor(updated);
      setMsg({ type: "success", text: "Schedule saved." });
    } catch (e) {
      setMsg({ type: "error", text: e.message });
    }
  };

  return (
    <div className="card">
      <h2>Weekly schedule</h2>
      <DoctorPicker value={doctor?.id} onChange={pick} />
      {doctor && (
        <>
          <p className="muted">Working windows in clinic time. Slots are generated using {doctor.slot_minutes}-minute steps.</p>
          {rows.map((r, i) => (
            <div className="row-inline" key={i}>
              <select value={r.weekday} onChange={(e) => update(i, "weekday", e.target.value)}>
                {WEEKDAYS.map((w, idx) => <option key={w} value={idx}>{w}</option>)}
              </select>
              <input type="time" value={r.start_time} onChange={(e) => update(i, "start_time", e.target.value)} />
              <span>to</span>
              <input type="time" value={r.end_time} onChange={(e) => update(i, "end_time", e.target.value)} />
              <button className="btn btn-outline" onClick={() => setRows(rows.filter((_, idx) => idx !== i))}>Remove</button>
            </div>
          ))}
          <div className="row-inline">
            <button className="btn btn-outline" onClick={() => setRows([...rows, { weekday: 0, start_time: "09:00", end_time: "13:00" }])}>+ Add window</button>
            <button className="btn" onClick={save}>Save schedule</button>
          </div>
        </>
      )}
      <Alert type={msg.type}>{msg.text}</Alert>
    </div>
  );
}
