import { request } from "./client";

export const register = (data) => request("/auth/register", { method: "POST", body: data });
export const login = (email, password) =>
  request("/auth/login", { method: "POST", form: { username: email, password } });
export const getMe = () => request("/users/me");
