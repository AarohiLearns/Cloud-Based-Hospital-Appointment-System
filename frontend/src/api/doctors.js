import { request } from "./client";

export const listDoctors = (params) => request("/doctors", { params: { limit: 100, ...params } });
export const getDoctor = (id) => request(`/doctors/${id}`);
export const getAvailability = (id, date) => request(`/doctors/${id}/availability`, { params: { date } });
export const createDoctor = (data) => request("/doctors", { method: "POST", body: data });
export const setSchedule = (id, entries) =>
  request(`/doctors/${id}/schedule`, { method: "PUT", body: { entries } });
