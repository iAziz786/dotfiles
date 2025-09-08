return {
  "romus204/go-tagger.nvim",
  config = function()
    require("go-tagger").setup({
      skip_private = true, -- Skip unexported fields (starting with lowercase)
    })
  end,
}
