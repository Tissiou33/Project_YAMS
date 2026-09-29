import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function PendingAccounts() {
  const [rows, setRows] = useState([]);
  const load = () => api("/admin/accounts/pending").then(setRows);
  useEffect(() => { load(); }, []);

  const act = async (id, action) => {
    await api(`/admin/accounts/${id}/${action}`, { method: "POST" });
    load();
  };

  return (
    <>
      <h2>Comptes en attente de validation (KYC)</h2>
      <table>
        <thead><tr><th>Téléphone</th><th>Rôle</th><th>KYC</th><th /></tr></thead>
        <tbody>
          {rows.map((u) => (
            <tr key={u.id}>
              <td>{u.phone}</td><td>{u.role}</td><td>{u.kyc_status}</td>
              <td>
                {/* TODO: visualiser les pièces justificatives avant décision */}
                <button onClick={() => act(u.id, "approve")}>Valider</button>
                <button onClick={() => act(u.id, "reject")}>Rejeter</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
