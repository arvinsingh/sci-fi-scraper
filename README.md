# Sci-Fi Technology Dataset Generator

**A specialized tool for creating high-quality fine-tuning datasets of science fiction technology from Wikipedia**

This project automatically scrapes, classifies, and formats science fiction technology information from Wikipedia to create training datasets for AI models. Perfect for fine-tuning language models on sci-fi content, creative writing applications, or building knowledge bases about fictional technologies.

## Purpose

This tool is specifically designed to create machine learning datasets for:
- **Fine-tuning language models** on science fiction content
- **Training AI systems** to understand and generate sci-fi technology descriptions
- **Building knowledge graphs** of fictional technologies
- **Creating training data** for creative writing assistants
- **Generating datasets** for sci-fi content generation models

## Dataset Output

The scraper generates multiple dataset formats optimized for machine learning:

### Training Data Format (JSONL)
```json
{
  "instruction": "Describe this weapon from science fiction:",
  "input": "Lightsaber",
  "output": "A lightsaber is a fictional energy sword featured in the Star Wars universe...",
  "metadata": {
    "source": "wikipedia",
    "category": "Science fiction weapons",
    "tech_type": "weapon",
    "url": "https://en.wikipedia.org/wiki/Lightsaber"
  }
}
```

### Raw Data Format (JSON)
```json
{
  "name": "Tricorder",
  "description": "A tricorder is a fictional handheld sensor...",
  "url": "https://en.wikipedia.org/wiki/Tricorder",
  "category": "Fictional technology",
  "tech_type": "device",
  "content_length": 535,
  "scraped_at": "2025-07-04T19:03:00",
  "confidence_score": 1.0
}
```

## Project Structure

```
sci-fi-scraper/
├── main.py                 # Main entry point
├── pyproject.toml         # Project configuration
├── README.md              # This file
├── scraper.log            # Application logs
├── checkpoints/           # Dataset output directory
│   ├── training_data_*.jsonl      # Main training dataset*
│   ├── fictional_tech_data_*.json # Raw dataset
│   ├── scraping_stats_*.json      # Dataset statistics
│   └── scraping_checkpoint.*      # Resume checkpoints
└── src/                   # Modular source code
    ├── models.py          # Data structures for dataset entries
    ├── config.py          # Classification and filtering rules
    ├── api_client.py      # Wikipedia API client
    ├── classifier.py      # Pattern-based content classification
    ├── scraper.py         # Main dataset generation engine
    ├── utils.py           # Dataset export and statistics
    └── cli.py             # Command line interface
```

## Quick Start

### Setup with UV Package Manager
```bash
# Clone or navigate to the project directory
cd sci-fi-scraper

# Install dependencies with UV
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows
```

### Generate a Small Dataset (for testing)
```bash
python main.py --max-entries 100 --categories "Science fiction weapons"
```

### Generate a Large Training Dataset
```bash
python main.py --max-entries 10000 --max-workers 8
```

### Generate Dataset for Specific Franchises
```bash
python main.py --categories "Star Trek technology" "Star Wars technology" "Stargate technology"
```

## Dataset Configuration

### Basic Options
```bash
# Dataset size
python main.py --max-entries 5000

# Processing speed
python main.py --max-workers 8

# Content depth
python main.py --max-depth 3

# Specific categories
python main.py --categories "Fictional spacecraft" "Fictional robots"
```

### Advanced Configuration
```bash
# High-quality dataset (stricter filtering)
python main.py --max-entries 1000 --max-workers 2 --max-depth 2

# Comprehensive dataset (broader coverage)
python main.py --max-entries 50000 --max-workers 12 --max-depth 6
```

## Dataset Quality Features

### Intelligent Classification
- **Technology Type Detection**: Rule-based pattern matching categorizes as weapon, vehicle, device, robot, etc.
- **Confidence Scoring**: Each entry has a quality confidence score (0.0-1.0) based on pattern matches
- **Content Filtering**: Removes biographies, plot summaries, and irrelevant content using regex patterns
- **Franchise Recognition**: Identifies content from major sci-fi franchises through keyword matching

