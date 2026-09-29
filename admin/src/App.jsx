import { Link, Navigate, Route, Routes } from "react-router-dom";
import { clearToken, getToken } from "./api.js";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import PendingAccounts from "./pages/PendingAccounts.jsx";
import Disputes from "./pages/Disputes.jsx";
import Settings from "./pages/Settings.jsx";

function Protected({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <>
      {getToken() && (
        <nav>
          <Link to="/">Tableau de bord</Link>
          <Link to="/accounts">Comptes à valider</Link>
          <Link to="/disputes">Litiges</Link>
          <Link to="/settings">Paramètres</Link>
          <a href="/login" onClick={clearToken} style={{ marginLeft: "auto" }}>Déconnexion</a>
        </nav>
      )}
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/accounts" element={<Protected><PendingAccounts /></Protected>} />
          <Route path="/disputes" element={<Protected><Disputes /></Protected>} />
          <Route path="/settings" element={<Protected><Settings /></Protected>} />
        </Routes>
      </main>
    </>
  );
}
