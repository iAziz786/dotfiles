-- markdownlint-cli2 stops config discovery at the git worktree root, so the
-- global ~/.markdownlint.json is never picked up inside repos. Pass it
-- explicitly to both consumers (nvim-lint diagnostics, conform formatting).
local markdownlint_config = vim.fn.expand("~/.markdownlint.json")

return {
  {
    "mfussenegger/nvim-lint",
    optional = true,
    opts = function(_, opts)
      opts.linters = opts.linters or {}
      opts.linters["markdownlint-cli2"] = vim.tbl_deep_extend("force", opts.linters["markdownlint-cli2"] or {}, {
        args = { "-", "--config", markdownlint_config },
      })
    end,
  },
  {
    "stevearc/conform.nvim",
    optional = true,
    opts = function(_, opts)
      opts.formatters = opts.formatters or {}
      opts.formatters["markdownlint-cli2"] = vim.tbl_deep_extend("force", opts.formatters["markdownlint-cli2"] or {}, {
        args = { "--fix", "--config", markdownlint_config, "$FILENAME" },
      })
    end,
  },
}
