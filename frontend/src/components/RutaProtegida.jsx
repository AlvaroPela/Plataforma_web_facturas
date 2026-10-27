// Envuelve las pantallas privadas: si no hay sesión, redirige al login.
// OJO: esto solo mejora la experiencia. La seguridad real está en el backend
// (requiere_roles), porque cualquiera puede manipular el código del navegador.
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RutaProtegida({ children, roles }) {
  const { usuario, cargando } = useAuth();

  if (cargando) return <p className="aviso-pagina">Cargando…</p>;
  if (!usuario) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(usuario.rol)) {
    return <p className="aviso-pagina">No tiene permisos para acceder a esta opción</p>;
  }
  return children;
}
