# -*- coding: utf-8 -*-
"""Llena el índice (tabla de contenido) de un Word para imprimir: abre el documento con LibreOffice (UNO), actualiza sus índices
y lo guarda en el mismo .docx. El índice queda con sus títulos y números de página; se conserva la orden de Word de actualizar
los campos al abrir (updateFields), para que Word recalcule los números con su propia paginación.

Uso: python3 herramientas/indice_word.py <archivo.docx> [<archivo2.docx> ...]
     o desde Python: indice_word.llenar([rutas])
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

PUERTO = 2101


def _pv(n, v):
    from com.sun.star.beans import PropertyValue
    p = PropertyValue(); p.Name = n; p.Value = v
    return p


def _update_fields(ruta):
    """Asegura <w:updateFields w:val="true"/> en word/settings.xml (LibreOffice no lo conserva)."""
    tmp = ruta + '.tmp'
    with zipfile.ZipFile(ruta) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == 'word/settings.xml' and b'updateFields' not in data:
                data = data.replace(b'</w:settings>', b'<w:updateFields w:val="true"/></w:settings>')
            zout.writestr(it, data)
    os.replace(tmp, ruta)


def llenar(rutas):
    import uno
    perfil = tempfile.mkdtemp()
    proc = subprocess.Popen(['soffice', '--headless', '--invisible', '--norestore', '-env:UserInstallation=file://' + perfil,
                             '--accept=socket,host=localhost,port=%d;urp;' % PUERTO], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ctx = None
        for _ in range(90):
            try:
                local = uno.getComponentContext()
                res = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
                ctx = res.resolve('uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext' % PUERTO); break
            except Exception:
                time.sleep(1)
        desk = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
        for ruta in rutas:
            ruta = os.path.abspath(ruta)
            tmp = ruta + '.lo.docx'
            doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(ruta), '_blank', 0, (_pv('Hidden', True),))
            idx = doc.getDocumentIndexes()
            for i in range(idx.getCount()):
                idx.getByIndex(i).update()
            doc.storeToURL(uno.systemPathToFileUrl(tmp), (_pv('FilterName', 'MS Word 2007 XML'),))
            doc.close(True)
            shutil.move(tmp, ruta)
            _update_fields(ruta)
    finally:
        proc.terminate()
        shutil.rmtree(perfil, ignore_errors=True)
    return rutas


if __name__ == '__main__':
    for r in llenar(sys.argv[1:]):
        print(r)
