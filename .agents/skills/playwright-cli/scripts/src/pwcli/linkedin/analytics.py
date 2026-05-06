#!/usr/bin/env python3
"""
LinkedIn Company Page Analytics Scraper and Visualizer

This script uses playwright-cli to scrape LinkedIn company page posts
and generates a visualization of engagement metrics.

Usage:
    uv run linkedin-analytics

Output:
    - CSV file with post data
    - PNG image with engagement visualization
    - Prints path to the generated image
"""

import re
import csv
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


# Configuration
LINKEDIN_URL = "https://www.linkedin.com/company/110597504/admin/page-posts/published/"
MAX_POSTS = 10
OUTPUT_DIR = Path.home() / ".linkedin-analytics"


@dataclass
class TreeNode:
    """A node in the parsed YAML tree."""
    indent: int
    tag: str
    content: str
    attrs: Dict[str, str] = field(default_factory=dict)
    children: List['TreeNode'] = field(default_factory=list)
    parent: Optional['TreeNode'] = None


@dataclass
class Post:
    """A LinkedIn post with analytics."""
    post_number: str = ""
    date: str = ""
    author: str = "Divyam Dhadwal"
    content: str = ""
    impressions: int = 0
    engagements: int = 0
    engagement_rate: float = 0.0
    clicks: int = 0
    click_through_rate: float = 0.0
    reactions: int = 0
    comments: int = 0
    reposts: int = 0
    is_ad: bool = False


def parse_line(line: str) -> Optional[TreeNode]:
    """Parse a single YAML line into a TreeNode."""
    stripped = line.rstrip()
    if not stripped or stripped.startswith('#'):
        return None
    
    indent_match = re.match(r'^(\s*)-', stripped)
    if not indent_match:
        return None
    
    indent = len(indent_match.group(1))
    rest = stripped[indent + 2:].strip()
    
    if not rest:
        return None
    
    node = TreeNode(indent=indent, tag="", content="", attrs={})
    
    # heading "..." [level=N] [ref=eNNN]
    m = re.match(r'^heading\s+"([^"]+)"(?:\s*\[([^\]]+)\])*', rest)
    if m:
        node.tag = "heading"
        node.content = m.group(1)
        return node
    
    # generic [ref=eNNN]: "value" or generic [ref=eNNN]: value
    m = re.match(r'^generic\s+\[ref=([^\]]+)\](?:\s*\[([^\]]+)\])?(?:\s*:\s*(.+))?$', rest)
    if m:
        node.tag = "generic"
        node.attrs['ref'] = m.group(1)
        if m.group(3):
            node.content = m.group(3).strip().strip('"')
        return node
    
    # list [ref=eNNN]:
    m = re.match(r'^list\s+\[ref=([^\]]+)\]:$', rest)
    if m:
        node.tag = "list"
        node.attrs['ref'] = m.group(1)
        return node
    
    # listitem [ref=eNNN]:
    m = re.match(r'^listitem\s+\[ref=([^\]]+)\]:$', rest)
    if m:
        node.tag = "listitem"
        node.attrs['ref'] = m.group(1)
        return node
    
    # text: content
    m = re.match(r'^text:\s*(.+)$', rest)
    if m:
        node.tag = "text"
        node.content = m.group(1).strip().strip('"')
        return node
    
    # link "..." [ref=eNNN]
    m = re.match(r'^link\s+"([^"]+)"\s+\[ref=([^\]]+)\]', rest)
    if m:
        node.tag = "link"
        node.content = m.group(1)
        return node
    
    # button "..." [ref=eNNN]
    m = re.match(r'^button\s+"([^"]+)"\s+\[ref=([^\]]+)\]', rest)
    if m:
        node.tag = "button"
        node.content = m.group(1)
        return node
    
    # article [ref=eNNN]:
    m = re.match(r'^article\s+\[ref=([^\]]+)\]:$', rest)
    if m:
        node.tag = "article"
        node.attrs['ref'] = m.group(1)
        return node
    
    return None


