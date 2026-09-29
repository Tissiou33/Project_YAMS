import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api.js";

// TODO: 2FA obligatoire pour les administrateurs (cahier des charges §6.1)
export default function Login() {
  const [phone, setPhone] = useState("+228");
  const [code, setCode] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const request = async () => {
    try {
      await api("/auth/otp/request", { method: "POST", body: JSON.stringify({ phone }) });
      setSent(true);
      setError("");
    } catch (e) { setError(e.message); }
  };

  const verify = async () => {
    try {
      const t = await api("/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ phone, code, role: "admin" }),
      });
      setToken(t.access_token);
      navigate("/");
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="card" style={{ maxWidth: 360, margin: "80px auto" }}>
      <h2>Administration</h2>
      <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+228…" />
      {!sent ? (
        <button onClick={request}>Recevoir le code</button>
      ) : (
        <>
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Code OTP" />
          <button onClick={verify}>Valider</button>
        </>
      )}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}
