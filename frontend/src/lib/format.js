import { CLINIC_TZ } from "../config";

export const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export const formatTime = (iso, tz = CLINIC_TZ) =>
  new Date(iso).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: tz });

export const formatDateTime = (iso, tz = CLINIC_TZ) =>
  new Date(iso).toLocaleString("en-IN", {
    weekday: "short", day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", timeZone: tz,
  });

// Today's date (YYYY-MM-DD) in the clinic's timezone.
export const todayISO = (tz = CLINIC_TZ) => new Date().toLocaleDateString("en-CA", { timeZone: tz });

export const addDaysISO = (isoDate, days) => {
  const d = new Date(`${isoDate}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
};
