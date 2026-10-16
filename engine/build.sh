#!/bin/sh
# Build the LYMPHODOOM engine (Dwasm = PrBoomX/PrBoom+ for WebAssembly) and its data package.
# Needs: git, cmake, a C compiler + SDL2 dev libs (native step, for prboomx.wad), Emscripten (emcmake on PATH),
# python3 with pillow/numpy/shapely, zdbsp, and freedoom1.wad (only GENMIDI/DMXGUS and a few UI lumps are used).
#   sh engine/build.sh /path/to/freedoom1.wad
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
FREEDOOM=${1:?path to freedoom1.wad}
WORK=${WORK:-$ROOT/build/work}
DWASM_COMMIT=ddf0347a4fc115b11ffb1c5710768b7c47c46698
mkdir -p "$WORK"
if [ ! -d "$WORK/Dwasm" ]; then
  git clone https://github.com/GMH-Code/Dwasm.git "$WORK/Dwasm"
  git -C "$WORK/Dwasm" checkout -q $DWASM_COMMIT
  git -C "$WORK/Dwasm" apply "$ROOT/engine/lymphodoom.patch"
fi
D="$WORK/Dwasm"
# 1. native build: produces prboomx.wad (engine resources) and a test binary
mkdir -p "$D/build_native"
(cd "$D/build_native" && cmake .. -DCMAKE_BUILD_TYPE=Release >/dev/null && make -j2 >/dev/null)
# 2. game data
python3 "$ROOT/tools/build.py" --freedoom "$FREEDOOM" --prboomx "$D/build_native/prboomx.wad" --out "$ROOT/build"
# 3. wasm build with our data, defaults and shell
rm -rf "$D/wasm/fs" && mkdir -p "$D/wasm/fs/defaults"
cp "$ROOT/build/lymphodoom.wad" "$ROOT/build/prboomx.wad" "$D/wasm/fs/"
cp "$ROOT/engine/prboomX.cfg" "$D/wasm/fs/defaults/prboomX.cfg"
cp "$ROOT/engine/shell.html" "$D/wasm/shell.html"
mkdir -p "$D/build_wasm"
(cd "$D/build_wasm" && emcmake cmake .. -DCMAKE_BUILD_TYPE=Release >/dev/null && make -j2 >/dev/null)
mkdir -p "$ROOT/web/game"
cp "$D/build_wasm/index.js" "$D/build_wasm/index.wasm" "$D/build_wasm/index.data" "$ROOT/web/game/"
for f in "$ROOT"/web/game/index.js "$ROOT"/web/game/index.wasm "$ROOT"/web/game/index.data; do
  gzip -9 -n -k -f "$f"
done
ls -la "$ROOT/web/game"