def build_tree(lines: List[str]) -> List[TreeNode]:
    """Build a tree from parsed lines using indentation."""
    nodes = []
    stack = []
    
    for line in lines:
        node = parse_line(line)
        if not node:
            continue
        
        while stack and stack[-1].indent >= node.indent:
            stack.pop()
        
        if stack:
            node.parent = stack[-1]
            stack[-1].children.append(node)
        else:
            nodes.append(node)
        
        stack.append(node)
    
    return nodes


def find_nodes(root: TreeNode, predicate: Callable[[TreeNode], bool]) -> List[TreeNode]:
    """Find all nodes matching predicate using DFS."""
    results = []
    
    def dfs(node: TreeNode):
        if predicate(node):
            results.append(node)
        for child in node.children:
            dfs(child)
    
    dfs(root)
    return results


def find_first_node(root: TreeNode, predicate: Callable[[TreeNode], bool]) -> Optional[TreeNode]:
    """Find first node matching predicate using DFS."""
    if predicate(root):
        return root
    for child in root.children:
        result = find_first_node(child, predicate)
        if result:
            return result
    return None


def get_post_sections(tree: List[TreeNode]) -> List[TreeNode]:
    """Find all post section root nodes."""
    posts = []
    
    def find_post_roots(nodes: List[TreeNode]):
        for node in nodes:
            if node.tag == 'heading' and 'Feed post number' in node.content:
                posts.append(node)
            else:
                find_post_roots(node.children)
    
    find_post_roots(tree)
    return posts


def get_section_root(node: TreeNode) -> TreeNode:
    """Get the section container for a heading node."""
    current = node
    while current.parent and current.parent.tag in ('generic', 'listitem'):
        current = current.parent
    return current


def extract_date(post_root: TreeNode) -> str:
    """Extract date from post section."""
    date_nodes = find_nodes(post_root, lambda n: 
        n.tag == 'text' and bool(re.search(r'(\d+[hdwmy]|\d{1,2}/\d{1,2}/\d{4})\s*•', n.content)))
    
    if date_nodes:
        match = re.search(r'(\d+[hdwmy]|\d{1,2}/\d{1,2}/\d{4})\s*•', date_nodes[0].content)
        if match:
            return match.group(1)
    
    date_nodes = find_nodes(post_root, lambda n:
        n.tag == 'text' and bool(re.search(r'•\s*(\d{1,2}/\d{1,2}/\d{4})', n.content)))
    
    if date_nodes:
        match = re.search(r'•\s*(\d{1,2}/\d{1,2}/\d{4})', date_nodes[0].content)
        if match:
            return match.group(1)
    
    return ""


def extract_author(post_root: TreeNode) -> str:
    """Extract author from post section."""
    author_nodes = find_nodes(post_root, lambda n: 
        n.tag == 'generic' and 'By ' in n.content)
    
    if author_nodes:
        match = re.search(r'By\s+(.+)', author_nodes[0].content)
        if match:
            return match.group(1).strip()
    
    link_nodes = find_nodes(post_root, lambda n:
        n.tag == 'link' and '/in/' in (n.content or ''))
    
    if link_nodes:
        return link_nodes[0].content
    
    return "Divyam Dhadwal"


def extract_content(post_root: TreeNode) -> str:
    """Extract post content, stopping before analytics section."""
    text_parts = []
    
    def collect_content(node: TreeNode) -> bool:
        if node.tag == 'text' and 'Organic impressions:' in node.content:
            return False
        if node.tag == 'heading' and 'Post performance' in node.content:
            return False
        if node.tag == 'heading' and 'Hide results' in node.content:
            return False
        
        if node.tag == 'text' and node.content:
            text = node.content.strip()
            if (len(text) > 15 and 
                not text.startswith('http') and
                not text.startswith('By ') and
                'followers' not in text.lower() and
                text != 'SelfHost' and
                '•' not in text):
                text_parts.append(text)
        
        for child in node.children:
            if not collect_content(child):
                return False
        
        return True
    
    collect_content(post_root)
    return ' '.join(text_parts)


