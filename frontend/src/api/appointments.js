import { request } from "./client";

export const bookAppointment = (data) => request("/appointments", { method: "POST", body: data });
export const myAppointments = () => request("/appointments/me");
export const doctorAppointments = (doctor_id, date) => request("/appointments", { params: { doctor_id, date } });
export const cancelAppointment = (id) => request(`/appointments/${id}/cancel`, { method: "POST" });
export const completeAppointment = (id) => request(`/appointments/${id}/complete`, { method: "POST" });
/*appointments.js is an API helper file for appointment-related operations.*/