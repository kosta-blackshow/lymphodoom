"""DEHACKED/BEX patch: English strings, the spectre's own sprite (DEHEXTRA states),
and UMAPINFO for the three-level episode."""

# Spectre (Thing 14) gets copies of the demon's states (475..501) using sprite SP00
# (index 145) so TUMOR NO MHC-I looks like a tumour cell, not a parasite.
SARG_FIRST, SARG_LAST = 475, 501
NEW_FIRST = 1089
SP00 = 145
SARG_STATES = [
    # (sprite frame, tics, action, next)  — copied from info.c S_SARG_STND..S_SARG_RAISE6
    (0, 10, "Look", 476), (1, 10, "Look", 475),
    (0, 2, "Chase", 478), (0, 2, "Chase", 479), (1, 2, "Chase", 480), (1, 2, "Chase", 481),
    (2, 2, "Chase", 482), (2, 2, "Chase", 483), (3, 2, "Chase", 484), (3, 2, "Chase", 477),
    (4, 8, "FaceTarget", 486), (5, 8, "FaceTarget", 487), (6, 8, "SargAttack", 477),
    (7, 2, None, 489), (7, 2, "Pain", 477),
    (8, 8, None, 491), (9, 8, "Scream", 492), (10, 4, None, 493), (11, 4, "Fall", 494), (12, 4, None, 495),
    (13, -1, None, 0),
    (13, 5, None, 497), (12, 5, None, 498), (11, 5, None, 499), (10, 5, None, 500), (9, 5, None, 501), (8, 5, None, 477),
]


def remap(s):
    if s == 0:
        return 0
    return NEW_FIRST + (s - SARG_FIRST)


STRINGS = {
    # pickups
    "GOTARMOR": "Picked up a cell membrane.",
    "GOTMEGA": "Picked up a double membrane!",
    "GOTHTHBONUS": "Picked up a sugar crumb.",
    "GOTARMBONUS": "Picked up a lipid patch.",
    "GOTSTIM": "Picked up glucose.",
    "GOTMEDINEED": "Picked up glucose that you REALLY need!",
    "GOTMEDIKIT": "Picked up a glucose chain.",
    "GOTSUPER": "IL-2 surge!",
    "GOTBLUECARD": "Picked up a white MHC-I badge.",
    "GOTYELWCARD": "Picked up a yellow MHC-I badge.",
    "GOTREDCARD": "Picked up an orange MHC-I badge.",
    "GOTBLUESKUL": "Picked up a white MHC-I badge.",
    "GOTYELWSKUL": "Picked up a yellow MHC-I badge.",
    "GOTREDSKULL": "Picked up an orange MHC-I badge.",
    "GOTINVUL": "Immune privilege!",
    "GOTBERSERK": "Inflammation!",
    "GOTINVIS": "Camouflage",
    "GOTSUIT": "Mucus coat",
    "GOTMAP": "A dendritic scout shows you the way.",
    "GOTVISOR": "Night vision",
    "GOTMSPHERE": "Memory cell!",
    "GOTCLIP": "Picked up a granule sac.",
    "GOTCLIPBOX": "Picked up a granule pouch.",
    "GOTROCKET": "Picked up an antibody.",
    "GOTROCKBOX": "Picked up a bundle of antibodies.",
    "GOTCELL": "Picked up an interferon capsule.",
    "GOTCELLBOX": "Picked up an interferon reservoir.",
    "GOTSHELLS": "Picked up cytokine vesicles.",
    "GOTSHELLBOX": "Picked up a box of cytokine vesicles.",
    "GOTBACKPACK": "Picked up an ATP pack!",
    "GOTBFG9000": "You got the CAR-T BOOST! Oh, yes.",
    "GOTCHAINGUN": "You got the granzyme stream!",
    "GOTCHAINSAW": "A cytotoxic drill! Find some infection!",
    "GOTLAUNCHER": "You got the antibody bomb!",
    "GOTPLASMA": "You got the interferon burst!",
    "GOTSHOTGUN": "You got the cytokine burst!",
    "GOTSHOTGUN2": "You got the super cytokine burst!",
    # locked doors
    "PD_BLUEO": "You need a white MHC-I badge to activate this object",
    "PD_REDO": "You need an orange MHC-I badge to activate this object",
    "PD_YELLOWO": "You need a yellow MHC-I badge to activate this object",
    "PD_BLUEK": "You need a white MHC-I badge to open this gate",
    "PD_REDK": "You need an orange MHC-I badge to open this gate",
    "PD_YELLOWK": "You need a yellow MHC-I badge to open this gate",
    "PD_BLUEC": "You need a white MHC-I badge to open this gate",
    "PD_REDC": "You need an orange MHC-I badge to open this gate",
    "PD_YELLOWC": "You need a yellow MHC-I badge to open this gate",
    "PD_BLUES": "You need a white MHC-I badge to open this gate",
    "PD_REDS": "You need an orange MHC-I badge to open this gate",
    "PD_YELLOWS": "You need a yellow MHC-I badge to open this gate",
    # levels
    "HUSTR_E1M1": "E1M1: Lymph Node",
    "HUSTR_E1M2": "E1M2: Bloodstream",
    "HUSTR_E1M3": "E1M3: Tumor",
    # menus and messages
    "NIGHTMARE": "Are you sure? This infection\\nwill not let go.\\n\\npress y or n.",
    "QUITMSG": "Leave the body defenceless?\\n\\npress y to quit.",
    "QUITMSG1": "The infection will spread\\nwhile you're gone!",
    "QUITMSG2": "Wait, there are still\\ntumor cells hiding!",
    "QUITMSG3": "Your immune system\\nwill miss you.",
    "QUITMSG4": "One more germinal center?",
    "QUITMSG5": "The macrophages can clean\\nup without you, I guess.",
    "QUITMSG6": "Apoptosis is not\\nthe answer!",
    "QUITMSG7": "Go wash your hands.",
    "ENDGAME": "Stop fighting the infection?\\n\\npress y or n.",
    "NEWGAME": "You can't start a new game\\nwhile in a network game.\\n\\npress a key.",
    "SAVEDEAD": "You can't save while\\nyou're in apoptosis!\\n\\npress a key.",
    "STSTR_DQDON": "Degreelessness Mode On",
    "STSTR_KFAADDED": "Very Happy Ammo Added",
    "E1TEXT": "",
    # obituaries
    "OB_ZOMBIE": "%o was infected by a virus.",
    "OB_SHOTGUY": "%o was poisoned by a bacterium.",
    "OB_IMP": "%o was smothered by a tumor cell.",
    "OB_IMPHIT": "%o was smothered by a tumor cell.",
    "OB_DEMONHIT": "%o was eaten by a parasite.",
    "OB_SPECTREHIT": "%o never saw the MHC-I-less tumor cell.",
    "OB_CACO": "%o inhaled fungal spores.",
    "OB_CACOHIT": "%o was overgrown by a fungus.",
    "OB_SKULL": "%o was injected by a phage.",
    "OB_BARON": "%o was overwhelmed by the tumor mass.",
    "OB_BARONHIT": "%o was absorbed by the tumor mass.",
    "OB_BARREL": "%o burst a toxin sac.",
}

