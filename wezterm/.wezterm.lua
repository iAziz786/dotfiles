local wezterm = require("wezterm")
local config = wezterm.config_builder()
local act = wezterm.action

config.font = wezterm.font("JetBrains Mono")
if wezterm.target_triple:find("darwin") then
	config.font_size = 16
else
	config.window_decorations = "RESIZE"
	config.font_size = 14
end

-- Theme
config.color_scheme = "Catppuccin Mocha"

config.window_background_opacity = 0.9
config.macos_window_background_blur = 10

-- Keybinding Ctrl + f runs zoxide's fzf jumper (zi) in the current pane
config.keys = {
	{ key = "f", mods = "CTRL", action = act.SendString("zi\n") },
}

return config
