import { useEffect, useState } from "react";
import { listDoctors } from "../api/doctors";

/** Dropdown of doctors; reports the full doctor object to the parent. */
export default function DoctorPicker({ value, onChange, refreshKey = 0 }) {
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    listDoctors().then(setDoctors).catch(() => setDoctors([]));
  }, [refreshKey]);

  return (
    <select value={value || ""} onChange={(e) => onChange(doctors.find((d) => d.id === e.target.value) || null)}>
      <option value="">Select a doctor...</option>
      {doctors.map((d) => (
        <option key={d.id} value={d.id}>{d.full_name} - {d.specialization}</option>
      ))}
    </select>
  );
}
