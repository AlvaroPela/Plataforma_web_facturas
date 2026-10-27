// Opciones del menú por rol (diagrama de roles + HU1: "muestra las opciones
// correspondientes al rol"). Las rutas se irán construyendo sprint a sprint.
export const NOMBRES_ROL = {
  administrador: "Administrador",
  auxiliar_contable: "Auxiliar contable",
  contador: "Contador",
  consulta: "Consulta",
};

const TODOS = ["administrador", "auxiliar_contable", "contador", "consulta"];

export const OPCIONES_MENU = [
  { ruta: "/usuarios/nuevo", texto: "Crear usuario", detalle: "Registrar personas y asignarles un rol", roles: ["administrador"] },
  { ruta: "/usuarios", texto: "Gestionar usuarios", detalle: "Cambiar correo, rol o estado", roles: ["administrador"] },
  { ruta: "/facturas/cargar", texto: "Cargar facturas", detalle: "Subir hasta 3 archivos PDF o imagen", roles: ["auxiliar_contable", "contador"] },
  { ruta: "/alertas", texto: "Revisar alertas", detalle: "Facturas con datos incompletos o inválidos", roles: ["auxiliar_contable", "contador"] },
  { ruta: "/facturas/aprobar", texto: "Aprobar o rechazar", detalle: "Dejar como definitivas las facturas procesadas", roles: ["contador"] },
  { ruta: "/facturas", texto: "Consultar historial", detalle: "Buscar facturas por NIT, número, fecha o estado", roles: TODOS },
  { ruta: "/auditoria", texto: "Auditoría", detalle: "Quién cargó, corrigió o aprobó cada factura", roles: ["administrador", "contador"] },
  { ruta: "/perfil", texto: "Cambiar mi contraseña", detalle: "Actualizar su clave con el código de verificación", roles: TODOS },
];

export const opcionesPara = (rol) => OPCIONES_MENU.filter((o) => o.roles.includes(rol));