def extract_analytics(post_root: TreeNode) -> Dict[str, str]:
    """Extract analytics from post section."""
    metrics = {}
    
    perf_heading = find_first_node(post_root, lambda n: 
        n.tag == 'heading' and 'Post performance' in n.content)
    
    if not perf_heading:
        return metrics
    
    list_node = find_first_node(post_root, lambda n: 
        n.tag == 'list' and n.parent and any(
            'Post performance' in (c.content or '') or 
            'Targeted to' in (c.content or '')
            for c in n.parent.children if c.tag == 'heading'
        ))
    
    if not list_node:
        all_lists = find_nodes(post_root, lambda n: n.tag == 'list')
        for lst in all_lists:
            for item in lst.children:
                if item.tag == 'listitem':
                    generic_children = [c for c in item.children if c.tag == 'generic']
                    for gc in generic_children:
                        if any(label in (gc.content or '') for label in 
                               ['Impressions', 'Engagements', 'Engagement rate', 
                                'Click-through rate', 'Clicks', 'Reaction', 'Comment', 'Repost']):
                            list_node = lst
                            break
                if list_node:
                    break
            if list_node:
                break
    
    if not list_node:
        return metrics
    
    for item in list_node.children:
        if item.tag != 'listitem':
            continue
        
        generic_children = [c for c in item.children if c.tag == 'generic']
        if len(generic_children) < 2:
            continue
        
        value_node = generic_children[0]
        label_node = generic_children[1]
        
        value_raw = value_node.content.strip()
        label = label_node.content.strip()
        
        if not value_raw or not label:
            continue
        
        value = value_raw.strip('"').replace(',', '')
        
        label_lower = label.lower()
        if 'engagement rate' in label_lower:
            metrics['engagement_rate'] = value
        elif 'engagements' in label_lower:
            metrics['engagements'] = value
        elif 'impressions' in label_lower:
            metrics['impressions'] = value
        elif 'click-through rate' in label_lower:
            metrics['click_through_rate'] = value
        elif 'clicks' in label_lower:
            metrics['clicks'] = value
        elif 'reaction' in label_lower:
            metrics['reactions'] = value
        elif 'comment' in label_lower:
            metrics['comments'] = value
        elif 'repost' in label_lower:
            metrics['reposts'] = value
    
    return metrics


def is_ad_post(post_root: TreeNode) -> bool:
    """Check if this is an ad/sponsored post."""
    perf_heading = find_first_node(post_root, lambda n: 
        n.tag == 'heading' and 'Post performance' in n.content)
    return perf_heading is None


def extract_posts_from_tree(tree: List[TreeNode]) -> List[Post]:
    """Extract all posts from the parsed tree."""
    posts = []
    post_sections = get_post_sections(tree)
    
    for section_heading in post_sections:
        post = Post()
        
        match = re.search(r'Feed post number (\d+)', section_heading.content)
        if match:
            post.post_number = match.group(1)
        
        section_root = get_section_root(section_heading)
        
        post.date = extract_date(section_root)
        post.author = extract_author(section_root)
        post.is_ad = is_ad_post(section_root)
        post.content = extract_content(section_root)
        
        metrics = extract_analytics(section_root)
        
        # Convert to proper types
        try:
            post.impressions = int(metrics.get('impressions', '0'))
        except ValueError:
            post.impressions = 0
            
        try:
            post.engagements = int(metrics.get('engagements', '0'))
        except ValueError:
            post.engagements = 0
            
        try:
            rate_str = metrics.get('engagement_rate', '0%').replace('%', '')
            post.engagement_rate = float(rate_str)
        except ValueError:
            post.engagement_rate = 0.0
            
        try:
            post.clicks = int(metrics.get('clicks', '0'))
        except ValueError:
            post.clicks = 0
            
        try:
            ctr_str = metrics.get('click_through_rate', '0%').replace('%', '')
            post.click_through_rate = float(ctr_str)
        except ValueError:
            post.click_through_rate = 0.0
            
        try:
            post.reactions = int(metrics.get('reactions', '0'))
        except ValueError:
            post.reactions = 0
            
        try:
            post.comments = int(metrics.get('comments', '0'))
        except ValueError:
            post.comments = 0
            
        try:
            post.reposts = int(metrics.get('reposts', '0'))
        except ValueError:
            post.reposts = 0
        
        posts.append(post)
    
    return posts


