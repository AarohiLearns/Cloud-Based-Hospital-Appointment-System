import { useState } from "react";
import AddDoctor from "./admin/AddDoctor";
import DoctorAppointments from "./admin/DoctorAppointments";
import ScheduleEditor from "./admin/ScheduleEditor";

const TABS = [
  { key: "appointments", label: "Appointments", Component: DoctorAppointments },
  { key: "schedule", label: "Doctor schedules", Component: ScheduleEditor },
  { key: "add", label: "Add doctor", Component: AddDoctor },
];

export default function Admin() {
  const [tab, setTab] = useState("appointments");
  const Active = TABS.find((t) => t.key === tab).Component;
  return (
    <>
      <h1>Admin dashboard</h1>
      <div className="tabs">
        {TABS.map((t) => (
          <button key={t.key} className={tab === t.key ? "active" : ""} onClick={() => setTab(t.key)}>{t.label}</button>
        ))}
      </div>
      <Active />
    </>
  );
}
