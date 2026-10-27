// Único punto de contacto con el backend. Si mañana cambia la URL o la forma
// de enviar el token, se cambia SOLO aquí.
const API_URL = import.meta.env.VITE_API_URL;
const CLAVE_TOKEN = "facturas_token";

export const guardarToken = (token) => sessionStorage.setItem(CLAVE_TOKEN, token);
export const leerToken = () => sessionStorage.getItem(CLAVE_TOKEN);
export const borrarToken = () => sessionStorage.removeItem(CLAVE_TOKEN);

export async function peticion(ruta, { metodo = "GET", cuerpo } = {}) {
  const encabezados = { "Content-Type": "application/json" };
  const token = leerToken();
  if (token) encabezados.Authorization = `Bearer ${token}`;

  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method: metodo,
      headers: encabezados,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    throw new Error("No hay conexión con el servidor. Verifique que el backend esté encendido.");
  }

  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    // El backend siempre responde { detail: "mensaje de la HU" }
    const error = new Error(datos.detail || "Ocurrió un error inesperado");
    error.estado = respuesta.status;
    throw error;
  }
  return datos;
}
