//! DrenIE 3.1.0 · motor de la red de cunetas (página «Red de cunetas»).
//! El motor va instalado junto al programa (recursos/motor/drenie-motor.exe). Solo se aceptan sus órdenes conocidas, cada
//! llamada pasa por la licencia y lleva una ficha de sesión firmada: el motor no trabaja si no lo llama DrenIE.
use sha2::{Digest, Sha256};
use std::io::Write;
use std::process::{Command, Stdio};
use tauri::Manager;
use tauri_plugin_dialog::DialogExt;

use crate::licensing;

// Misma clave que drenie_motor/__main__.py (_CLAVE_SESION).
const CLAVE_SESION: [u8; 32] = [
    0x5d, 0x0e, 0x9b, 0x3a, 0x7c, 0x41, 0xf2, 0x6e, 0x8a, 0x19, 0xd4, 0xc0, 0x7b, 0x3e, 0x52, 0xf1,
    0xa6, 0xc9, 0x8d, 0x2e, 0x40, 0xb7, 0x1f, 0x53, 0xc8, 0xe6, 0xa2, 0x9d, 0x10, 0x47, 0xfb, 0x3c,
];
// orden -> (argumentos mínimos, máximos, lleva JSON por la entrada estándar, permiso)
// Permiso DEMO: también la edición demo (leer el plano, crear el proyecto, dibujar). EXPORTAR: licencia con el módulo export
// (calcular la red y generar los entregables).
const DEMO: &str = "demo";
const EXPORTAR: &str = "export";
const ORDENES: &[(&str, usize, usize, bool, &str)] = &[
    ("capas", 1, 1, false, DEMO),
    ("crear", 0, 0, true, DEMO),
    ("vista", 1, 1, false, DEMO),
    ("leer", 1, 1, false, DEMO),
    ("ediciones", 1, 1, true, DEMO),
    ("datos", 1, 1, true, DEMO),
    ("disenar", 1, 1, false, EXPORTAR),
    ("aplicar", 3, 3, false, EXPORTAR),
    ("entregables", 1, 1, false, DEMO),
    ("abrir", 1, 2, false, DEMO),
    ("normas", 0, 0, false, DEMO),
    ("para_drenie", 1, 1, false, EXPORTAR),
    ("ubicacion", 1, 1, true, DEMO),
    ("pisco", 0, 0, true, DEMO),
];

fn permiso(app: &tauri::AppHandle, clase: &str) -> Result<(), String> {
    if clase == DEMO { licensing::authorize_feature(app.clone(), "calculate".into(), 0, 0) } else { licensing::require_feature(app, clase) }
}
const ENTRADA_MAX: usize = 20 * 1024 * 1024;

fn hmac_sha256(clave: &[u8], mensaje: &[u8]) -> [u8; 32] {
    let mut k = [0u8; 64];
    k[..clave.len()].copy_from_slice(clave);
    let (mut ipad, mut opad) = ([0x36u8; 64], [0x5cu8; 64]);
    for i in 0..64 { ipad[i] ^= k[i]; opad[i] ^= k[i]; }
    let interno = Sha256::new().chain_update(ipad).chain_update(mensaje).finalize();
    Sha256::new().chain_update(opad).chain_update(interno).finalize().into()
}

fn ficha() -> Result<String, String> {
    let ts = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_err(|e| e.to_string())?.as_secs().to_string();
    let firma: String = hmac_sha256(&CLAVE_SESION, ts.as_bytes()).iter().map(|b| format!("{b:02x}")).collect();
    Ok(format!("{ts}.{firma}"))
}

fn ejecutable(app: &tauri::AppHandle) -> Result<std::path::PathBuf, String> {
    let ruta = app.path().resource_dir().map_err(|e| e.to_string())?.join("motor").join("drenie-motor.exe");
    if ruta.is_file() { Ok(ruta) } else { Err("No se encuentra el motor de la red de cunetas. Instale nuevamente DrenIE.".into()) }
}

fn argumento_valido(a: &str) -> bool {
    !a.is_empty() && a.len() <= 4096 && !a.contains('\0') && !a.starts_with('-')
}

