// Contexto de autenticación: guarda "quién está en sesión" y lo comparte
// con todas las pantallas sin tener que pasarlo de componente en componente.
import { createContext, useContext, useEffect, useState } from "react";
import { borrarToken, guardarToken, leerToken, peticion } from "../api/cliente";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  // Al abrir o recargar la página: si hay token guardado, se valida con /auth/yo
  useEffect(() => {
    if (!leerToken()) {
      setCargando(false);
      return;
    }
    peticion("/auth/yo")
      .then(setUsuario)
      .catch(() => borrarToken())
      .finally(() => setCargando(false));
  }, []);

  const iniciarSesion = (respuesta) => {
    guardarToken(respuesta.access_token);
    setUsuario(respuesta.usuario);
  };

  const cerrarSesion = () => {
    borrarToken();
    setUsuario(null);
  };

  return (
    <AuthContext.Provider value={{ usuario, cargando, iniciarSesion, cerrarSesion }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