def scrape_linkedin_posts() -> List[Post]:
    """Scrape LinkedIn posts using playwright-cli."""
    print("🌐 Opening LinkedIn page...")
    
    # Open browser and navigate
    subprocess.run(
        ["playwright-cli", "open", LINKEDIN_URL],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("📊 Expanding analytics sections...")
    
    # Click all Preview results buttons
    for _ in range(3):  # Multiple rounds to catch all
        result = subprocess.run(
            ["playwright-cli", "--raw", "eval", 
             "async () => { const buttons = document.querySelectorAll('button'); let clicked = 0; for (const btn of buttons) { if (btn.textContent && btn.textContent.toLowerCase().includes('preview results')) { try { btn.scrollIntoView({behavior: 'instant', block: 'center'}); btn.click(); clicked++; await new Promise(r => setTimeout(r, 800)); } catch(e) {} } } return clicked; }"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Scroll down to load more
        subprocess.run(
            ["playwright-cli", "mousewheel", "0", "1000"],
            capture_output=True,
            timeout=15
        )
    
    print("📸 Taking snapshot...")
    
    # Take snapshot
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        snapshot_path = f.name
    
    subprocess.run(
        ["playwright-cli", "snapshot", f"--filename={snapshot_path}"],
        capture_output=True,
        timeout=45
    )
    
    print("🔍 Parsing snapshot...")
    
    # Parse snapshot
    lines = Path(snapshot_path).read_text().split('\n')
    tree = build_tree(lines)
    posts = extract_posts_from_tree(tree)
    
    # Filter out ads and limit to MAX_POSTS
    real_posts = [p for p in posts if not p.is_ad][:MAX_POSTS]
    
    # Cleanup
    Path(snapshot_path).unlink()
    
    # Close browser
    subprocess.run(
        ["playwright-cli", "close"],
        capture_output=True,
        timeout=15
    )
    
    return real_posts


def create_visualization(posts: List[Post]) -> Path:
    """Create a visualization of post analytics."""
    if not posts:
        print("❌ No posts to visualize")
        return None
    
    # Prepare data
    df = pd.DataFrame([
        {
            'Post': f"#{p.post_number}",
            'Date': p.date,
            'Impressions': p.impressions,
            'Engagement Rate (%)': p.engagement_rate,
            'CTR (%)': p.click_through_rate,
            'Reactions': p.reactions,
            'Reposts': p.reposts,
            'Engagements': p.engagements,
        }
        for p in posts
    ])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('LinkedIn Company Page Analytics Dashboard\nSelfHost - Last 10 Posts', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Color palette
    colors = sns.color_palette("husl", len(df))
    
    # 1. Engagement Rate by Post
    ax1 = axes[0, 0]
    bars1 = ax1.bar(df['Post'], df['Engagement Rate (%)'], color=colors, alpha=0.8, edgecolor='black')
    ax1.set_title('Engagement Rate by Post', fontweight='bold', pad=10)
    ax1.set_ylabel('Engagement Rate (%)')
    ax1.set_xlabel('Post')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 2. Click-Through Rate by Post
    ax2 = axes[0, 1]
    bars2 = ax2.bar(df['Post'], df['CTR (%)'], color=colors, alpha=0.8, edgecolor='black')
    ax2.set_title('Click-Through Rate by Post', fontweight='bold', pad=10)
    ax2.set_ylabel('CTR (%)')
    ax2.set_xlabel('Post')
    ax2.grid(axis='y', alpha=0.3)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 3. Impressions vs Engagements Scatter
    ax3 = axes[1, 0]
    scatter = ax3.scatter(df['Impressions'], df['Engagements'], 
                         s=df['Reactions']*50, c=colors, alpha=0.7, edgecolors='black', linewidth=2)
    ax3.set_title('Impressions vs Engagements\n(Bubble size = Reactions)', fontweight='bold', pad=10)
    ax3.set_xlabel('Impressions')
    ax3.set_ylabel('Engagements')
    ax3.grid(True, alpha=0.3)
    
    # Add post labels
    for i, row in df.iterrows():
        ax3.annotate(f"#{posts[i].post_number}", 
                    (row['Impressions'], row['Engagements']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, fontweight='bold')
    
    # 4. Reactions and Reposts
    ax4 = axes[1, 1]
    x = np.arange(len(df))
    width = 0.35
    
    bars3 = ax4.bar(x - width/2, df['Reactions'], width, label='Reactions', 
                   color='#3498db', alpha=0.8, edgecolor='black')
    bars4 = ax4.bar(x + width/2, df['Reposts'], width, label='Reposts', 
                   color='#e74c3c', alpha=0.8, edgecolor='black')
    
    ax4.set_title('Reactions vs Reposts', fontweight='bold', pad=10)
    ax4.set_ylabel('Count')
    ax4.set_xlabel('Post')
    ax4.set_xticks(x)
    ax4.set_xticklabels(df['Post'])
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    
    # Save image
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = OUTPUT_DIR / f"linkedin_analytics_{timestamp}.png"
    
    plt.savefig(image_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return image_path


def export_to_csv(posts: List[Post]) -> Path:
    """Export posts to CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"linkedin_posts_{timestamp}.csv"
    
    fieldnames = [
        'Post Number', 'Date', 'Author', 'Content',
        'Impressions', 'Engagements', 'Engagement Rate (%)',
        'Clicks', 'CTR (%)', 'Reactions', 'Comments', 'Reposts'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for post in posts:
            content = post.content[:300] + '...' if len(post.content) > 300 else post.content
            writer.writerow({
                'Post Number': post.post_number,
                'Date': post.date,
                'Author': post.author,
                'Content': content,
                'Impressions': post.impressions,
                'Engagements': post.engagements,
                'Engagement Rate (%)': post.engagement_rate,
                'Clicks': post.clicks,
                'CTR (%)': post.click_through_rate,
                'Reactions': post.reactions,
                'Comments': post.comments,
                'Reposts': post.reposts
            })
    
    return csv_path


def main():
    """Main entry point."""
    print("="*70)
    print("🔗 LinkedIn Company Page Analytics Scraper")
    print("="*70)
    print()
    
    try:
        # Scrape posts
        posts = scrape_linkedin_posts()
        
        if not posts:
            print("❌ No posts found")
            return 1
        
        print(f"✅ Found {len(posts)} posts")
        print()
        
        # Display summary
        print("📊 Post Summary:")
        print("-" * 70)
        for post in posts:
            print(f"Post #{post.post_number} | {post.date:>6} | "
                  f"{post.impressions:>5} imp | {post.engagement_rate:>5.1f}% ER | "
                  f"{post.click_through_rate:>5.1f}% CTR | {post.reactions:>2} reacts")
        print()
        
        # Export to CSV
        csv_path = export_to_csv(posts)
        print(f"📁 CSV exported: {csv_path}")
        
        # Create visualization
        print("📈 Creating visualization...")
        image_path = create_visualization(posts)
        
        if image_path:
            print(f"🖼️  Image saved: {image_path}")
            print()
            print("="*70)
            print("✨ Done! Open the image with:")
            print(f"   open {image_path}")
            print("="*70)
        
        return 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout: Browser operation took too long")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
