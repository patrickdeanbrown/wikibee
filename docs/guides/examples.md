# Examples and Use Cases

Real-world examples of using wikibee for various tasks and workflows.

## Table of Contents
- [Accessibility and TTS](#accessibility-and-tts)
- [Research and Education](#research-and-education)
- [Content Creation](#content-creation)
- [Automation and Scripts](#automation-and-scripts)
- [Integration Examples](#integration-examples)

## Accessibility and TTS

### Creating Audio Content for Visual Accessibility

```bash
# Create clean TTS content for accessibility
wikibee "Marie Curie" --tts --heading-prefix "Section:" --output accessibility/

# Process a series of biographical articles
mkdir -p biographies/accessibility
for person in "Albert Einstein" "Marie Curie" "Isaac Newton" "Charles Darwin"; do
    wikibee "$person" --tts --yolo --output biographies/accessibility/ --heading-prefix "Section:"
    echo "Processed: $person"
done
```

**Output**: Clean text files optimized for screen readers and TTS engines.

### Audio Book Preparation

```bash
#!/bin/bash
# Prepare content for audio book creation

TOPIC="Ancient Rome"
OUTPUT_DIR="audiobook_prep"

# Get comprehensive content
wikibee "$TOPIC" --tts --output "$OUTPUT_DIR/" --heading-prefix "Chapter:"

# Get related topics for additional chapters
wikibee "Roman Empire" --tts --yolo --output "$OUTPUT_DIR/" --filename "02_roman_empire" --heading-prefix "Chapter:"
wikibee "Julius Caesar" --tts --yolo --output "$OUTPUT_DIR/" --filename "03_julius_caesar" --heading-prefix "Chapter:"
wikibee "Fall of Rome" --tts --yolo --output "$OUTPUT_DIR/" --filename "04_fall_of_rome" --heading-prefix "Chapter:"

echo "Audio book content prepared in $OUTPUT_DIR/"
```

## Research and Education

### Academic Research Workflow

```bash
#!/bin/bash
# Research workflow for academic paper preparation

RESEARCH_TOPIC="Machine Learning"
BASE_DIR="research_$(date +%Y%m%d)"

# Create directory structure
mkdir -p "$BASE_DIR"/{summaries,detailed,references}

echo "Starting research on: $RESEARCH_TOPIC"

# Phase 1: Quick summaries for overview
echo "Phase 1: Gathering summaries..."
wikibee "$RESEARCH_TOPIC" --lead-only --output "$BASE_DIR/summaries/" --filename "01_ml_overview"
wikibee "Deep Learning" --lead-only --yolo --output "$BASE_DIR/summaries/" --filename "02_deep_learning"
wikibee "Neural Networks" --lead-only --yolo --output "$BASE_DIR/summaries/" --filename "03_neural_networks"
wikibee "Artificial Intelligence" --lead-only --yolo --output "$BASE_DIR/summaries/" --filename "04_ai_overview"

# Phase 2: Detailed articles
echo "Phase 2: Detailed research..."
wikibee "$RESEARCH_TOPIC" --tts --output "$BASE_DIR/detailed/" --timeout 30
wikibee "Supervised Learning" --tts --yolo --output "$BASE_DIR/detailed/" --timeout 30
wikibee "Unsupervised Learning" --tts --yolo --output "$BASE_DIR/detailed/" --timeout 30

echo "Research completed in $BASE_DIR/"
find "$BASE_DIR" -name "*.md" | wc -l | xargs echo "Created files:"
```

### Student Study Guide Creation

```bash
# Create study guides for biology class
mkdir -p biology_study_guides

# Key topics with TTS for audio study
TOPICS=("Photosynthesis" "Cellular Respiration" "Mitosis" "Meiosis" "DNA Replication" "Protein Synthesis")

for topic in "${TOPICS[@]}"; do
    echo "Creating study guide: $topic"
    
    # Summary for quick review
    wikibee "$topic" --lead-only --output biology_study_guides/summaries/ --yolo --filename "${topic,,}_summary"
    
    # Full article with TTS for comprehensive study
    wikibee "$topic" --tts --output biology_study_guides/detailed/ --yolo --heading-prefix "Topic:" --filename "${topic,,}_detailed"
done

# Create index file
echo "# Biology Study Guides" > biology_study_guides/README.md
echo "" >> biology_study_guides/README.md
echo "## Quick Summaries" >> biology_study_guides/README.md
ls biology_study_guides/summaries/*.md | sed 's/.*\//- [/' | sed 's/\.md/](&)/' >> biology_study_guides/README.md
echo "" >> biology_study_guides/README.md
echo "## Detailed Guides" >> biology_study_guides/README.md
ls biology_study_guides/detailed/*.md | sed 's/.*\//- [/' | sed 's/\.md/](&)/' >> biology_study_guides/README.md
```

### Language Learning Support

```bash
# Create content for language learning (simplified English from Wikipedia)
mkdir -p language_learning/simple_articles

# Get lead sections of basic topics for vocabulary building
BASIC_TOPICS=("Water" "Food" "Family" "School" "Weather" "Animals" "Colors" "Numbers")

for topic in "${BASIC_TOPICS[@]}"; do
    wikibee "$topic" --lead-only --tts --output language_learning/simple_articles/ --yolo --filename "${topic,,}"
    echo "Created: $topic"
done
```

## Content Creation

### Podcast Research Pipeline

```bash
#!/bin/bash
# Podcast episode preparation workflow

EPISODE_TOPIC="The Renaissance"
EPISODE_DIR="podcast_$(date +%Y%m%d)_renaissance"

mkdir -p "$EPISODE_DIR"/{research,scripts,audio_prep}

echo "Preparing podcast episode: $EPISODE_TOPIC"

# Background research
wikibee "$EPISODE_TOPIC" --output "$EPISODE_DIR/research/" --filename "main_topic"
wikibee "Leonardo da Vinci" --lead-only --yolo --output "$EPISODE_DIR/research/" --filename "leonardo"
wikibee "Michelangelo" --lead-only --yolo --output "$EPISODE_DIR/research/" --filename "michelangelo"
wikibee "Renaissance Art" --lead-only --yolo --output "$EPISODE_DIR/research/" --filename "art"

# Script preparation (TTS-optimized for reading aloud)
wikibee "$EPISODE_TOPIC" --tts --output "$EPISODE_DIR/scripts/" --heading-prefix "Segment:" --filename "main_script"

# Audio preparation
wikibee "Renaissance Music" --tts --lead-only --yolo --output "$EPISODE_DIR/audio_prep/" --filename "music_segment"

echo "Podcast research completed in $EPISODE_DIR/"
```

### Blog Post Research

```bash
# Research for a blog post about emerging technologies
mkdir -p blog_research/emerging_tech_$(date +%Y%m%d)

echo "Researching: Emerging Technologies"

# Quick overviews for blog outline
wikibee "Quantum Computing" --lead-only --output blog_research/emerging_tech_*/
wikibee "Artificial Intelligence" --lead-only --yolo --output blog_research/emerging_tech_*/ --filename "ai_overview"
wikibee "Blockchain" --lead-only --yolo --output blog_research/emerging_tech_*/ --filename "blockchain_overview"
wikibee "Gene Therapy" --lead-only --yolo --output blog_research/emerging_tech_*/ --filename "gene_therapy_overview"

# Detailed research for specific sections
wikibee "Machine Learning Applications" --tts --yolo --output blog_research/emerging_tech_*/ --filename "ml_applications"

echo "Blog research completed!"
```

## Automation and Scripts

### Daily Wikipedia Digest

```python
#!/usr/bin/env python3
"""
Daily Wikipedia digest automation
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

def run_wikibee(topic, output_dir, additional_args=[]):
    """Run wikibee command and return success status"""
    cmd = ['wikibee', topic, '--output', output_dir, '--yolo'] + additional_args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def create_daily_digest():
    """Create daily digest of interesting topics"""
    today = datetime.now().strftime('%Y-%m-%d')
    digest_dir = f"daily_digest_{today}"
    os.makedirs(digest_dir, exist_ok=True)
    
    # Topics that change frequently or are always relevant
    topics = [
        "Current events",
        "Portal:Current events", 
        "2024 in science",
        "Recent deaths"
    ]
    
    successful = 0
    for topic in topics:
        print(f"Processing: {topic}")
        if run_wikibee(topic, digest_dir, ['--lead-only']):
            successful += 1
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed")
    
    print(f"\nDaily digest created: {digest_dir}/")
    print(f"Successfully processed: {successful}/{len(topics)} topics")
    
    return digest_dir

if __name__ == "__main__":
    create_daily_digest()
```

### Batch Processing with Error Handling

```bash
#!/bin/bash
# Robust batch processing script

LOG_FILE="wikibee_batch_$(date +%Y%m%d_%H%M%S).log"
SUCCESS_COUNT=0
FAILED_COUNT=0

process_topic() {
    local topic="$1"
    local output_dir="$2"
    local timeout="$3"
    
    echo "[$(date)] Processing: $topic" | tee -a "$LOG_FILE"
    
    if timeout "$timeout" wikibee "$topic" --yolo --output "$output_dir" --tts --timeout 30 2>>"$LOG_FILE"; then
        echo "[$(date)] ✓ Success: $topic" | tee -a "$LOG_FILE"
        ((SUCCESS_COUNT++))
        return 0
    else
        echo "[$(date)] ✗ Failed: $topic" | tee -a "$LOG_FILE"
        ((FAILED_COUNT++))
        return 1
    fi
}

# Main processing
OUTPUT_DIR="batch_output_$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Topics to process
TOPICS=(
    "Artificial Intelligence"
    "Machine Learning" 
    "Deep Learning"
    "Computer Vision"
    "Natural Language Processing"
    "Robotics"
    "Quantum Computing"
)

echo "Starting batch processing of ${#TOPICS[@]} topics..." | tee -a "$LOG_FILE"

for topic in "${TOPICS[@]}"; do
    process_topic "$topic" "$OUTPUT_DIR" 120  # 2-minute timeout per topic
    
    # Brief pause between requests to be respectful
    sleep 2
done

# Summary report
echo "" | tee -a "$LOG_FILE"
echo "=== BATCH PROCESSING SUMMARY ===" | tee -a "$LOG_FILE"
echo "Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "Failed: $FAILED_COUNT" | tee -a "$LOG_FILE"
echo "Output directory: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# List created files
echo "" | tee -a "$LOG_FILE"
echo "Created files:" | tee -a "$LOG_FILE"
find "$OUTPUT_DIR" -name "*.md" | sort | tee -a "$LOG_FILE"
```

## Integration Examples

### Web Application Backend

```python
# Flask web service for on-demand Wikipedia extraction
from flask import Flask, request, jsonify, send_file
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/api/extract', methods=['POST'])
def extract_wikipedia():
    data = request.get_json()
    topic = data.get('topic')
    format_type = data.get('format', 'markdown')  # 'markdown' or 'tts'
    lead_only = data.get('lead_only', False)
    
    if not topic:
        return jsonify({'error': 'Topic required'}), 400
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Build wikibee command
            cmd = ['wikibee', topic, '--output', temp_dir, '--yolo']
            
            if lead_only:
                cmd.append('--lead-only')
            
            if format_type == 'tts':
                cmd.append('--tts')
            
            # Run extraction
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return jsonify({'error': 'Extraction failed'}), 500
            
            # Find created files
            files = os.listdir(temp_dir)
            markdown_files = [f for f in files if f.endswith('.md')]
            
            if not markdown_files:
                return jsonify({'error': 'No content generated'}), 500
            
            # Read content
            content_file = os.path.join(temp_dir, markdown_files[0])
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for TTS file
            tts_content = None
            if format_type == 'tts':
                tts_files = [f for f in files if f.endswith('.txt')]
                if tts_files:
                    tts_file = os.path.join(temp_dir, tts_files[0])
                    with open(tts_file, 'r', encoding='utf-8') as f:
                        tts_content = f.read()
            
            response = {
                'success': True,
                'topic': topic,
                'content': content,
                'word_count': len(content.split()),
                'format': format_type
            }
            
            if tts_content:
                response['tts_content'] = tts_content
            
            return jsonify(response)
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Request timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'wikibee-api'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Jupyter Notebook Integration

```python
# Jupyter notebook helper functions
import subprocess
import tempfile
import os
from IPython.display import Markdown, display

def extract_and_display(topic, lead_only=True, show_tts=False):
    """Extract Wikipedia content and display in Jupyter notebook"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = ['wikibee', topic, '--output', temp_dir, '--yolo']
        
        if lead_only:
            cmd.append('--lead-only')
        
        if show_tts:
            cmd.append('--tts')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Error extracting '{topic}': {result.stderr}")
                return
            
            # Display markdown content
            md_files = [f for f in os.listdir(temp_dir) if f.endswith('.md')]
            if md_files:
                with open(os.path.join(temp_dir, md_files[0]), 'r') as f:
                    content = f.read()
                display(Markdown(content))
            
            # Display TTS content if requested
            if show_tts:
                txt_files = [f for f in os.listdir(temp_dir) if f.endswith('.txt')]
                if txt_files:
                    print("\n" + "="*50)
                    print("TTS-OPTIMIZED VERSION:")
                    print("="*50)
                    with open(os.path.join(temp_dir, txt_files[0]), 'r') as f:
                        print(f.read()[:500] + "...")
        
        except subprocess.TimeoutExpired:
            print(f"Timeout extracting '{topic}'")

# Usage in Jupyter notebook
extract_and_display("Quantum Computing")
extract_and_display("Machine Learning", lead_only=False, show_tts=True)
```

### Content Management System Integration

```python
# Django model integration example
from django.db import models
import subprocess
import tempfile
import os

class WikipediaArticle(models.Model):
    topic = models.CharField(max_length=200)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    tts_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extraction_successful = models.BooleanField(default=False)
    
    def extract_content(self, lead_only=False, include_tts=True):
        """Extract Wikipedia content for this article"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = ['wikibee', self.topic, '--output', temp_dir, '--yolo']
            
            if lead_only:
                cmd.append('--lead-only')
            
            if include_tts:
                cmd.append('--tts')
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Read generated files
                    files = os.listdir(temp_dir)
                    
                    # Get markdown content
                    md_files = [f for f in files if f.endswith('.md')]
                    if md_files:
                        with open(os.path.join(temp_dir, md_files[0]), 'r') as f:
                            content = f.read()
                            # Extract title from content
                            lines = content.split('\n')
                            title = lines[0].replace('# ', '') if lines else self.topic
                            
                            self.title = title
                            self.content = content
                    
                    # Get TTS content if available
                    if include_tts:
                        txt_files = [f for f in files if f.endswith('.txt')]
                        if txt_files:
                            with open(os.path.join(temp_dir, txt_files[0]), 'r') as f:
                                self.tts_content = f.read()
                    
                    self.extraction_successful = True
                else:
                    self.extraction_successful = False
                
                self.save()
                return self.extraction_successful
                
            except subprocess.TimeoutExpired:
                self.extraction_successful = False
                self.save()
                return False

    def __str__(self):
        return f"Wikipedia: {self.title or self.topic}"

# Usage
article = WikipediaArticle(topic="Artificial Intelligence")
success = article.extract_content(lead_only=True, include_tts=True)
if success:
    print(f"Extracted: {article.title}")
```

## Best Practices from Examples

### Performance Optimization
- Use `--lead-only` for faster processing when full content isn't needed
- Add `--yolo` for non-interactive batch processing  
- Set appropriate timeouts based on expected content size
- Add delays between requests in batch operations

### Error Handling
- Always check return codes in scripts
- Implement retry logic for network issues
- Log both successes and failures
- Use timeouts to prevent hanging processes

### File Organization
- Create dated output directories for batch operations
- Use descriptive filenames with prefixes/suffixes
- Maintain separate directories for different content types
- Create index files for large collections

### Content Quality
- Review generated content for accuracy
- Use TTS optimization for audio applications
- Consider lead-only extraction for summaries
- Implement content validation in automated workflows

---

**Navigation**: [Documentation Home](../README.md) | [Integration Guide](integration.md) | [API Reference](../reference/api-reference.md) | [CLI Reference](../reference/cli-reference.md)