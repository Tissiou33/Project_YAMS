import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Disputes() {
  const [rows, setRows] = useState([]);
  useEffect(() => { api("/admin/disputes").then(setRows); }, []);
  return (
    <>
      <h2>Litiges ouverts</h2>
      <table>
        <thead><tr><th>Commande</th><th>Motif</th><th>Statut</th></tr></thead>
        <tbody>
          {rows.map((d) => (<tr key={d.id}><td>{d.order_id}</td><td>{d.reason}</td><td>{d.status}</td></tr>))}
        </tbody>
      </table>
      {/* TODO: historique horodaté de la commande, décision d'arbitrage (remboursement, sanction) */}
    </>
  );
}
