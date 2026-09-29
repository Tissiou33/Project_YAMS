import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  useEffect(() => { api("/admin/stats").then(setStats).catch(() => setStats(null)); }, []);
  if (!stats) return <p>Chargement…</p>;
  return (
    <>
      <h2>Tableau de bord</h2>
      <div className="cards">
        <div className="card"><b>{stats.orders}</b><br />Commandes</div>
        <div className="card"><b>{stats.delivered}</b><br />Livrées</div>
        <div className="card"><b>{stats.commission_fcfa} FCFA</b><br />Commissions</div>
      </div>
      {/* TODO: délai moyen par région, carte d'activité, taux de livraison réussie */}
    </>
  );
}
