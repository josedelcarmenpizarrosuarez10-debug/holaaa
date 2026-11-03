DATOS_JSON = r'''{"edificios":[{"cod":"E-01","nombre":"ADMINISTRACIÓN","techo":[12.3,24.8,33.1,50.2],"cumbrera":"y","muro":[13.8,26.3,31.6,48.7],"piso":[12.6,25.1,32.8,49.9],"lados":[[13.8,26.3,31.6,26.3,0,-1],[13.8,48.7,31.6,48.7,0,1],[13.8,26.3,13.8,48.7,-1,0],[31.6,26.3,31.6,48.7,1,0]],"vanos":[{"lado":0,"x":15.58,"y":26.3,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":0,"x":19.14,"y":26.3,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":0,"x":22.7,"y":26.3,"tipo":"puerta","ancho":1.8,"alto":2.35,"alf":0.15,"vidrio":true},{"lado":0,"x":26.26,"y":26.3,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":0,"x":29.82,"y":26.3,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":1,"x":15.58,"y":48.7,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":1,"x":19.14,"y":48.7,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":1,"x":22.7,"y":48.7,"tipo":"puerta","ancho":1.8,"alto":2.35,"alf":0.15,"vidrio":true},{"lado":1,"x":26.26,"y":48.7,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":1,"x":29.82,"y":48.7,"tipo":"ventana","ancho":1.78,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":28.167,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":31.9,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":13.8,"y":35.633,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":39.367,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":43.1,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":13.8,"y":46.833,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":3,"x":31.6,"y":28.167,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":3,"x":31.6,"y":31.9,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":31.6,"y":35.633,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":3,"x":31.6,"y":39.367,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05},{"lado":3,"x":31.6,"y":43.1,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":31.6,"y":46.833,"tipo":"ventana","ancho":2.165,"alto":1.35,"alf":1.05}],"columnas":[[17.36,26.3],[24.48,26.3],[31.6,26.3],[31.6,30.033],[28.04,26.3],[13.8,33.767],[20.92,26.3],[31.6,33.767],[13.8,37.5],[31.6,44.967],[31.6,37.5],[13.8,41.233],[13.8,48.7],[20.92,48.7],[31.6,41.233],[17.36,48.7],[13.8,44.967],[24.48,48.7],[31.6,48.7],[28.04,48.7],[13.8,26.3],[13.8,30.033]],"hastiales":[[[13.8,26.3,3.75],[22.7,26.3,6.242],[31.6,26.3,3.75]],[[13.8,48.7,3.75],[22.7,48.7,6.242],[31.6,48.7,3.75]]],"alero":3.33},{"cod":"E-02","nombre":"","techo":[43.8,41.4,54.1,55.8],"cumbrera":"y","muro":[45.3,42.9,52.6,54.3],"piso":[44.1,41.7,53.8,55.5],"lados":[[45.3,42.9,52.6,42.9,0,-1],[45.3,54.3,52.6,54.3,0,1],[45.3,42.9,45.3,54.3,-1,0],[52.6,42.9,52.6,54.3,1,0]],"vanos":[{"lado":0,"x":47.125,"y":42.9,"tipo":"ventana","ancho":1.825,"alto":1.35,"alf":1.05},{"lado":0,"x":50.775,"y":42.9,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":1,"x":47.125,"y":54.3,"tipo":"ventana","ancho":1.825,"alto":1.35,"alf":1.05},{"lado":1,"x":50.775,"y":54.3,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":2,"x":45.3,"y":44.8,"tipo":"ventana","ancho":2.204,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":48.6,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":45.3,"y":52.4,"tipo":"ventana","ancho":2.204,"alto":1.35,"alf":1.05},{"lado":3,"x":52.6,"y":44.8,"tipo":"ventana","ancho":2.204,"alto":1.35,"alf":1.05},{"lado":3,"x":52.6,"y":48.6,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":52.6,"y":52.4,"tipo":"ventana","ancho":2.204,"alto":1.35,"alf":1.05}],"columnas":[[45.3,54.3],[52.6,50.5],[52.6,54.3],[45.3,50.5],[48.95,42.9],[45.3,42.9],[45.3,46.7],[52.6,42.9],[52.6,46.7],[48.95,54.3]],"hastiales":[[[45.3,42.9,3.75],[48.95,42.9,4.772],[52.6,42.9,3.75]],[[45.3,54.3,3.75],[48.95,54.3,4.772],[52.6,54.3,3.75]]],"alero":3.33},{"cod":"E-03","nombre":"","techo":[43.8,31.0,61.1,39.8],"cumbrera":"x","muro":[45.3,32.5,59.6,38.3],"piso":[44.1,31.3,60.8,39.5],"lados":[[45.3,32.5,59.6,32.5,0,-1],[45.3,38.3,59.6,38.3,0,1],[45.3,32.5,45.3,38.3,-1,0],[59.6,32.5,59.6,38.3,1,0]],"vanos":[{"lado":0,"x":47.087,"y":32.5,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":0,"x":50.663,"y":32.5,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":0,"x":54.237,"y":32.5,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":0,"x":57.812,"y":32.5,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":1,"x":47.087,"y":38.3,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":1,"x":50.663,"y":38.3,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":1,"x":54.237,"y":38.3,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":1,"x":57.812,"y":38.3,"tipo":"ventana","ancho":2.074,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":33.95,"tipo":"ventana","ancho":1.45,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":36.85,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":3,"x":59.6,"y":33.95,"tipo":"ventana","ancho":1.45,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":36.85,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false}],"columnas":[[45.3,38.3],[59.6,35.4],[56.025,32.5],[52.45,32.5],[48.875,38.3],[45.3,32.5],[59.6,38.3],[48.875,32.5],[56.025,38.3],[45.3,35.4],[59.6,32.5],[52.45,38.3]],"hastiales":[[[45.3,32.5,3.75],[45.3,35.4,4.562],[45.3,38.3,3.75]],[[59.6,32.5,3.75],[59.6,35.4,4.562],[59.6,38.3,3.75]]],"alero":3.33},{"cod":"E-04","nombre":"","techo":[12.3,50.6,26.1,88.7],"cumbrera":"y","muro":[13.8,52.1,24.6,87.2],"piso":[12.6,50.9,25.8,88.4],"lados":[[13.8,52.1,24.6,52.1,0,-1],[13.8,87.2,24.6,87.2,0,1],[13.8,52.1,13.8,87.2,-1,0],[24.6,52.1,24.6,87.2,1,0]],"vanos":[{"lado":0,"x":15.6,"y":52.1,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":0,"x":19.2,"y":52.1,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":0,"x":22.8,"y":52.1,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":1,"x":15.6,"y":87.2,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":1,"x":19.2,"y":87.2,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":1,"x":22.8,"y":87.2,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":53.855,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":57.365,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":13.8,"y":60.875,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":64.385,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":67.895,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":13.8,"y":71.405,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":74.915,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":78.425,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":13.8,"y":81.935,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":13.8,"y":85.445,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":53.855,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":57.365,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":24.6,"y":60.875,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":64.385,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":67.895,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":24.6,"y":71.405,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":74.915,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":78.425,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":24.6,"y":81.935,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":24.6,"y":85.445,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05}],"columnas":[[24.6,69.65],[24.6,59.12],[24.6,66.14],[24.6,62.63],[24.6,55.61],[13.8,83.69],[21.0,52.1],[24.6,87.2],[24.6,73.16],[24.6,76.67],[17.4,52.1],[13.8,52.1],[24.6,83.69],[13.8,80.18],[13.8,66.14],[21.0,87.2],[13.8,69.65],[13.8,59.12],[13.8,55.61],[13.8,62.63],[17.4,87.2],[24.6,52.1],[13.8,87.2],[13.8,76.67],[13.8,73.16],[24.6,80.18]],"hastiales":[[[13.8,52.1,3.75],[19.2,52.1,5.262],[24.6,52.1,3.75]],[[13.8,87.2,3.75],[19.2,87.2,5.262],[24.6,87.2,3.75]]],"alero":3.33},{"cod":"E-05","nombre":"SUM","techo":[43.8,56.4,61.1,88.7],"cumbrera":"y","muro":[45.3,57.9,59.6,87.2],"piso":[44.1,56.7,60.8,88.4],"lados":[[45.3,57.9,59.6,57.9,0,-1],[45.3,87.2,59.6,87.2,0,1],[45.3,57.9,45.3,87.2,-1,0],[59.6,57.9,59.6,87.2,1,0]],"vanos":[{"lado":0,"x":47.087,"y":57.9,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":0,"x":50.663,"y":57.9,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":0,"x":54.237,"y":57.9,"tipo":"puerta","ancho":1.8,"alto":2.35,"alf":0.15,"vidrio":true},{"lado":0,"x":57.812,"y":57.9,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":1,"x":47.087,"y":87.2,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":1,"x":50.663,"y":87.2,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":1,"x":54.237,"y":87.2,"tipo":"puerta","ancho":1.8,"alto":2.35,"alf":0.15,"vidrio":true},{"lado":1,"x":57.812,"y":87.2,"tipo":"ventana","ancho":1.788,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":59.731,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":63.394,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":45.3,"y":67.056,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":70.719,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":74.381,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":45.3,"y":78.044,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":81.706,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":2,"x":45.3,"y":85.369,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":59.6,"y":59.731,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":63.394,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":59.6,"y":67.056,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":70.719,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":74.381,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":59.6,"y":78.044,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":81.706,"tipo":"ventana","ancho":2.124,"alto":1.35,"alf":1.05},{"lado":3,"x":59.6,"y":85.369,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15}],"columnas":[[59.6,79.875],[59.6,61.562],[59.6,76.213],[45.3,65.225],[59.6,87.2],[59.6,57.9],[59.6,68.888],[59.6,72.55],[52.45,87.2],[52.45,57.9],[45.3,79.875],[45.3,61.562],[59.6,83.537],[48.875,87.2],[48.875,57.9],[56.025,87.2],[45.3,76.213],[56.025,57.9],[45.3,87.2],[45.3,57.9],[45.3,68.888],[59.6,65.225],[45.3,72.55],[45.3,83.537]],"hastiales":[[[45.3,57.9,3.75],[52.45,57.9,5.752],[59.6,57.9,3.75]],[[45.3,87.2,3.75],[52.45,87.2,5.752],[59.6,87.2,3.75]]],"alero":3.33},{"cod":"E-06","nombre":"","techo":[30.5,91.2,51.3,105.0],"cumbrera":"x","muro":[32.0,92.7,49.8,103.5],"piso":[30.8,91.5,51.0,104.7],"lados":[[32.0,92.7,49.8,92.7,0,-1],[32.0,103.5,49.8,103.5,0,1],[32.0,92.7,32.0,103.5,-1,0],[49.8,92.7,49.8,103.5,1,0]],"vanos":[{"lado":0,"x":33.78,"y":92.7,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":37.34,"y":92.7,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":0,"x":40.9,"y":92.7,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":44.46,"y":92.7,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":48.02,"y":92.7,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":1,"x":33.78,"y":103.5,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":37.34,"y":103.5,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":1,"x":40.9,"y":103.5,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":44.46,"y":103.5,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":48.02,"y":103.5,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":32.0,"y":94.5,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":2,"x":32.0,"y":98.1,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":2,"x":32.0,"y":101.7,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":3,"x":49.8,"y":94.5,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":3,"x":49.8,"y":98.1,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":3,"x":49.8,"y":101.7,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05}],"columnas":[[46.24,103.5],[39.12,103.5],[49.8,96.3],[35.56,92.7],[32.0,96.3],[49.8,103.5],[49.8,92.7],[32.0,103.5],[32.0,92.7],[42.68,103.5],[42.68,92.7],[35.56,103.5],[46.24,92.7],[49.8,99.9],[39.12,92.7],[32.0,99.9]],"hastiales":[[[32.0,92.7,3.75],[32.0,98.1,5.262],[32.0,103.5,3.75]],[[49.8,92.7,3.75],[49.8,98.1,5.262],[49.8,103.5,3.75]]],"alero":3.33},{"cod":"E-08","nombre":"","techo":[30.5,115.5,51.3,129.3],"cumbrera":"x","muro":[32.0,117.0,49.8,127.8],"piso":[30.8,115.8,51.0,129.0],"lados":[[32.0,117.0,49.8,117.0,0,-1],[32.0,127.8,49.8,127.8,0,1],[32.0,117.0,32.0,127.8,-1,0],[49.8,117.0,49.8,127.8,1,0]],"vanos":[{"lado":0,"x":33.78,"y":117.0,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":37.34,"y":117.0,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":0,"x":40.9,"y":117.0,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":44.46,"y":117.0,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":0,"x":48.02,"y":117.0,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":1,"x":33.78,"y":127.8,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":37.34,"y":127.8,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":1,"x":40.9,"y":127.8,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":44.46,"y":127.8,"tipo":"ventana","ancho":2.065,"alto":1.35,"alf":1.05},{"lado":1,"x":48.02,"y":127.8,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":32.0,"y":118.8,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":2,"x":32.0,"y":122.4,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":2,"x":32.0,"y":126.0,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":3,"x":49.8,"y":118.8,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":3,"x":49.8,"y":122.4,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":3,"x":49.8,"y":126.0,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05}],"columnas":[[49.8,117.0],[39.12,127.8],[32.0,117.0],[49.8,120.6],[42.68,117.0],[32.0,120.6],[46.24,117.0],[35.56,117.0],[49.8,127.8],[49.8,124.2],[32.0,127.8],[32.0,124.2],[42.68,127.8],[46.24,127.8],[39.12,117.0],[35.56,127.8]],"hastiales":[[[32.0,117.0,3.75],[32.0,122.4,5.262],[32.0,127.8,3.75]],[[49.8,117.0,3.75],[49.8,122.4,5.262],[49.8,127.8,3.75]]],"alero":3.33},{"cod":"E-07","nombre":"","techo":[54.2,91.2,68.0,129.3],"cumbrera":"y","muro":[55.7,92.7,66.5,127.8],"piso":[54.5,91.5,67.7,129.0],"lados":[[55.7,92.7,66.5,92.7,0,-1],[55.7,127.8,66.5,127.8,0,1],[55.7,92.7,55.7,127.8,-1,0],[66.5,92.7,66.5,127.8,1,0]],"vanos":[{"lado":0,"x":57.5,"y":92.7,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":0,"x":61.1,"y":92.7,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":0,"x":64.7,"y":92.7,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":1,"x":57.5,"y":127.8,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":1,"x":61.1,"y":127.8,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":1,"x":64.7,"y":127.8,"tipo":"ventana","ancho":1.8,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":94.455,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":97.965,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":55.7,"y":101.475,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":104.985,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":108.495,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":55.7,"y":112.005,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":115.515,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":119.025,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":55.7,"y":122.535,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":2,"x":55.7,"y":126.045,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":94.455,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":97.965,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":66.5,"y":101.475,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":104.985,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":108.495,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":66.5,"y":112.005,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":115.515,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":119.025,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":66.5,"y":122.535,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05},{"lado":3,"x":66.5,"y":126.045,"tipo":"ventana","ancho":2.036,"alto":1.35,"alf":1.05}],"columnas":[[55.7,113.76],[55.7,99.72],[55.7,96.21],[66.5,127.8],[62.9,127.8],[66.5,103.23],[55.7,120.78],[66.5,92.7],[55.7,117.27],[55.7,106.74],[62.9,92.7],[66.5,124.29],[66.5,110.25],[66.5,113.76],[66.5,96.21],[55.7,127.8],[66.5,99.72],[59.3,127.8],[55.7,103.23],[66.5,117.27],[66.5,120.78],[66.5,106.74],[59.3,92.7],[55.7,92.7],[55.7,124.29],[55.7,110.25]],"hastiales":[[[55.7,92.7,3.75],[61.1,92.7,5.262],[66.5,92.7,3.75]],[[55.7,127.8,3.75],[61.1,127.8,5.262],[66.5,127.8,3.75]]],"alero":3.33},{"cod":"E-09","nombre":"","techo":[2.0,73.7,10.9,88.5],"cumbrera":"y","muro":[3.5,75.2,9.4,87.0],"piso":[2.3,74.0,10.6,88.2],"lados":[[3.5,75.2,9.4,75.2,0,-1],[3.5,87.0,9.4,87.0,0,1],[3.5,75.2,3.5,87.0,-1,0],[9.4,75.2,9.4,87.0,1,0]],"vanos":[{"lado":0,"x":4.975,"y":75.2,"tipo":"ventana","ancho":1.475,"alto":1.35,"alf":1.05},{"lado":0,"x":7.925,"y":75.2,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":1,"x":4.975,"y":87.0,"tipo":"ventana","ancho":1.475,"alto":1.35,"alf":1.05},{"lado":1,"x":7.925,"y":87.0,"tipo":"puerta","ancho":1.0,"alto":2.35,"alf":0.15,"vidrio":false},{"lado":2,"x":3.5,"y":77.167,"tipo":"ventana","ancho":2.281,"alto":1.35,"alf":1.05},{"lado":2,"x":3.5,"y":81.1,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":2,"x":3.5,"y":85.033,"tipo":"ventana","ancho":2.281,"alto":1.35,"alf":1.05},{"lado":3,"x":9.4,"y":77.167,"tipo":"ventana","ancho":2.281,"alto":1.35,"alf":1.05},{"lado":3,"x":9.4,"y":81.1,"tipo":"puerta","ancho":1.0,"alto":2.15,"alf":0.15},{"lado":3,"x":9.4,"y":85.033,"tipo":"ventana","ancho":2.281,"alto":1.35,"alf":1.05}],"columnas":[[9.4,87.0],[3.5,87.0],[6.45,87.0],[3.5,83.067],[9.4,75.2],[3.5,75.2],[6.45,75.2],[9.4,79.133],[3.5,79.133],[9.4,83.067]],"hastiales":[[[3.5,75.2,3.75],[6.45,75.2,4.576],[9.4,75.2,3.75]],[[3.5,87.0,3.75],[6.45,87.0,4.576],[9.4,87.0,3.75]]],"alero":3.33}],"losa":{"rect":[3.5,92.6,26.6,127.0],"h_col":6.0,"flecha":4.2,"columnas":[[3.5,92.6],[26.6,92.6],[3.5,98.333],[26.6,98.333],[3.5,104.067],[26.6,104.067],[3.5,109.8],[26.6,109.8],[3.5,115.533],[26.6,115.533],[3.5,121.267],[26.6,121.267],[3.5,127.0],[26.6,127.0]]},"oe01":{"gx0":31.3,"gx1":45.1,"yf":16.1,"yb":21.5,"columnas":[[31.441,16.3],[31.441,21.3],[33.388,16.3],[33.388,21.3],[38.295,16.3],[38.295,21.3],[40.262,16.3],[40.262,21.3],[44.959,16.3],[44.959,21.3]],"m1":[33.518,16.25,38.165,21.35],"caseta":[38.325,16.4,40.232,21.35]},"cerco":[[1.05,18.0,31.3,18.0],[45.1,18.0,71.76,18.0],[71.76,18.0,71.76,131.21],[71.76,131.21,1.05,131.21],[1.05,131.21,1.05,18.0]],"pisos":{"veredas":[[[[44.08,54.905],[44.1,41.7],[53.8,41.7],[53.81,54.905],[53.81,41.575],[44.08,41.575]]],[[[63.205,78.669],[70.205,78.669],[70.205,56.844],[63.205,56.844]]],[[[44.08,56.674],[44.08,88.004],[44.1,56.7],[60.8,56.7],[60.81,88.004],[60.81,56.674]]],[[[28.185,88.004],[41.685,88.004],[41.685,77.709],[28.185,77.709]]],[[[54.485,129.024],[67.715,129.024],[67.715,91.494],[54.485,91.494]],[[67.7,129.0],[54.5,129.0],[54.5,91.5],[67.7,91.5]]],[[[51.635,129.024],[53.835,129.024],[53.835,122.424],[51.635,122.424]]]],"pavimento":[[[[2.148,18.0],[2.103,127.095],[2.703,127.105],[2.686,130.765],[70.08,130.768],[70.085,88.011],[63.205,88.004],[63.205,56.844],[70.196,56.844],[70.205,55.101],[71.0,55.092],[71.0,23.002],[71.751,23.001],[71.758,22.906],[68.759,22.901],[66.852,18.0],[51.797,18.0],[51.79,21.531],[48.065,24.381],[45.612,18.901],[45.6,22.1],[30.8,22.1],[30.798,18.704],[29.807,20.305],[27.439,18.904],[27.431,18.0],[12.845,18.0],[11.961,20.307],[10.911,20.308],[10.911,18.01],[10.817,18.001],[10.815,25.211],[12.335,25.219],[12.335,48.574],[2.723,48.574],[2.738,18.01]],[[54.485,91.494],[67.715,91.494],[67.715,129.024],[54.485,129.024]],[[63.36,29.398],[64.725,31.844],[64.726,38.874],[63.36,41.336]],[[44.08,56.674],[60.81,56.674],[60.8,88.4],[44.1,88.4]],[[44.1,31.3],[60.8,31.3],[60.8,39.5],[44.1,39.5]],[[51.635,122.424],[53.835,122.424],[53.835,129.024],[51.635,129.024]],[[44.08,41.575],[53.81,41.575],[53.8,55.5],[44.1,55.5]],[[30.8,91.5],[51.0,91.5],[51.0,104.7],[30.8,104.7]],[[30.8,115.8],[51.0,115.8],[51.0,129.0],[30.8,129.0]],[[28.185,77.709],[41.685,77.709],[41.685,88.004],[28.185,88.004]],[[37.285,69.49],[37.856,69.49],[37.864,69.939],[38.703,69.94],[38.765,69.99],[38.875,69.969],[38.965,70.042],[39.019,70.015],[39.049,69.94],[39.852,69.938],[39.856,69.49],[40.282,69.487],[40.285,69.04],[40.732,69.037],[40.735,68.595],[40.81,68.566],[40.837,68.512],[40.764,68.421],[40.785,68.312],[40.735,68.25],[40.735,67.772],[40.803,67.671],[40.735,67.586],[40.734,67.047],[40.285,67.039],[40.285,66.49],[41.585,66.49],[41.585,70.789],[37.285,70.789]],[[37.285,55.789],[37.285,54.49],[41.585,54.49],[41.585,58.789],[40.285,58.789],[40.285,58.24],[40.734,58.232],[40.735,57.693],[40.803,57.608],[40.735,57.507],[40.735,57.029],[40.785,56.967],[40.764,56.858],[40.837,56.767],[40.81,56.713],[40.735,56.684],[40.732,56.242],[40.285,56.239],[40.282,55.792],[39.856,55.789],[39.852,55.341],[39.049,55.339],[39.019,55.264],[38.965,55.237],[38.875,55.31],[38.765,55.289],[38.703,55.339],[37.864,55.34],[37.856,55.789]],[[12.6,25.1],[32.8,25.1],[32.8,49.9],[12.6,49.9]],[[28.285,54.49],[32.585,54.49],[32.585,55.789],[32.013,55.789],[32.013,55.658],[32.052,55.576],[32.013,55.493],[32.012,55.346],[31.863,55.339],[31.78,55.272],[31.677,55.339],[31.166,55.34],[31.104,55.289],[30.994,55.31],[30.904,55.237],[30.85,55.264],[30.821,55.339],[30.018,55.341],[30.013,55.789],[29.588,55.792],[29.585,56.239],[29.138,56.242],[29.135,56.684],[29.06,56.713],[29.032,56.767],[29.105,56.858],[29.085,56.967],[29.135,57.029],[29.135,57.507],[29.067,57.608],[29.135,57.693],[29.135,58.232],[29.585,58.24],[29.585,58.789],[28.285,58.789]],[[28.285,70.789],[28.285,66.49],[29.585,66.49],[29.585,67.039],[29.135,67.047],[29.135,67.586],[29.067,67.671],[29.135,67.772],[29.135,68.25],[29.085,68.312],[29.105,68.421],[29.032,68.512],[29.06,68.566],[29.135,68.595],[29.138,69.037],[29.585,69.04],[29.588,69.487],[30.013,69.49],[30.018,69.938],[30.821,69.94],[30.85,70.015],[30.904,70.042],[30.994,69.969],[31.104,69.99],[31.166,69.939],[31.677,69.94],[31.78,70.007],[31.863,69.94],[32.012,69.933],[32.013,69.786],[32.052,69.703],[32.013,69.621],[32.013,69.49],[32.585,69.49],[32.585,70.789]],[[3.5,92.6],[26.6,92.6],[26.6,127.0],[3.5,127.0]],[[12.6,50.9],[25.8,50.9],[25.8,88.4],[12.6,88.4]],[[4.211,70.574],[10.81,70.574],[10.81,72.574],[4.211,72.574]],[[4.211,66.574],[10.81,66.574],[10.81,68.574],[4.211,68.574]],[[4.211,62.574],[10.81,62.574],[10.81,64.574],[4.211,64.574]],[[4.211,58.574],[10.81,58.574],[10.81,60.574],[4.211,60.574]],[[4.211,54.574],[10.81,54.574],[10.81,56.574],[4.211,56.574]],[[4.211,50.574],[10.81,50.574],[10.81,52.574],[4.211,52.574]],[[2.3,74.0],[10.6,74.0],[10.6,88.2],[2.3,88.2]]],[[[1.104,18.01],[1.05,18.01],[1.06,86.591],[1.07,86.581]]]],"verdes":[[[[27.439,18.001],[27.439,18.904],[29.807,20.305],[30.8,18.675],[30.8,18.001]]],[[[10.911,18.001],[10.911,20.308],[11.961,20.307],[12.839,18.001]]],[[[2.723,48.574],[12.335,48.574],[12.335,25.219],[10.815,25.219],[10.811,18.001],[2.738,18.001]]],[[[4.211,50.574],[4.211,52.574],[10.81,52.574],[10.81,50.574]]],[[[4.211,54.574],[4.211,56.574],[10.81,56.574],[10.81,54.574]]],[[[10.81,58.574],[4.211,58.574],[4.211,60.574],[10.81,60.574]]],[[[10.81,62.574],[4.211,62.574],[4.211,64.574],[10.81,64.574]]],[[[10.81,66.574],[4.211,66.574],[4.211,68.574],[10.81,68.574]]],[[[10.81,70.574],[4.211,70.574],[4.211,72.574],[10.81,72.574]]],[[[71.76,22.901],[71.76,18.048],[66.859,18.001],[68.759,22.901]]],[[[45.6,18.001],[45.6,18.864],[48.065,24.381],[51.79,21.531],[51.79,18.001]]],[[[64.726,38.874],[64.725,31.844],[63.36,29.398],[63.36,41.336]]],[[[29.105,56.858],[29.031,56.768],[29.058,56.714],[29.135,56.684],[29.135,56.24],[29.585,56.24],[29.585,55.79],[30.013,55.79],[30.013,55.34],[30.821,55.34],[30.851,55.263],[30.905,55.236],[30.994,55.31],[31.104,55.289],[31.166,55.34],[31.677,55.34],[31.779,55.271],[31.863,55.34],[32.013,55.34],[32.013,55.493],[32.053,55.576],[32.013,55.658],[32.013,55.79],[32.585,55.79],[32.585,54.49],[28.285,54.49],[28.285,58.789],[29.585,58.789],[29.585,58.24],[29.135,58.24],[29.135,57.693],[29.066,57.609],[29.135,57.507],[29.135,57.029],[29.084,56.968]]],[[[38.965,55.236],[39.019,55.263],[39.049,55.34],[39.856,55.34],[39.856,55.79],[40.285,55.79],[40.285,56.24],[40.735,56.24],[40.735,56.684],[40.811,56.714],[40.838,56.768],[40.764,56.858],[40.786,56.968],[40.735,57.029],[40.735,57.507],[40.803,57.609],[40.735,57.693],[40.735,58.24],[40.285,58.24],[40.285,58.789],[41.585,58.789],[41.585,54.49],[37.285,54.49],[37.285,55.79],[37.856,55.79],[37.856,55.34],[38.703,55.34],[38.765,55.289],[38.875,55.31]]],[[[31.159,69.955],[31.104,69.99],[30.994,69.969],[30.905,70.043],[30.851,70.016],[30.821,69.939],[30.013,69.939],[30.013,69.489],[29.585,69.489],[29.585,69.039],[29.135,69.039],[29.135,68.595],[29.058,68.565],[29.031,68.511],[29.105,68.421],[29.084,68.311],[29.135,68.25],[29.135,67.772],[29.066,67.67],[29.135,67.586],[29.135,67.039],[29.585,67.039],[29.585,66.489],[28.285,66.489],[28.285,70.789],[32.585,70.789],[32.585,69.489],[32.013,69.489],[32.013,69.621],[32.053,69.703],[32.013,69.786],[32.013,69.939],[31.863,69.939],[31.779,70.008],[31.677,69.939]]],[[[40.772,68.431],[40.838,68.511],[40.811,68.565],[40.735,68.595],[40.735,69.039],[40.285,69.039],[40.285,69.489],[39.856,69.489],[39.856,69.939],[39.049,69.939],[39.019,70.016],[38.965,70.043],[38.875,69.969],[38.765,69.99],[38.703,69.939],[37.856,69.939],[37.856,69.489],[37.285,69.489],[37.285,70.789],[41.585,70.789],[41.585,66.489],[40.285,66.489],[40.285,67.039],[40.735,67.039],[40.735,67.586],[40.803,67.67],[40.735,67.772],[40.735,68.25],[40.786,68.311]]],[[[2.685,130.769],[2.703,127.105],[2.103,127.105],[2.138,18.001],[1.104,18.001],[1.05,131.21],[71.76,131.21],[71.76,23.001],[71.0,23.001],[71.0,55.099],[70.205,55.101],[70.205,78.669],[63.205,78.669],[63.205,88.004],[70.085,88.002],[70.085,130.769]]]],"plaza":[[[[29.7,55.9],[40.2,55.9],[40.2,69.4],[29.7,69.4]]]]},"arboles":[[48.81,19.47],[68.31,19.44],[27.85,18.36],[45.75,19.47],[6.16,43.72],[6.16,38.23],[6.16,32.24],[5.35,20.21],[6.0,52],[6.0,60],[6.0,68],[2.5,46],[66,33],[66,45],[66,56],[66,70],[66,82],[28,60],[29,90],[52,90],[48.5,114],[60,112],[28.8,18.8],[58,19.3]],"medidas":{"VOL":1.5,"H_MURO":3.3,"Z_TECHO":3.75,"PEND":0.28}}'''
# Modelo nativo del Hogar de Refugio Temporal (CUI 2675514) - Revit + Dynamo (nodo Python Script, CPython3 o PythonNet3)
# Correr UNA vez en un proyecto nuevo (plantilla de arquitectura), con las familias de puerta, ventana, columna y vegetación
# cargadas. Medidas en metros (se pasan a pies). Origen local = E 349 090, N 9 281 900 (mismo origen del IFC complementario).
import clr, json, math
clr.AddReference('RevitAPI'); clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB.Visual import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List

