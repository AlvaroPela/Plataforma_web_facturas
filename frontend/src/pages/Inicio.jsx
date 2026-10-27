// Pantalla principal después del login: muestra solo las opciones del rol (HU1).
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { NOMBRES_ROL, opcionesPara } from "../config/menu";

export default function Inicio() {
  const { usuario, cerrarSesion } = useAuth();
  const opciones = opcionesPara(usuario.rol);

  return (
    <div className="inicio">
      <header className="barra">
        <span className="barra-marca">Facturas</span>
        <div className="barra-usuario">
          <span>{usuario.nombre} <small>{NOMBRES_ROL[usuario.rol]}</small></span>
          <button type="button" className="boton-secundario" onClick={cerrarSesion}>Cerrar sesión</button>
        </div>
      </header>

      <main className="inicio-contenido">
        <h1>Hola, {usuario.nombre.split(" ")[0]}</h1>
        <p className="texto">Estas son las opciones disponibles para su rol.</p>
        <ul className="menu">
          {opciones.map((o) => (
            <li key={o.ruta}>
              <Link to={o.ruta} className="menu-opcion">
                <span className="menu-texto">{o.texto}</span>
                <span className="menu-detalle">{o.detalle}</span>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
