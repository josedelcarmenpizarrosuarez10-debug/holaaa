#!/bin/sh
# Texturas, cielos y figuras de uso libre (repositorio de three.js en GitHub y muestras glTF de Khronos), en ./assets
mkdir -p assets && cd assets
R=https://raw.githubusercontent.com
for u in mrdoob/three.js/dev/examples/models/gltf/Michelle.glb mrdoob/three.js/dev/examples/models/gltf/Xbot.glb \
         mrdoob/three.js/dev/examples/models/gltf/readyplayer.me.glb \
         KhronosGroup/glTF-Sample-Assets/main/Models/CesiumMan/glTF-Binary/CesiumMan.glb \
         mrdoob/three.js/dev/examples/textures/terrain/grasslight-big.jpg; do
  curl -sSL -o "$(basename $u)" "$R/$u"
done
