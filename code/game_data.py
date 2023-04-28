horizontal_tile_number = 30
vertical_tile_number = 16
tile_size = 64
screen_width = 1920
screen_height = 1080

maps = {
    'map0': {
        'terrain': '../map/map0/map0_terrain.csv',
        'power': '../map/map0/map0_power.csv',
        'palm_fg': '../map/map0/map0_palm_fg.csv',
        'palm_bg': '../map/map0/map0_palm_bg.csv',
        'crate': '../map/map0/map0_crates.csv',
        'spawn': '../map/map0/map0_spawn.csv',
        'grass': '../map/map0/map0_grass.csv'
    },

    'map1': {
        'terrain': '../map/map1/map1_terrain.csv',
        'power': '../map/map1/map1_power.csv',
        'palm_fg': '../map/map1/map1_palm_fg.csv',
        'palm_bg': '../map/map1/map1_palm_bg.csv',
        'crate': '../map/map1/map1_crates.csv',
        'grass': '../map/map1/map1_grass.csv'
    }
}

player_sprites = {
    'jump_dust': '../assets/character/dust_particles/jump/',
    'land_dust': '../assets/character/dust_particles/land/',
    'run_dust': '../assets/character/dust_particles/run/',
    'tag': '../assets/character/tagged.png'
}

map_sprites = {
    'timer': '../assets/decoration/timerbg.png',
    'terrain': '../assets/terrain/terrain_tiles.png',
    'grass': '../assets/decoration/grass/grass.png',
    'crate': '../assets/terrain/crate.png',
    'silver': '../assets/coins/silver/',
    'gold': '../assets/coins/gold',
    'palm_small': '../assets/terrain/palm_small/',
    'palm_large': '../assets/terrain/palm_large/',
    'palm_bg': '../assets/terrain/palm_bg',
    'sky_top': '../assets/decoration/sky/sky_top.png',
    'sky_middle': '../assets/decoration/sky/sky_middle.png',
    'sky_bottom': '../assets/decoration/sky/sky_bottom.png',
    'clouds': '../assets/decoration/clouds/'
}

ui_sprites = {
    'text_input': '../assets/ui/elements/text_input.png',
    'chat_window': '../assets/ui/elements/chat_box.png',
    'chat_input': '../assets/ui/elements/chat_input.png',

    'buttons': {
        'login': '../assets/ui/buttons/login.png',
        'signup': '../assets/ui/buttons/signup.png',
        'join': '../assets/ui/buttons/join.png',
        'back': '../assets/ui/buttons/back.png',
        'logout': '../assets/ui/buttons/logout.png',
        'close': '../assets/ui/buttons/close.png',
        'create': '../assets/ui/buttons/create.png',
        'left': '../assets/ui/buttons/left_arrow.png',
        'right': '../assets/ui/buttons/right_arrow.png',
        'up': '../assets/ui/buttons/up_arrow.png',
        'down': '../assets/ui/buttons/down_arrow.png',
        'start_active': '../assets/ui/buttons/start.png',
        'start_inactive': '../assets/ui/buttons/start_inactive.png',
        'ready': '../assets/ui/buttons/ready.png',
        'unready': '../assets/ui/buttons/unready.png',
        'exit': '../assets/ui/buttons/exit.png',
        'send_chat': '../assets/ui/buttons/send_chat.png',
        'lobby': '../assets/ui/buttons/lobby.png'
    },

    'bg': {
        'home': '../assets/ui/menus/home.png',
        'lobby': '../assets/ui/menus/lobby.png',
        'end_bg': '../assets/end_screen.png',
        'end_fg': '../assets/ui/menus/end.png',
        'end_default': '../assets/ui/elements/bg.png'
    }
}

button_pos = {
    'home_default_top': (804, 630),
    'home_default_bot': (804, 792),
    'home_input_top': (774, 579),
    'home_input_mid': (774, 713),
    'home_input_bot': (804, 847),
    'home_default_inp': (774, 630),
    'lobby_left_arrow': (1431, 568),
    'lobby_right_arrow': (1793, 568),
    'lobby_default_top': (1481, 750),
    'lobby_default_bot': (1481, 861),
    'lobby_room_id': (812, 187),
    'lobby_chat_input': (656, 905),
    'lobby_chat_display': (687, 416),
    'lobby_send_chat': (1183, 898),
    'lobby_chat_down': (1183, 820),
    'lobby_chat_up': (1183, 354),
    'end_default_btn': (1321, 812),
    'end_default_txt': (1402, 542),
    'end_default_sprite': (1410, 568),
    'back_btn': (23, 18),
    'close_btn': (1767, 18),
    'logout_btn': (1626, 18)
}

map_thumbnails = {
    'pos': (1508, 529),
    'path': {
        0: '../assets/ui/map_thumbnails/map_0.png',
        1: '../assets/ui/map_thumbnails/map_1.png'
    }
}

music = {
    'lobby': '../assets/music/8Bit Adventure Loop.wav',
    'game': '../assets/music/Bone Zone Loop.wav'
}

sound = {
    'back': '../assets/sound_effects/back_style_2_003.wav',
    'click': '../assets/sound_effects/confirm_style_2_002.wav',
    'type': '../assets/sound_effects/Wood Block2.wav',
    'jump': '../assets/sound_effects/Jump.wav',
    'tag': '../assets/sound_effects/Explosion.wav',
    'error': '../assets/sound_effects/error_style_2_001.wav'
}

error = {
    'error_path': '../assets/ui/elements/error.png',
    'error_pos': {
        'home_start': (1663, 506),
        'home_end': (1383, 506)
    },
    'error_code': {
        500: "Invalid request",
        501: "Server error",
        400: "Both fields required",
        401: "User doesn't exist",
        402: "Username exists",
        403: "Invalid credentials",
        404: "Unauthorized request",
        405: "Malformed request",
        300: "Room doesn't exist",
        301: "Room id required"
    }
}