#[tauri::command]
pub async fn motor_red(app: tauri::AppHandle, accion: String, args: Vec<String>, entrada: Option<String>) -> Result<String, String> {
    let Some(&(_, minimo, maximo, con_entrada, clase)) = ORDENES.iter().find(|o| o.0 == accion) else {
        return Err("Orden no permitida.".into());
    };
    if args.len() < minimo || args.len() > maximo || !args.iter().all(|a| argumento_valido(a)) {
        return Err("Datos de la orden no válidos.".into());
    }
    let entrada = if con_entrada { entrada.unwrap_or_default() } else { String::new() };
    if entrada.len() > ENTRADA_MAX { return Err("Los datos enviados al motor exceden 20 MB.".into()); }
    permiso(&app, clase)?;
    let exe = ejecutable(&app)?;
    let sesion = ficha()?;
    tauri::async_runtime::spawn_blocking(move || {
        let mut orden = Command::new(&exe);
        orden.arg(&accion).args(&args)
            .env("DRENIE_SESION", sesion).env("PYTHONIOENCODING", "utf-8").env("PYTHONUTF8", "1")
            .stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
        if let Some(carpeta) = exe.parent() { orden.current_dir(carpeta); }
        #[cfg(target_os = "windows")]
        { use std::os::windows::process::CommandExt; orden.creation_flags(0x0800_0000); } // CREATE_NO_WINDOW
        let mut hijo = orden.spawn().map_err(|e| format!("No se pudo iniciar el motor de la red de cunetas: {e}"))?;
        if let Some(mut stdin) = hijo.stdin.take() {
            stdin.write_all(entrada.as_bytes()).map_err(|e| format!("No se pudo enviar los datos al motor: {e}"))?;
        }
        let salida = hijo.wait_with_output().map_err(|e| e.to_string())?;
        let texto = String::from_utf8_lossy(&salida.stdout).trim().to_owned();
        if texto.starts_with('{') { return Ok(texto); }
        let detalle = String::from_utf8_lossy(&salida.stderr);
        let cola: String = detalle.lines().rev().take(6).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join(" | ");
        Err(format!("El motor de la red de cunetas terminó sin respuesta (código {}). {}", salida.status.code().unwrap_or(-1), cola))
    }).await.map_err(|e| e.to_string())?
}

// Archivos y carpetas siempre elegidos en el diálogo del sistema.
#[tauri::command]
pub async fn motor_elegir(app: tauri::AppHandle, tipo: String) -> Result<Option<String>, String> {
    permiso(&app, DEMO)?;
    tauri::async_runtime::spawn_blocking(move || {
        let dialogo = app.dialog().file();
        let elegido = match tipo.as_str() {
            "dxf" => dialogo.set_title("Plano del local (DXF) — DrenIE").add_filter("Plano DXF", &["dxf"]).blocking_pick_file(),
            "landxml" => dialogo.set_title("Superficie del terreno (LandXML) — DrenIE").add_filter("LandXML", &["xml", "zip"]).blocking_pick_file(),
            "proyecto" => dialogo.set_title("Proyecto de red de cunetas — DrenIE").add_filter("Proyecto de red (proyecto.json)", &["json"]).blocking_pick_file(),
            "carpeta" => dialogo.set_title("Carpeta del proyecto — DrenIE").blocking_pick_folder(),
            "imagen" => dialogo.set_title("Foto aérea del proyecto — DrenIE").add_filter("Imagen (PNG o JPG)", &["png", "jpg", "jpeg"]).blocking_pick_file(),
            _ => return Err("Tipo de archivo no válido.".into()),
        };
        let Some(elegido) = elegido else { return Ok(None) };
        let ruta = elegido.into_path().map_err(|e| e.to_string())?;
        Ok(Some(ruta.to_string_lossy().into_owned()))
    }).await.map_err(|e| e.to_string())?
}

#[cfg(test)]
mod tests {
    use super::*;
    // Vector de RFC 4231, caso 2: clave «Jefe».
    #[test]
    fn hmac_conocido() {
        let r = hmac_sha256(b"Jefe", b"what do ya want for nothing?");
        let hex: String = r.iter().map(|b| format!("{b:02x}")).collect();
        assert_eq!(hex, "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
    }
    #[test]
    fn solo_ordenes_conocidas() {
        assert!(ORDENES.iter().all(|o| o.1 <= o.2 && (o.4 == DEMO || o.4 == EXPORTAR)));
        // con licencia (módulo export): diseñar, aplicar soluciones y pasar la red a CUNETAS / MONTANTES / METRADO
        assert!(ORDENES.iter().filter(|o| o.4 == EXPORTAR).all(|o| o.0 == "disenar" || o.0 == "aplicar" || o.0 == "para_drenie"));
        assert!(["disenar", "aplicar", "para_drenie"].iter().all(|n| ORDENES.iter().any(|o| o.0 == *n && o.4 == EXPORTAR)));
        assert!(!ORDENES.iter().any(|o| o.0 == "lluvia" || o.0 == "cmd"));
        // editor de Ubicación: solo mapas de vista previa, recibe lo editado por la entrada estándar
        assert!(ORDENES.iter().any(|o| o.0 == "ubicacion" && o.1 == 1 && o.2 == 1 && o.3 && o.4 == DEMO));
        // lluvia PISCO-SENAMHI de la pestaña LLUVIA: sin proyecto, recibe el lugar por la entrada estándar
        assert!(ORDENES.iter().any(|o| o.0 == "pisco" && o.1 == 0 && o.2 == 0 && o.3 && o.4 == DEMO));
        assert!(!argumento_valido("--help") && !argumento_valido("") && argumento_valido("C:\\obra\\proyecto.json"));
    }
}
