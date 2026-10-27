// Pantalla temporal para las opciones que se construyen en sprints siguientes.
import { Link } from "react-router-dom";

export default function EnConstruccion({ titulo }) {
  return (
    <main className="aviso-pagina">
      <h1>{titulo}</h1>
      <p>Esta opción se construye en un próximo sprint.</p>
      <Link to="/" className="enlace">Volver al inicio</Link>
    </main>
  );
}
