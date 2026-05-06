# LinkedIn Analytics Script

A comprehensive tool for scraping LinkedIn company page post analytics and generating visualizations.

## Features

- 🤖 Automated browser control via playwright-cli
- 📊 Scrapes last 10 posts (excluding ads)
- 📈 Generates 4-panel visualization dashboard
- 💾 Exports data to CSV
- 🖼️ Creates PNG image with engagement metrics

## Metrics Tracked

- Impressions
- Engagement Rate (%)
- Click-Through Rate (%)
- Reactions
- Reposts
- Comments
- Engagements

## Installation

```bash
cd /Users/aziz/Documents/github.com/iAziz786/dotfiles/.agents/skills/playwright-cli/scripts
uv sync
```

## Usage

```bash
uv run linkedin-analytics
```

The script will:
1. Open LinkedIn company page
2. Scrape post data
3. Generate visualization
4. Export CSV
5. Print path to generated image

Open the image with:
```bash
open ~/.linkedin-analytics/linkedin_analytics_YYYYMMDD_HHMMSS.png
```

## Output

- **CSV**: `~/.linkedin-analytics/linkedin_posts_YYYYMMDD_HHMMSS.csv`
- **Image**: `~/.linkedin-analytics/linkedin_analytics_YYYYMMDD_HHMMSS.png`

## Visualization Dashboard

The generated image contains 4 charts:
1. **Engagement Rate by Post** - Bar chart showing engagement rates
2. **Click-Through Rate by Post** - Bar chart showing CTR
3. **Impressions vs Engagements** - Scatter plot with bubble size = reactions
4. **Reactions vs Reposts** - Grouped bar chart

## Configuration

Edit the script to change:
- `LINKEDIN_URL` - Company page URL
- `MAX_POSTS` - Number of posts to scrape (default: 10)
- `OUTPUT_DIR` - Where to save files (default: `~/.linkedin-analytics`)

## Requirements

- Python 3.10+
- playwright-cli (must be installed and configured)
- LinkedIn account with company page admin access
- UV package manager

## How It Works

1. **Browser Automation**: Uses playwright-cli to control browser
2. **Tree Parsing**: Parses YAML accessibility snapshots using tree-based parser
3. **Data Extraction**: Extracts post content, dates, and analytics
4. **Ad Detection**: Automatically filters out sponsored/ad posts
5. **Visualization**: Uses matplotlib/seaborn to create dashboard

## Troubleshooting

**Timeout errors**: LinkedIn may load slowly. The script has built-in retries.

**No posts found**: Ensure you're logged into LinkedIn and have admin access to the company page.

**Missing analytics**: Click "Preview results" buttons manually if needed before running.

## License

MIT
