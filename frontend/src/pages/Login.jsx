// HU1 - Iniciar sesión. Tiene dos pasos dentro de la misma pantalla:
//   paso "credenciales": correo + contraseña + código
//   paso "vincular": primer ingreso, muestra el QR y pide el primer código
import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { peticion } from "../api/cliente";
import { useAuth } from "../context/AuthContext";

const PATRON_CORREO = /^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/;
const PATRON_CODIGO = /^\d{6}$/;
const MSG_CODIGO = "Código de verificación inválido o vencido";

export default function Login() {
  const { usuario, iniciarSesion } = useAuth();
  const navegar = useNavigate();

  const [paso, setPaso] = useState("credenciales");
  const [form, setForm] = useState({ correo: "", contrasena: "", codigo: "" });
  const [errores, setErrores] = useState({});
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [vinculacion, setVinculacion] = useState(null); // { token, qr, secreto }
  const [codigoNuevo, setCodigoNuevo] = useState("");

  if (usuario) return <Navigate to="/" replace />;

  const cambiar = (e) => {
    const { name, value } = e.target;
    // El código solo admite números: se filtra mientras se escribe
    const limpio = name === "codigo" ? value.replace(/\D/g, "").slice(0, 6) : value;
    setForm({ ...form, [name]: limpio });
    setErrores({ ...errores, [name]: "" });
  };

  // Validación en el navegador: mismos mensajes que la HU (el backend repite la validación)
  const validar = () => {
    const e = {};
    if (!form.correo.trim()) e.correo = "Campo obligatorio";
    else if (!PATRON_CORREO.test(form.correo.trim())) e.correo = "Verificar correo";
    if (!form.contrasena) e.contrasena = "Campo obligatorio";
    if (form.codigo && !PATRON_CODIGO.test(form.codigo)) e.codigo = MSG_CODIGO;
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const entrar = (respuesta) => {
    iniciarSesion(respuesta);
    navegar("/", { replace: true });
  };

  const enviarCredenciales = async (e) => {
    e.preventDefault();
    setMensaje("");
    if (!validar()) return;
    setEnviando(true);
    try {
      const respuesta = await peticion("/auth/login", {
        metodo: "POST",
        cuerpo: {
          correo: form.correo.trim(),
          contrasena: form.contrasena,
          codigo: form.codigo || null,
        },
      });
      if (respuesta.estado === "configurar_2fa") {
        setVinculacion({ token: respuesta.token_configuracion, qr: respuesta.qr, secreto: respuesta.secreto });
        setPaso("vincular");
      } else {
        entrar(respuesta);
      }
    } catch (error) {
      setMensaje(error.message);
    } finally {
      setEnviando(false);
    }
  };

  const enviarVinculacion = async (e) => {
    e.preventDefault();
    setMensaje("");
    if (!PATRON_CODIGO.test(codigoNuevo)) {
      setMensaje(MSG_CODIGO);
      return;
    }
    setEnviando(true);
    try {
      const respuesta = await peticion("/auth/2fa/activar", {
        metodo: "POST",
        cuerpo: { token_configuracion: vinculacion.token, codigo: codigoNuevo },
      });
      entrar(respuesta);
    } catch (error) {
      setMensaje(error.message);
    } finally {
      setEnviando(false);
    }
  };

  const volver = () => {
    setPaso("credenciales");
    setVinculacion(null);
    setCodigoNuevo("");
    setMensaje("");
  };

  return (
    <main className="login">
      <section className="login-marca" aria-hidden="true">
        <p className="login-empresa">ZeroBugs Solutions</p>
        <h1 className="login-titulo">Facturas</h1>
        <p className="login-lema">Registro, validación y consulta de facturas en un solo lugar.</p>
      </section>

      <section className="login-panel">
        {paso === "credenciales" ? (
          <form onSubmit={enviarCredenciales} noValidate className="formulario">
            <h2>Iniciar sesión</h2>

            <Campo etiqueta="Correo electrónico" error={errores.correo}>
              <input name="correo" type="email" autoComplete="username"
                value={form.correo} onChange={cambiar} aria-invalid={!!errores.correo} />
            </Campo>

            <Campo etiqueta="Contraseña" error={errores.contrasena}>
              <input name="contrasena" type="password" autoComplete="current-password"
                value={form.contrasena} onChange={cambiar} aria-invalid={!!errores.contrasena} />
            </Campo>

            <Campo etiqueta="Código de verificación" error={errores.codigo}
              ayuda="Los 6 dígitos de su app Authenticator. En su primer ingreso déjelo vacío.">
              <input name="codigo" inputMode="numeric" autoComplete="one-time-code"
                value={form.codigo} onChange={cambiar} aria-invalid={!!errores.codigo}
                className="input-codigo" placeholder="000000" />
            </Campo>

            {mensaje && <p className="mensaje-error" role="alert">{mensaje}</p>}

            <button type="submit" className="boton" disabled={enviando}>
              {enviando ? "Verificando…" : "Ingresar"}
            </button>
            <Link to="/recuperar" className="enlace">¿Olvidó su contraseña?</Link>
          </form>
        ) : (
          <form onSubmit={enviarVinculacion} noValidate className="formulario">
            <h2>Vincule su app de verificación</h2>
            <p className="texto">
              Es su primer ingreso. Abra Google Authenticator o Microsoft Authenticator,
              escanee este código y escriba los 6 dígitos que aparecen.
            </p>
            <img src={vinculacion.qr} alt="Código QR para vincular la cuenta" className="qr" />
            <details className="texto">
              <summary>No puedo escanear el código</summary>
              <p>Ingrese esta clave manualmente en la app:</p>
              <code className="secreto">{vinculacion.secreto}</code>
            </details>

            <Campo etiqueta="Código de verificación">
              <input inputMode="numeric" autoComplete="one-time-code" className="input-codigo"
                value={codigoNuevo} placeholder="000000"
                onChange={(e) => setCodigoNuevo(e.target.value.replace(/\D/g, "").slice(0, 6))} />
            </Campo>

            {mensaje && <p className="mensaje-error" role="alert">{mensaje}</p>}

            <button type="submit" className="boton" disabled={enviando}>
              {enviando ? "Verificando…" : "Vincular e ingresar"}
            </button>
            <button type="button" className="enlace" onClick={volver}>Volver</button>
          </form>
        )}
      </section>
    </main>
  );
}

function Campo({ etiqueta, error, ayuda, children }) {
  return (
    <label className="campo">
      <span className="campo-etiqueta">{etiqueta}</span>
      {children}
      {error ? <span className="campo-error">{error}</span> : ayuda && <span className="campo-ayuda">{ayuda}</span>}
    </label>
  );
}