import traceback
doc = DocumentManager.Instance.CurrentDBDocument
D = json.loads(DATOS_JSON)
LOG = []
cuenta = {}
def _principal():
    M = D['medidas']
    FT = 1 / 0.3048
    def ft(v): return v * FT
    def P(x, y, z=0.0): return XYZ(ft(x), ft(y), ft(z))
    def nota(t): LOG.append(t)

    TransactionManager.Instance.EnsureInTransaction(doc)

    # ---------------- nivel
    niveles = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda l: abs(l.Elevation))
    NIV = niveles[0] if niveles else Level.Create(doc, 0.0)

    # ---------------- materiales con color (sombreado) y apariencia (realista)
    PLANTILLA_APAR = None
    for a in FilteredElementCollector(doc).OfClass(AppearanceAssetElement).ToElements():
        try:
            if a.GetRenderingAsset().FindByName('generic_diffuse') is not None:
                PLANTILLA_APAR = a; break
        except Exception:
            pass
    MATS = {}
    def material(nombre, rgb):
        if nombre in MATS: return MATS[nombre]
        ex = [m for m in FilteredElementCollector(doc).OfClass(Material).ToElements() if m.Name == nombre]
        mat = ex[0] if ex else doc.GetElement(Material.Create(doc, nombre))
        mat.Color = Color(rgb[0], rgb[1], rgb[2]); mat.UseRenderAppearanceForShading = False
        if PLANTILLA_APAR is not None and not ex:
            try:
                ap = PLANTILLA_APAR.Duplicate('Apar ' + nombre)
                esc = AppearanceAssetEditScope(doc)
                asset = esc.Start(ap.Id)
                asset.FindByName('generic_diffuse').SetValueAsColor(Color(rgb[0], rgb[1], rgb[2]))
                esc.Commit(True); esc.Dispose()
                mat.AppearanceAssetId = ap.Id
            except Exception as ex_:
                nota('apariencia %s: %s' % (nombre, ex_))
        MATS[nombre] = mat.Id
        return mat.Id

    TP1 = material('HR TP-1 Guinda', (123, 31, 45)); TP2 = material('HR TP-2 Gris', (125, 133, 139))
    TP3 = material('HR TP-3 Blanco RAL 9010', (241, 236, 225)); CONC = material('HR Concreto', (186, 182, 174))
    VER = material('HR Vereda', (190, 186, 178)); CAL = material('HR Calamina', (196, 200, 204))
    PASTO = material('HR Area verde', (88, 128, 58)); ACERO = material('HR Acero', (110, 115, 120))
    ADOQ = material('HR Adoquin', (150, 92, 74)); CANCHA = material('HR Losa deportiva', (150, 62, 52))

    # ---------------- tipos de muro, piso y cubierta de una capa
    def tipo(clase, base_nombre, nombre, ancho, mat, funcion=MaterialFunctionAssignment.Structure):
        ex = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements() if t.Name == nombre]
        if ex: return ex[0]
        bases = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements()
                 if (clase != WallType or t.Kind == WallKind.Basic) and t.GetCompoundStructure() is not None]
        t = doc.GetElement(bases[0].Duplicate(nombre).Id)
        cs = CompoundStructure.CreateSingleLayerCompoundStructure(funcion, ft(ancho), mat)
        t.SetCompoundStructure(cs)
        return t

    W_TP2 = tipo(WallType, '', 'HR-Muro TP-2 e=0.15', 0.15, TP2)
    W_VIGA = tipo(WallType, '', 'HR-Viga collar TP-1 0.23', 0.23, TP1)
    W_HAST = tipo(WallType, '', 'HR-Hastial TP-3 e=0.20', 0.20, TP3)
    W_CERCO = tipo(WallType, '', 'HR-Cerco TP-3 e=0.15', 0.15, TP3)
    W_ZOC = tipo(WallType, '', 'HR-Zocalo cerco TP-2 e=0.17', 0.17, TP2)
    W_PARA = tipo(WallType, '', 'HR-Parapeto PL-2 TP-3 e=0.35', 0.35, TP3)
    W_LAT = tipo(WallType, '', 'HR-Muro lateral OE-01 TP-2 e=0.20', 0.20, TP2)
    F_PISO = tipo(FloorType, '', 'HR-Piso concreto e=0.15', 0.15, CONC)
    F_VER = tipo(FloorType, '', 'HR-Vereda e=0.10', 0.10, VER)
    F_PAV = tipo(FloorType, '', 'HR-Pavimento concreto e=0.10', 0.10, CONC)
    F_VERDE = tipo(FloorType, '', 'HR-Area verde e=0.05', 0.05, PASTO)
    F_ADOQ = tipo(FloorType, '', 'HR-Patio civico adoquin e=0.12', 0.12, ADOQ)
    F_LOSA = tipo(FloorType, '', 'HR-Losa deportiva e=0.12', 0.12, CANCHA)
    R_CAL = tipo(RoofType, '', 'HR-Cobertura calamina e=0.05', 0.05, CAL)
    R_LOSA = tipo(RoofType, '', 'HR-Cobertura losa OE-01 e=0.20', 0.20, CONC)

    # ---------------- utilidades
    def lazo(pts):
        cl = CurveLoop()
        for i in range(len(pts)):
            a = pts[i]; b = pts[(i + 1) % len(pts)]
            if a.DistanceTo(b) > 0.003: cl.Append(Line.CreateBound(a, b))
        return cl

    def piso(anillos, ftipo, z_sup):
        n = 0
        for poli in anillos:
            try:
                loops = List[CurveLoop]()
                for r in poli: loops.Add(lazo([P(x, y) for x, y in r]))
                fl = Floor.Create(doc, loops, ftipo.Id, NIV.Id)
                fl.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(ft(z_sup))
                n += 1
            except Exception as ex_:
                nota('piso %s: %s' % (ftipo.Name, ex_))
        return n

    def muro(x0, y0, x1, y1, wtipo, z0, h):
        w = Wall.Create(doc, Line.CreateBound(P(x0, y0), P(x1, y1)), wtipo.Id, NIV.Id, ft(h), ft(z0), False, False)
        return w

    def muro_perfil(pts, wtipo):
        c = List[Curve]()
        for i in range(len(pts)):
            a = P(*pts[i]); b = P(*pts[(i + 1) % len(pts)]); c.Add(Line.CreateBound(a, b))
        return Wall.Create(doc, c, wtipo.Id, NIV.Id, False)

    def solido(x0, y0, z0, x1, y1, z1, mat, cat, nombre):
        """Caja como DirectShape (categoría nativa con material), para piezas que no tienen familia en el proyecto."""
        loops = List[CurveLoop](); loops.Add(lazo([P(x0, y0, z0), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0)]))
        so = SolidOptions(mat, ElementId.InvalidElementId)
        s = GeometryCreationUtilities.CreateExtrusionGeometry(loops, XYZ.BasisZ, ft(z1 - z0), so)
        ds = DirectShape.CreateElement(doc, ElementId(cat))
        g = List[GeometryObject](); g.Add(s); ds.SetShape(g); ds.Name = nombre
        return ds

    def simbolo(cat, claves, nombre_tipo, dims=(), mat=None):
        """Tipo de familia cargada: el primero cuyo nombre tenga una de las claves; se duplica con las medidas pedidas.
        dims = [(valor_m, [nombres de parámetro], [BuiltInParameter])]."""
        sims = [s for s in FilteredElementCollector(doc).OfCategory(cat).OfClass(FamilySymbol).ToElements()]
        if not sims: return None
        elegido = None
        for k in claves:
            for s in sims:
                if k.lower() in (s.FamilyName + ' ' + s.Name).lower(): elegido = s; break
            if elegido: break
        elegido = elegido or sims[0]
        ex = [s for s in sims if s.Name == nombre_tipo and s.FamilyName == elegido.FamilyName]
        if ex: s = ex[0]
        else:
            s = doc.GetElement(elegido.Duplicate(nombre_tipo).Id)
            for val, nombres, bips in dims:
                p = None
                for b in bips:
                    q = s.get_Parameter(b)
                    if q is not None and not q.IsReadOnly: p = q; break
                if p is None:
                    for n in nombres:
                        q = s.LookupParameter(n)
                        if q is not None and not q.IsReadOnly: p = q; break
                if p is not None: p.Set(ft(val))
                else: nota('%s: sin parámetro %s' % (nombre_tipo, nombres[0]))
            if mat is not None:
                q = s.LookupParameter('Material')
                if q is not None and not q.IsReadOnly: q.Set(mat)
        if not s.IsActive: s.Activate()
        return s

    S_COL = {}
    def columna(x, y, b, h, z0, z1, mat, nombre):
        k = (b, h, mat.IntegerValue if hasattr(mat, 'IntegerValue') else str(mat))
        if k not in S_COL:
            S_COL[k] = simbolo(BuiltInCategory.OST_Columns, ('rectangular', 'rectangle'), 'HR-Columna %.2fx%.2f %s' % (b, h, doc.GetElement(mat).Name),
                               [(b, ['Width', 'Ancho', 'b'], []), (h, ['Depth', 'Profundidad', 'h'], [])], mat)
        s = S_COL[k]
        if s is not None:
            try:
                c = doc.Create.NewFamilyInstance(P(x, y, 0), s, NIV, StructuralType.NonStructural)
                for bip, val in ((BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM, ft(z0)), (BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM, ft(z1))):
                    q = c.get_Parameter(bip)
                    if q is not None and not q.IsReadOnly: q.Set(val)
                q = c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM)
                if q is not None and not q.IsReadOnly: q.Set(NIV.Id)
                return c
            except Exception as ex_:
                nota('columna familia: %s' % ex_)
        return solido(x - b / 2, y - h / 2, z0, x + b / 2, y + h / 2, z1, mat, BuiltInCategory.OST_Columns, nombre)

    def techo_huella(rect, base, pend, eje, rtipo):
        x0, y0, x1, y1 = rect
        ca = CurveArray()
        for a, b in ((P(x0, y0), P(x1, y0)), (P(x1, y0), P(x1, y1)), (P(x1, y1), P(x0, y1)), (P(x0, y1), P(x0, y0))):
            ca.Append(Line.CreateBound(a, b))
        try:
            res = doc.Create.NewFootPrintRoof(ca, NIV, rtipo, ModelCurveArray())
        except Exception:
            res = doc.Create.NewFootPrintRoof(ca, NIV, rtipo)
        roof = res[0] if isinstance(res, tuple) else res
        roof.get_Parameter(BuiltInParameter.ROOF_LEVEL_OFFSET_PARAM).Set(ft(base))
        for arr in roof.GetProfiles():
            for mc in arr:
                ln = mc.GeometryCurve; d = ln.GetEndPoint(1) - ln.GetEndPoint(0)
                paralelo_y = abs(d.Y) > abs(d.X)
                define = (eje == 'y' and paralelo_y) or (eje == 'x' and not paralelo_y)
                if eje == 'una':
                    define = abs(ln.GetEndPoint(0).Y - ft(y1)) < 0.01 and abs(ln.GetEndPoint(1).Y - ft(y1)) < 0.01
                try:
                    roof.set_DefinesSlope(mc, define)
                    if define: roof.set_SlopeAngle(mc, pend)
                except Exception:
                    roof.DefinesSlope[mc] = define
                    if define: roof.SlopeAngle[mc] = pend
        return roof

    def suma(k, n=1): cuenta[k] = cuenta.get(k, 0) + n

    # ---------------- edificaciones E-01 a E-09
    S_PUERTA = {}; S_VENT = {}
    for e in D['edificios']:
        try:
            a0, b0, a1, b1 = e['muro']; t = 0.075
            piso([[[[x, y] for x, y in ((e['piso'][0], e['piso'][1]), (e['piso'][2], e['piso'][1]), (e['piso'][2], e['piso'][3]), (e['piso'][0], e['piso'][3]))]]], F_PISO, 0.15)
            muros = []
            for (xa, ya, xb, yb, nx, ny) in e['lados']:                    # eje del muro 0.075 hacia adentro de la cara exterior
                w = muro(xa - nx * t, ya - ny * t, xb - nx * t, yb - ny * t, W_TP2, 0.15, M['H_MURO'] - 0.15); muros.append(w); suma('muros')
                muro(xa - nx * 0.115, ya - ny * 0.115, xb - nx * 0.115, yb - ny * 0.115, W_VIGA, M['H_MURO'], M['Z_TECHO'] - M['H_MURO']); suma('vigas collar')
            for h in e['hastiales']:
                try: muro_perfil(h, W_HAST); suma('hastiales')
                except Exception as ex_: nota('%s hastial: %s' % (e['cod'], ex_))
            cols = []
            for (x, y) in e['columnas']:
                cols.append(columna(x, y, 0.32, 0.32, 0.15, M['H_MURO'], TP1, e['cod'] + ' columna TP-1')); suma('columnas')
            doc.Regenerate()
            for c in cols:                                                 # la columna queda en TP-1 (no toma el material del muro)
                for w in muros:
                    try:
                        if JoinGeometryUtils.AreElementsJoined(doc, c, w): JoinGeometryUtils.UnjoinGeometry(doc, c, w)
                    except Exception: pass
            for v in e['vanos']:
                try:
                    w = muros[v['lado']]
                    if v['tipo'] == 'puerta':
                        k = (v['ancho'], v['alto'], v.get('vidrio', False))
                        if k not in S_PUERTA:
                            S_PUERTA[k] = simbolo(BuiltInCategory.OST_Doors, ('double glass', 'doble', 'glass') if k[2] else ('single-flush', 'single', 'simple'),
                                                  'HR-Puerta %.2fx%.2f%s' % (k[0], k[1], ' vidrio' if k[2] else ''),
                                                  [(k[0], ['Width', 'Ancho'], [BuiltInParameter.DOOR_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                                   (k[1], ['Height', 'Altura'], [BuiltInParameter.DOOR_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
                        s = S_PUERTA[k]
                    else:
                        k = (v['ancho'], v['alto'])
                        if k not in S_VENT:
                            S_VENT[k] = simbolo(BuiltInCategory.OST_Windows, ('sliding', 'corrediza', 'fixed', 'fija'), 'HR-Ventana %.2fx%.2f' % k,
                                                [(k[0], ['Width', 'Ancho'], [BuiltInParameter.WINDOW_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                                 (k[1], ['Height', 'Altura'], [BuiltInParameter.WINDOW_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
                        s = S_VENT[k]
                    if s is None: nota('sin familia de %s cargada' % v['tipo']); continue
                    nx, ny = e['lados'][v['lado']][4], e['lados'][v['lado']][5]
                    fi = doc.Create.NewFamilyInstance(P(v['x'] - nx * 0.075, v['y'] - ny * 0.075, 0), s, w, NIV, StructuralType.NonStructural)
                    pa = fi.get_Parameter(BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                    if pa is not None and not pa.IsReadOnly: pa.Set(ft(v['alf']))
                    suma(v['tipo'] + 's')
                except Exception as ex_:
                    nota('%s %s: %s' % (e['cod'], v['tipo'], ex_))
            techo_huella(e['techo'], e['alero'], M['PEND'], e['cumbrera'], R_CAL); suma('cubiertas a dos aguas')
        except Exception as ex_:
            nota('%s: %s' % (e['cod'], ex_))

    # ---------------- losa deportiva OC-06: losa, columnas y cubierta en arco
    L = D['losa']; x0, y0, x1, y1 = L['rect']
    try:
        piso([[[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]]], F_LOSA, 0.12)
        for (x, y) in L['columnas']:
            columna(x, y, 0.36, 0.36, 0.12, L['h_col'], ACERO, 'OC-06 columna'); suma('columnas')
        rp = doc.Create.NewReferencePlane(P(x1, y0, 0), P(x0, y0, 0), XYZ.BasisZ, doc.ActiveView)
        ca = CurveArray()
        ca.Append(Arc.Create(P(x0, y0, L['h_col']), P(x1, y0, L['h_col']), P((x0 + x1) / 2, y0, L['h_col'] + L['flecha'])))
        doc.Create.NewExtrusionRoof(ca, rp, NIV, R_CAL, 0.0, ft(y1 - y0)); suma('cubierta en arco')
    except Exception as ex_:
        nota('losa deportiva: %s' % ex_)

    # ---------------- pórtico de ingreso OE-01
    O = D['oe01']; gx0, gx1, yf, yb = O['gx0'], O['gx1'], O['yf'], O['yb']
    try:
        piso([[[[gx0 - 0.5, yf - 0.6], [gx1 + 0.5, yf - 0.6], [gx1 + 0.5, yb + 0.6], [gx0 - 0.5, yb + 0.6]]]], F_VER, 0.05)
        for (x, y) in O['columnas']:
            columna(x, y, 0.26, 0.40, 0.05, 4.18, TP1, 'OE-01 columna C-1'); suma('columnas')
        solido(gx0, yf, 4.18, gx1, yf + 0.4, 4.71, TP1, BuiltInCategory.OST_StructuralFraming, 'OE-01 viga VG-1')
        solido(gx0, yf + 0.05, 4.71, gx1, yf + 0.4, 5.09, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 cielo CR-1')
        solido(gx0, yb - 0.4, 3.55, gx1, yb, 4.19, TP1, BuiltInCategory.OST_StructuralFraming, 'OE-01 viga posterior')
        muro(gx0 - 0.05, yf + 0.125, gx1 + 0.05, yf + 0.125, W_PARA, 5.09, 0.86)
        muro(gx0 - 0.05, yb - 0.10, gx1 + 0.05, yb - 0.10, W_PARA, 4.19, 0.60)
        for xx, s in ((gx0 + 0.1, 1), (gx1 - 0.1, -1)):
            muro_perfil([[xx, yf, 0.05], [xx, yb, 0.05], [xx, yb, 4.19], [xx, yf, 5.72]], W_LAT); suma('muros')
        m = O['m1']; solido(m[0], m[1], 0.05, m[2], m[3], 4.18, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 muro M-1 (SS.HH.)')
        c = O['caseta']; solido(c[0], c[1], 0.05, c[2], c[3], 3.5, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 caseta de vigilancia')
        techo_huella([gx0, yf + 0.3, gx1, yb - 0.2], 4.19, (5.72 - 4.19) / (yb - yf - 0.5), 'una', R_LOSA); suma('cubierta OE-01')
    except Exception as ex_:
        nota('OE-01: %s' % ex_)

    # ---------------- cerco perimétrico (muro TP-3, zócalo TP-2, columnas cada 3 m)
    for (xa, ya, xb, yb_) in D['cerco']:
        try:
            Lc = math.hypot(xb - xa, yb_ - ya)
            if Lc < 0.5: continue
            muro(xa, ya, xb, yb_, W_CERCO, 0.0, 2.43); muro(xa, ya, xb, yb_, W_ZOC, 0.0, 0.60); suma('tramos de cerco')
            nc = max(1, int(round(Lc / 3.0)))
            for k in range(nc + 1):
                t = float(k) / nc
                solido(xa + (xb - xa) * t - 0.14, ya + (yb_ - ya) * t - 0.14, 0.0, xa + (xb - xa) * t + 0.14, ya + (yb_ - ya) * t + 0.14, 2.5,
                       TP2, BuiltInCategory.OST_Columns, 'Columna de cerco')
        except Exception as ex_:
            nota('cerco: %s' % ex_)

    # ---------------- pisos exteriores
    Pz = D['pisos']
    suma('veredas', piso(Pz['veredas'], F_VER, 0.10)); suma('pavimento', piso(Pz['pavimento'], F_PAV, 0.08))
    suma('areas verdes', piso(Pz['verdes'], F_VERDE, 0.02)); suma('patio civico', piso(Pz['plaza'], F_ADOQ, 0.12))

    # ---------------- árboles (familia de vegetación RPC del proyecto)
    sims = [s for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).OfClass(FamilySymbol).ToElements()]
    if sims:
        s = next((x for x in sims if 'tree' in (x.FamilyName + x.Name).lower() or 'arbol' in (x.FamilyName + x.Name).lower()), sims[0])
        if not s.IsActive: s.Activate()
        for (x, y) in D['arboles']:
            try: doc.Create.NewFamilyInstance(P(x, y, 0), s, NIV, StructuralType.NonStructural); suma('arboles')
            except Exception as ex_: nota('arbol: %s' % ex_)
    else:
        nota('No hay familia de vegetación cargada: Insertar > Cargar familia de Autodesk > Vegetación (RPC Tree) y volver a correr solo esta parte.')


TransactionManager.Instance.EnsureInTransaction(doc)
ERROR = None
try:
    _principal()
except Exception:
    ERROR = traceback.format_exc()
TransactionManager.Instance.TransactionTaskDone()
OUT = (['ERROR (copiar este texto):', ERROR] if ERROR else []) + ['%s: %d' % (k, v) for k, v in sorted(cuenta.items())] + ['--- avisos ---'] + LOG[:200]
