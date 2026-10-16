# Engine patch

`engine/lymphodoom.patch` applies to [Dwasm](https://github.com/GMH-Code/Dwasm) at commit
`ddf0347a4fc115b11ffb1c5710768b7c47c46698` (PrBoomX / PrBoom+ built for WebAssembly).
`engine/build.sh` clones Dwasm, checks out that commit and applies the patch.

## What it changes

| Area | Change | Files |
| --- | --- | --- |
| IWAD | A `LYMPHO` lump marks our IWAD as a registered Doom 1 episode; missing demos are skipped | `d_main.c` |
| Menus | Two skills (COMMON COLD = 2, METASTASIS = 4); main menu has only New Game; no help, save/load, options or quit; menus draw on a clean background; UMAPINFO episodes are not trimmed | `m_menu.c` |
| Start | The page passes `-skill 2|4 -warp 1 1`, so the game opens straight in E1M1 | — |
| Intermission | Body map with three spots, no animations, a plain stats background, a BODY line | `wi_stuff.c` |
| Finale | An `endpic` without `intertext` goes straight to the picture; BODY % is drawn under it | `f_finale.c`, `f_finale2.c` |
| BODY | Organism health: drains over time, +1 % per enemy, +10 % for the boss, −5 % per own cell; at 0 the "THE BODY DIED" screen, then E1M1 again; T-cell death restores the level-start value | `lympho.c`, `lympho.h`, hooks in `g_game.c`, `p_inter.c`, `p_tick.c` |
| HUD | The ARMS panel shows BODY (number + silhouette, blinks red below 25 %) | `st_stuff.c`, `d_main.c`, `lympho.c` |
| Own cells | New codepointer `A_CivWander`: wander, run from the nearest visible enemy within 384 units | `p_enemy.c`, `p_enemy.h`, `d_deh.c` |
| Build | Cheat handlers share one signature, so the build runs without `EMULATE_FUNCTION_POINTER_CASTS` | `m_cheat.c`, `CMakeLists.txt` |

## Testing switches

- `-bodysecs N` (engine argument): a full body lasts N seconds instead of 15 / 9 minutes.
- `LYMPHO_TEST_BOSS=1 python3 tools/build.py ...`: the boss dies at spawn next to the player
  (checks the boss exit, intermission and finale).
- `LYMPHO_TEST_CIV=1 python3 tools/build.py ...`: four own cells stand in front of the E1M1 start.

## Updating the patch

Edit the Dwasm checkout in `build/work/Dwasm`, then:

    cd build/work/Dwasm
    git add -N src/lympho.c src/lympho.h
    git diff -- CMakeLists.txt src > ../../../engine/lymphodoom.patch
