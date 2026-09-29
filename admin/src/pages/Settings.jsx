import { useState } from "react";
import { api } from "../api.js";

export default function Settings() {
  const [commission, setCommission] = useState(0.08);
  const [msg, setMsg] = useState("");

  const save = async () => {
    await api("/admin/settings/commission_rate", {
      method: "PUT",
      body: JSON.stringify({ value: { rate: Number(commission) } }),
    });
    setMsg("Enregistré");
  };

  return (
    <>
      <h2>Paramètres de la plateforme</h2>
      <label>Taux de commission (0.05 – 0.10)&nbsp;
        <input type="number" step="0.01" value={commission} onChange={(e) => setCommission(e.target.value)} />
      </label>
      <button onClick={save}>Enregistrer</button> {msg}
      {/* TODO: tarifs de livraison, zones de couverture, campagnes promotionnelles */}
    </>
  );
}