THINGS = {
    # Thing number: {field: value}
    # (DeHackEd numbering: 1 player, 2 zombieman, 3 shotgun guy, 12 imp, 13 demon,
    #  14 spectre, 15 cacodemon, 16 baron, 19 lost soul)
    2: {"Hit points": 20},                 # VIRUS (zombieman)
    3: {"Hit points": 30},                 # BACTERIUM (shotgun guy)
    12: {"Hit points": 60},                # TUMOR CELL (imp)
    13: {"Hit points": 150},               # PARASITE (demon)
    14: {"Hit points": 150,                # TUMOR NO MHC-I (spectre)
         "Initial frame": remap(475), "First moving frame": remap(477), "Injury frame": remap(488),
         "Close attack frame": remap(485), "Death frame": remap(490), "Respawn frame": remap(496)},
    16: {"Hit points": 1000},              # TUMOR MASS (baron)
}


def dehacked():
    import os
    if os.environ.get("LYMPHO_TEST_BOSS"):
        THINGS[16] = {"Hit points": 1, "Initial frame": 542}  # test: dies at spawn -> A_BossDeath
    out = ["Patch File for DeHackEd v3.0", "# LYMPHODOOM", "Doom version = 21", "Patch format = 6", ""]
    for i, (frame, tics, action, nxt) in enumerate(SARG_STATES):
        n = NEW_FIRST + i
        out += ["Frame %d" % n, "Sprite number = %d" % SP00, "Sprite subnumber = %d" % frame,
                "Duration = %d" % tics, "Next frame = %d" % remap(nxt), ""]
    for t, fields in THINGS.items():
        out.append("Thing %d" % t)
        out += ["%s = %d" % (k, v) for k, v in fields.items()]
        out.append("")
    out += ["[CODEPTR]"]
    for i, (frame, tics, action, nxt) in enumerate(SARG_STATES):
        out.append("FRAME %d = %s" % (NEW_FIRST + i, action or "NULL"))
    out += ["", "[STRINGS]"]
    for k, v in STRINGS.items():
        out.append("%s = %s" % (k, v))
    out.append("")
    return ("\n".join(out)).encode("ascii")


def umapinfo():
    return b'''MAP E1M1
{
  levelname = "Lymph Node"
  label = "E1M1"
  episode = clear
  episode = "M_EPI1", "The Body", "b"
  next = "E1M2"
  music = "D_E1M1"
  levelpic = "WILV00"
  skytexture = "SKY1"
  partime = 150
}

MAP E1M2
{
  levelname = "Bloodstream"
  label = "E1M2"
  next = "E1M3"
  music = "D_E1M2"
  levelpic = "WILV01"
  skytexture = "SKY1"
  partime = 210
}

MAP E1M3
{
  levelname = "Tumor"
  label = "E1M3"
  music = "D_E1M3"
  levelpic = "WILV02"
  skytexture = "SKY1"
  partime = 270
  endpic = "CLEARPIC"
  bossaction = BaronOfHell, 11, 0
}
'''