### Quality Metrics
- **Content Length**: Ensures substantial descriptions (200+ characters)
- **Sci-fi Relevance**: Advanced pattern matching for science fiction context
- **Technical Accuracy**: Filters out non-technical content
- **Duplicate Detection**: Prevents duplicate entries in the dataset

### Dataset Optimization
- **Training Format**: Ready-to-use instruction-following format
- **Metadata Rich**: Comprehensive metadata for each entry
- **Streaming Export**: JSONL format for efficient processing
- **Statistics**: Detailed dataset composition analysis

## Dataset Statistics Example

```json
{
  "total_entries": 5234,
  "tech_types": {
    "weapon": 1456,
    "vehicle": 1203,
    "device": 987,
    "robot": 743,
    "system": 845
  },
  "categories": {
    "Science fiction weapons": 1456,
    "Fictional spacecraft": 1203,
    "Fictional technology": 987
  },
  "quality_metrics": {
    "avg_content_length": 847,
    "high_confidence_entries": 4891,
    "training_ready_entries": 4652
  }
}
```

## Use Cases

### Fine-tuning Language Models
- **Instruction Following**: Train models to describe sci-fi technologies
- **Creative Writing**: Generate fictional technology descriptions
- **World Building**: Create consistent sci-fi universes
- **Technical Documentation**: Generate technical manuals for fictional tech

### Dataset Applications
- **RAG Systems**: Knowledge base for sci-fi question answering
- **Content Generation**: Automated sci-fi content creation
- **Game Development**: Generate technology descriptions for games
- **Educational Tools**: Teaching about science fiction concepts

## Testing Dataset Quality

Test the classification system on known sci-fi technologies:
```bash
python main.py --test-pages "Lightsaber" "Tricorder" "Warp drive" "Sonic screwdriver"
```

## Output Formats

### 1. Training Data (`training_data_*.jsonl`)
**Purpose**: Direct use in fine-tuning pipelines
- Instruction-following format
- Optimized for language model training
- Filtered for quality (100+ character descriptions)

### 2. Raw Dataset (`fictional_tech_data_*.json`)
**Purpose**: Research and analysis
- Complete metadata
- All scraped entries
- Suitable for data analysis

### 3. Streaming Format (`fictional_tech_data_*.jsonl`)
**Purpose**: Large-scale processing
- Line-by-line processing
- Memory efficient
- Suitable for big data pipelines

### 4. Statistics (`scraping_stats_*.json`)
**Purpose**: Dataset evaluation
- Composition analysis
- Quality metrics
- Processing statistics

## Advanced Configuration

### Custom Classification Rules
Edit `src/config.py` to modify:
- Technology classification patterns
- Sci-fi franchise detection
- Content exclusion rules
- Quality thresholds

### Custom Export Formats
Add new exporters in `src/utils.py`:
- Custom JSON schemas
- Database formats
- API endpoints
- Cloud storage integration

## Resumable Processing

The scraper automatically saves progress and can resume interrupted sessions:
- Checkpoints saved every 10 entries
- Resume from last checkpoint automatically
- No duplicate processing
- Progress tracking across sessions

## Dataset Validation

Before fine-tuning, validate your dataset:
```bash
# Check dataset statistics
python -c "
import json
with open('checkpoints/scraping_stats_*.json') as f:
    stats = json.load(f)
    print(f'Total entries: {stats[\"total_entries\"]}')
    print(f'Training ready: {stats[\"quality_entries\"]}')
"
```

## Fine-tuning Ready

The generated datasets are optimized for popular fine-tuning frameworks:
- **Transformers**: Direct JSONL import
- **Axolotl**: Compatible format
- **LLaMA-Factory**: Ready to use
- **Custom pipelines**: JSON/JSONL support

## License

MIT License