import { useState } from "react";
import { createDoctor } from "../../api/doctors";
import Alert from "../../components/Alert";

const EMPTY = { full_name: "", specialization: "", department: "", bio: "", slot_minutes: 30 };

export default function AddDoctor() {
  const [form, setForm] = useState(EMPTY);
  const [msg, setMsg] = useState({ type: "", text: "" });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const d = await createDoctor({
        ...form,
        department: form.department || null,
        bio: form.bio || null,
        slot_minutes: Number(form.slot_minutes),
      });
      setMsg({ type: "success", text: `${d.full_name} added. Now set a weekly schedule under "Doctor schedules".` });
      setForm(EMPTY);
    } catch (err) {
      setMsg({ type: "error", text: err.message });
    }
  };

  return (
    <form className="card form narrow" onSubmit={submit}>
      <h2>Add a doctor</h2>
      <Alert type={msg.type}>{msg.text}</Alert>
      <label>Full name<input value={form.full_name} onChange={set("full_name")} required minLength={2} /></label>
      <label>Specialization<input value={form.specialization} onChange={set("specialization")} required minLength={2} /></label>
      <label>Department<input value={form.department} onChange={set("department")} /></label>
      <label>Bio<textarea rows={2} value={form.bio} onChange={set("bio")} /></label>
      <label>Slot length (minutes)<input type="number" min={5} max={240} value={form.slot_minutes} onChange={set("slot_minutes")} required /></label>
      <button className="btn">Add doctor</button>
    </form>
  );
}
