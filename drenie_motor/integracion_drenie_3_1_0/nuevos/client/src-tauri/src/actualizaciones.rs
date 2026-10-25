//! Actualizaciones automáticas firmadas (tauri-plugin-updater).
//!
//! DrenIE consulta `latest.json` en la dirección de `plugins.updater.endpoints` (tauri.conf.json) y solo instala un instalador
//! cuya firma corresponde a la clave pública de `plugins.updater.pubkey`. La clave privada la tiene únicamente el propietario
//! (GENERAR_CLAVE_ACTUALIZACIONES.ps1); sin clave pública configurada el programa no busca actualizaciones.

use serde::Serialize;
use tauri::AppHandle;
use tauri_plugin_updater::UpdaterExt;

#[derive(Serialize)]
pub struct Novedad {
    pub disponible: bool,
    pub version: String,
    pub actual: String,
    pub notas: String,
    pub fecha: String,
}

fn configurada(app: &AppHandle) -> bool {
    let u = app.config().plugins.0.get("updater");
    let clave = u.and_then(|u| u.get("pubkey")).and_then(|p| p.as_str()).map(|p| !p.trim().is_empty()).unwrap_or(false);
    let destino = u.and_then(|u| u.get("endpoints")).and_then(|e| e.as_array()).map(|e| !e.is_empty()).unwrap_or(false);
    clave && destino
}

async fn consultar(app: &AppHandle) -> Result<Option<tauri_plugin_updater::Update>, String> {
    if !configurada(app) {
        return Err("Las actualizaciones automáticas no están configuradas en esta versión de DrenIE.".into());
    }
    let buscador = app.updater().map_err(|e| format!("No se pudo preparar la búsqueda de actualizaciones ({e})."))?;
    buscador
        .check()
        .await
        .map_err(|e| format!("No se pudo consultar si hay una versión nueva. Revise su conexión a internet ({e})."))
}

#[tauri::command]
pub async fn buscar_actualizacion(app: AppHandle) -> Result<Novedad, String> {
    let actual = app.package_info().version.to_string();
    Ok(match consultar(&app).await? {
        Some(u) => Novedad {
            disponible: true,
            version: u.version.clone(),
            actual,
            notas: u.body.clone().unwrap_or_default(),
            fecha: u.date.map(|d| d.date().to_string()).unwrap_or_default(),
        },
        None => Novedad { disponible: false, version: actual.clone(), actual, notas: String::new(), fecha: String::new() },
    })
}

/// Descarga, comprueba la firma e instala; luego reinicia DrenIE (en Windows el instalador cierra el programa).
#[tauri::command]
pub async fn instalar_actualizacion(app: AppHandle) -> Result<(), String> {
    let Some(u) = consultar(&app).await? else {
        return Err("Ya tiene la última versión de DrenIE.".into());
    };
    u.download_and_install(|_, _| {}, || {})
        .await
        .map_err(|e| format!("No se pudo instalar la actualización; DrenIE sigue como estaba ({e})."))?;
    app.restart();
}
