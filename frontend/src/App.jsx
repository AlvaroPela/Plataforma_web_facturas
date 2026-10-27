import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import RutaProtegida from "./components/RutaProtegida";
import Login from "./pages/Login";
import Inicio from "./pages/Inicio";
import EnConstruccion from "./pages/EnConstruccion";
import { OPCIONES_MENU } from "./config/menu";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/recuperar" element={<EnConstruccion titulo="Recuperar contraseña" />} />
          <Route path="/" element={<RutaProtegida><Inicio /></RutaProtegida>} />

          {/* Cada opción del menú queda protegida por rol desde ya */}
          {OPCIONES_MENU.map((o) => (
            <Route key={o.ruta} path={o.ruta}
              element={<RutaProtegida roles={o.roles}><EnConstruccion titulo={o.texto} /></RutaProtegida>} />
          ))}

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
