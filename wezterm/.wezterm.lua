local wezterm = require("wezterm")

local config = wezterm.config_builder()

config.font = wezterm.font("JetBrains Mono")
config.font_size = 16

-- Theme
config.color_scheme = "Catppuccin Mocha"

config.window_background_opacity = 0.9
config.macos_window_background_blur = 10

return config
