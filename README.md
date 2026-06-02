# Reddit Opportunity Analyzer

A CLI tool to scan `r/SomebodyMakeThis` and similar subreddits for unfulfilled project ideas, prioritized by upvotes and comments.

## Features
- Fetches top posts from any subreddit (default: `r/SomebodyMakeThis`).
- Filters out fulfilled requests (flair: "Completed").
- Prioritizes posts by score + comments (weighted).
- Outputs in markdown or JSON.

## Limitations
- **Reddit API Blocking**: Due to network restrictions, this tool uses HTML scraping (`old.reddit.com`). If blocked, it falls back to mock data for testing.
- **Dependencies**: Requires `requests` and `beautifulsoup4`. If `pip install` fails, use a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Usage
```bash
# Generate a markdown report for r/SomebodyMakeThis (top posts this month)
python reddit_analyzer.py --subreddit SomebodyMakeThis --time-filter month --output markdown

# Save to a file
python reddit_analyzer.py --output markdown --output-file report.md

# Output as JSON
python reddit_analyzer.py --output json
```

## Example Output
```markdown
| Priority | Title | Score | Comments | URL |
|----------|-------|-------|----------|-----|
| 1 | A CLI tool to batch-rename files using natural language | 420 | 84 | [Link](https://old.reddit.com/r/SomebodyMakeThis/comments/xyz) |
```

## Mock Data Mode
If Reddit is blocked, use mock data for testing:
```bash
MOCK_DATA=1 python reddit_analyzer.py
```