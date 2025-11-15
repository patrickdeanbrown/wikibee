# Python API Tutorial

This tutorial shows how to use wikibee programmatically in your Python applications. You'll learn to extract Wikipedia content, process it, and integrate wikibee into larger workflows.

## Table of Contents
- [Installation and Imports](#installation-and-imports)
- [Basic Article Extraction](#basic-article-extraction)
- [Search Functionality](#search-functionality)
- [Text Processing](#text-processing)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Integration Examples](#integration-examples)

## Installation and Imports

### Installing wikibee

```bash
# Install wikibee as a Python package
pip install wikibee
# or
pipx install wikibee
```

### Basic Imports

```python
# Core functions
from wikibee import (
    extract_wikipedia_text,
    make_tts_friendly,
    sanitize_filename,
    write_text_file
)

# Exception handling
from wikibee import (
    NetworkError,
    APIError,
    NotFoundError,
    DisambiguationError
)

# Optional: Access to internal modules
from wikibee.client import WikiClient
```

## Basic Article Extraction

### Search and Extract

```python
from wikibee import extract_wikipedia_text
from wikibee.client import WikiClient

client = WikiClient()
results = client.search_articles("Albert Einstein", limit=1)

if not results:
    raise SystemExit("No results found")

url = results[0]["url"]
text, title = extract_wikipedia_text(url)

print(f"Title: {title}")
print(f"Content length: {len(text)} characters")
print(f"First 200 chars: {text[:200]}...")
```

### Extract by Direct URL

```python
# Extract from a specific Wikipedia URL
url = "https://en.wikipedia.org/wiki/Quantum_mechanics"
text, title = extract_wikipedia_text(url)

print(f"Extracted: {title}")
```

### Extract Lead Section Only

```python
# Get just the introduction for faster processing
text, title = extract_wikipedia_text("Machine Learning", lead_only=True)

print(f"Lead section length: {len(text)} characters")
```

## Search Functionality

### Using the WikiClient

```python
from wikibee.client import WikiClient

# Create a client instance
client = WikiClient()

# Search for articles
search_results = client.search_articles("quantum physics", limit=5)

print("Search results:")
for i, result in enumerate(search_results, 1):
    print(f"{i}. {result['title']}")
    print(f"   {result['description']}")
    print(f"   URL: {result['url']}")
```

### Handling Search Results

```python
from wikibee.client import WikiClient

def find_best_match(search_term, max_results=10):
    client = WikiClient()
    results = client.search_articles(search_term, limit=max_results)
    
    if not results:
        return None, None
    
    # Return the first (most relevant) result
    best_match = results[0]
    return best_match['url'], best_match['title']

# Usage
url, title = find_best_match("artificial intelligence")
if url:
    text, title = extract_wikipedia_text(url)
    print(f"Found and extracted: {title}")
```

## Text Processing

### Generate TTS-Friendly Text

```python
from wikibee import extract_wikipedia_text, make_tts_friendly

# Extract article
text, title = extract_wikipedia_text("Shakespeare")

# Create TTS-friendly version
tts_text = make_tts_friendly(f"# {title}\n\n{text}")

print("Original length:", len(text))
print("TTS version length:", len(tts_text))
```

### Custom TTS Processing

```python
from wikibee import make_tts_friendly

def create_audio_script(title, content, heading_prefix="Section"):
    """Create a well-formatted TTS script."""
    
    # Combine title and content
    full_text = f"# {title}\n\n{content}"
    
    # Convert to TTS-friendly format
    tts_text = make_tts_friendly(full_text, heading_prefix=heading_prefix)
    
    # Add introduction
    intro = f"This is an article about {title}.\n\n"
    
    return intro + tts_text

# Usage
text, title = extract_wikipedia_text("Marie Curie")
script = create_audio_script(title, text)
```

### Filename Sanitization

```python
from wikibee import sanitize_filename

# Clean filenames for safe file operations
titles = [
    "C++ (programming language)",
    "Paris, France", 
    'File with "quotes" and /slashes/',
    "Title: With Colons"
]

for title in titles:
    clean = sanitize_filename(title)
    print(f"'{title}' -> '{clean}'")
```

Output:
```
'C++ (programming language)' -> 'c_programming_language'
'Paris, France' -> 'paris_france'
'File with "quotes" and /slashes/' -> 'file_with_quotes_and_slashes'
'Title: With Colons' -> 'title_with_colons'
```

## Error Handling

### Comprehensive Error Handling

```python
from wikibee import (
    extract_wikipedia_text,
    NetworkError,
    APIError,
    NotFoundError,
    DisambiguationError
)

def safe_extract(search_term, retries=3):
    """Extract article with comprehensive error handling."""
    
    for attempt in range(retries):
        try:
            text, title = extract_wikipedia_text(
                search_term, 
                timeout=30,  # Longer timeout
                lead_only=False
            )
            
            if text:
                return text, title
            else:
                print(f"No content returned for '{search_term}'")
                return None, None
                
        except NetworkError as e:
            print(f"Network error (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                raise
                
        except NotFoundError:
            print(f"Article not found: '{search_term}'")
            return None, None
            
        except DisambiguationError as e:
            print(f"Multiple matches found for '{search_term}': {e}")
            # Could implement logic to choose from disambiguation options
            return None, None
            
        except APIError as e:
            print(f"Wikipedia API error: {e}")
            return None, None

# Usage
text, title = safe_extract("quantum mechanics")
if text:
    print(f"Successfully extracted: {title}")
```

### Specific Error Scenarios

```python
# Handle disambiguation pages
try:
    text, title = extract_wikipedia_text("Mercury")
except DisambiguationError as e:
    print("Disambiguation page found. Available options:")
    # In a real app, you might present these options to the user
    print(str(e))

# Handle network timeouts
try:
    text, title = extract_wikipedia_text("Large Article", timeout=5)
except NetworkError as e:
    print(f"Network timeout: {e}")
    # Retry with longer timeout
    text, title = extract_wikipedia_text("Large Article", timeout=30)
```

## Advanced Usage

### Batch Processing

```python
from wikibee import extract_wikipedia_text, make_tts_friendly, write_text_file
import os
from pathlib import Path

def batch_extract(topics, output_dir="output", create_tts=True):
    """Extract multiple articles and organize them."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    for topic in topics:
        try:
            print(f"Processing: {topic}")
            
            # Extract article
            text, title = extract_wikipedia_text(topic)
            
            if not text:
                print(f"  Failed to extract: {topic}")
                continue
                
            # Create safe filename
            filename = sanitize_filename(title)
            
            # Save markdown
            md_path = output_path / f"{filename}.md"
            full_content = f"# {title}\n\n{text}"
            write_text_file(str(md_path), str(output_path), full_content)
            
            # Save TTS version if requested
            if create_tts:
                tts_text = make_tts_friendly(full_content)
                txt_path = output_path / f"{filename}.txt"
                write_text_file(str(txt_path), str(output_path), tts_text)
            
            results.append({
                'topic': topic,
                'title': title,
                'filename': filename,
                'success': True
            })
            
            print(f"  Saved: {filename}")
            
        except Exception as e:
            print(f"  Error processing {topic}: {e}")
            results.append({
                'topic': topic,
                'title': None,
                'filename': None,
                'success': False,
                'error': str(e)
            })
    
    return results

# Usage
topics = [
    "Photosynthesis",
    "Mitosis", 
    "Evolution",
    "DNA",
    "Cell membrane"
]

results = batch_extract(topics, output_dir="biology", create_tts=True)

# Print summary
successful = sum(1 for r in results if r['success'])
print(f"\nProcessed {len(topics)} topics, {successful} successful")
```

### Content Analysis

```python
import re
from collections import Counter

def analyze_article(search_term):
    """Analyze extracted Wikipedia content."""
    
    text, title = extract_wikipedia_text(search_term)
    
    if not text:
        return None
    
    # Basic statistics
    char_count = len(text)
    word_count = len(text.split())
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    # Find headings
    headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    
    # Most common words (simple analysis)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    common_words = Counter(words).most_common(10)
    
    return {
        'title': title,
        'characters': char_count,
        'words': word_count,
        'paragraphs': paragraph_count,
        'headings': headings,
        'common_words': common_words,
        'reading_time': word_count // 200  # Rough estimate in minutes
    }

# Usage
analysis = analyze_article("Artificial Intelligence")
if analysis:
    print(f"Title: {analysis['title']}")
    print(f"Words: {analysis['words']:,}")
    print(f"Estimated reading time: {analysis['reading_time']} minutes")
    print(f"Main sections: {', '.join(analysis['headings'][:5])}")
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from wikibee import extract_wikipedia_text, make_tts_friendly

app = Flask(__name__)

@app.route('/api/extract', methods=['POST'])
def extract_article():
    """API endpoint to extract Wikipedia articles."""
    
    data = request.get_json()
    search_term = data.get('term')
    include_tts = data.get('tts', False)
    lead_only = data.get('lead_only', False)
    
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400
    
    try:
        text, title = extract_wikipedia_text(
            search_term, 
            lead_only=lead_only,
            timeout=30
        )
        
        if not text:
            return jsonify({'error': 'Article not found'}), 404
        
        result = {
            'title': title,
            'content': text,
            'word_count': len(text.split()),
            'success': True
        }
        
        if include_tts:
            tts_content = make_tts_friendly(f"# {title}\n\n{text}")
            result['tts_content'] = tts_content
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Jupyter Notebook Integration

```python
# Great for research and analysis workflows
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from wikibee import extract_wikipedia_text

def create_article_wordcloud(search_term):
    """Create a word cloud from a Wikipedia article."""
    
    text, title = extract_wikipedia_text(search_term)
    
    if not text:
        print("Article not found")
        return
    
    # Create word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400,
        background_color='white'
    ).generate(text)
    
    # Display
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud: {title}')
    plt.tight_layout()
    plt.show()

# Usage in Jupyter
create_article_wordcloud("Machine Learning")
```

### Automation Scripts

```python
#!/usr/bin/env python3
"""
Daily Wikipedia digest script.
Extracts trending articles and creates summaries.
"""

import schedule
import time
from datetime import datetime
from wikibee import extract_wikipedia_text, make_tts_friendly

def create_daily_digest():
    """Create a daily digest of featured articles."""
    
    # You could get trending topics from various sources
    # For demo, using predefined interesting topics
    topics = [
        "Today in history",
        "Current events", 
        "Portal:Current events"
    ]
    
    digest_content = f"# Daily Wikipedia Digest - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    for topic in topics:
        try:
            text, title = extract_wikipedia_text(topic, lead_only=True)
            if text:
                digest_content += f"## {title}\n\n{text}\n\n---\n\n"
        except:
            continue
    
    # Save digest
    filename = f"digest_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(digest_content)
    
    print(f"Created digest: {filename}")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(create_daily_digest)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Best Practices

### Performance Optimization

1. **Cache results** for repeated requests
2. **Use lead_only=True** for summaries
3. **Implement retry logic** for network issues
4. **Process articles in parallel** for bulk operations
5. **Set appropriate timeouts** based on article size

### Memory Management

```python
from wikibee.client import WikiClient

client = WikiClient()

def resolve_topic_url(topic: str) -> str | None:
    results = client.search_articles(topic, limit=1)
    return results[0]["url"] if results else None


def process_large_batch(topics):
    """Process many articles without memory buildup."""

    for topic in topics:
        url = resolve_topic_url(topic)
        if not url:
            continue

        text, title = extract_wikipedia_text(url)

        if text:
            # Process immediately and discard
            process_and_save(text, title)

        # Clear variables
        text = title = None
```

### Error Recovery

```python
from wikibee.client import WikiClient

client = WikiClient()


def robust_extraction(search_term, max_retries=3, fallback_to_lead=True):
    """Extract with fallback strategies."""

    def _resolve_url() -> str | None:
        results = client.search_articles(search_term, limit=1)
        return results[0]["url"] if results else None

    url = _resolve_url()
    if not url:
        return None, None, "failed"

    # Try full article first
    for _ in range(max_retries):
        try:
            text, title = extract_wikipedia_text(url, timeout=30)
            if text:
                return text, title, "full"
        except Exception:
            continue

    # Fallback to lead section
    if fallback_to_lead:
        try:
            text, title = extract_wikipedia_text(url, lead_only=True, timeout=15)
            if text:
                return text, title, "lead"
        except Exception:
            pass

    return None, None, "failed"
```

## Next Steps

- **[Basic Usage Tutorial](basic-usage.md)** - Review CLI-first workflows
- **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation
- **[Configuration Guide](../reference/configuration.md)** - Customize defaults and TTS options
- **[Examples Guide](../guides/examples.md)** - Real-world automation scripts

---

**Navigation**: [Documentation Home](../README.md) | [Basic Usage](basic-usage.md) | [CLI Reference](../reference/cli-reference.md)
