#!/usr/bin/env python3
"""
Reddit Opportunity Analyzer

A CLI tool to scan r/SomebodyMakeThis and similar subreddits for unfulfilled project ideas.
Prioritizes requests by upvotes/comments and outputs a curated list in markdown/json.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class RedditAnalyzer:
    """Core logic for fetching and analyzing Reddit posts."""

    def __init__(self, subreddit: str = "SomebodyMakeThis", time_filter: str = "month"):
        self.subreddit = subreddit
        self.time_filter = time_filter
        self.base_url = f"https://old.reddit.com/r/{subreddit}/top/?t={time_filter}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; FemirinsBot/1.0; +https://github.com/femirins)"
        }

    def fetch_posts(self) -> List[Dict]:
        """Fetch top posts from the subreddit using HTML scraping (fallback)."""
        if os.getenv("MOCK_DATA"):
            return self._mock_posts()
        
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            posts = []

            for post in soup.find_all("div", class_="thing"):
                title = post.find("a", class_="title").text.strip()
                url = post.find("a", class_="title")["href"]
                if not url.startswith("http"):
                    url = f"https://old.reddit.com{url}"
                
                score = int(post.find("div", class_="score unvoted").text.strip().split()[0])
                comments = int(post.find("a", class_="comments").text.strip().split()[0])
                flair = post.find("span", class_="linkflairlabel")
                flair = flair.text.strip() if flair else None

                # Skip fulfilled requests
                if flair == "Completed":
                    continue

                posts.append({
                    "title": title,
                    "url": url,
                    "score": score,
                    "comments": comments,
                    "flair": flair,
                })

            return posts
        except Exception as e:
            print(f"❌ Error fetching posts: {e}", file=sys.stderr)
            return self._mock_posts()

    def _mock_posts(self) -> List[Dict]:
        """Return mock data for testing when Reddit is blocked."""
        return [
            {
                "title": "A CLI tool to batch-rename files using natural language",
                "url": "https://old.reddit.com/r/SomebodyMakeThis/comments/xyz",
                "score": 420,
                "comments": 84,
                "flair": None,
            },
            {
                "title": "A local-first, ephemeral chat app for LAN parties",
                "url": "https://old.reddit.com/r/SomebodyMakeThis/comments/abc",
                "score": 310,
                "comments": 56,
                "flair": None,
            },
        ]

    def prioritize_posts(self, posts: List[Dict]) -> List[Dict]:
        """Prioritize posts by score + comments (weighted)."""
        for post in posts:
            post["priority_score"] = post["score"] + (post["comments"] * 0.5)
        return sorted(posts, key=lambda x: x["priority_score"], reverse=True)

    def to_markdown(self, posts: List[Dict]) -> str:
        """Convert posts to markdown table."""
        markdown = "# Reddit Opportunity Analyzer\n\n"
        markdown += f"**Subreddit**: r/{self.subreddit} | **Time Filter**: {self.time_filter}\n\n"
        markdown += "| Priority | Title | Score | Comments | URL |\n"
        markdown += "|----------|-------|-------|----------|-----|\n"

        for idx, post in enumerate(posts, 1):
            markdown += (
                f"| {idx} | {post['title']} | {post['score']} | {post['comments']} | "
                f"[Link]({post['url']}) |\n"
            )

        markdown += f"\n*Generated at {datetime.now().isoformat()}*\n"
        return markdown

    def to_json(self, posts: List[Dict]) -> str:
        """Convert posts to JSON."""
        return json.dumps(posts, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Reddit Opportunity Analyzer")
    parser.add_argument(
        "--subreddit",
        default="SomebodyMakeThis",
        help="Subreddit to analyze (default: SomebodyMakeThis)",
    )
    parser.add_argument(
        "--time-filter",
        default="month",
        choices=["hour", "day", "week", "month", "year", "all"],
        help="Time filter for top posts (default: month)",
    )
    parser.add_argument(
        "--output",
        default="markdown",
        choices=["markdown", "json"],
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output-file",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    analyzer = RedditAnalyzer(args.subreddit, args.time_filter)
    posts = analyzer.fetch_posts()
    prioritized_posts = analyzer.prioritize_posts(posts)

    if args.output == "markdown":
        output = analyzer.to_markdown(prioritized_posts)
    else:
        output = analyzer.to_json(prioritized_posts)

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()