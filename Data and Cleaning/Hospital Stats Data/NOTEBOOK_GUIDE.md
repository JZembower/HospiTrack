# Jupyter Notebook Guide - Comprehensive Hospital Scraper

## Overview

The `scrape_us_states_comprehensive.ipynb` notebook provides an interactive way to scrape comprehensive hospital data from HospitalStats.org for all 50 US states.

## Quick Start

### 1. Open the Notebook
```bash
jupyter notebook scrape_us_states_comprehensive.ipynb
```

Or use VS Code, JupyterLab, or Google Colab.

### 2. Configure Settings

In the **Configuration** cell, adjust these settings:

```python
MAX_COUNTIES = 5        # Number of counties to scrape (None = all ~3000)
ENRICH_DATA = True      # Whether to scrape detail pages (slower but more data)
DELAY = 0.8             # Delay between requests (seconds)
```

**Recommended for first run:**
- `MAX_COUNTIES = 5` (test with 5 counties)
- `ENRICH_DATA = True` (get full data)

### 3. Run All Cells

**Option A: Run All**
- Click "Run All" in the menu
- Wait for completion (~3-5 minutes for 5 counties)

**Option B: Run Step-by-Step**
- Execute each cell sequentially
- Review output after each step

## Notebook Structure

### Setup Cells (Run Once)
1. **Title & Overview** - Introduction and features
2. **Imports** - Load required libraries
3. **Configuration** - Adjust scraping settings
4. **Helper Functions** - Utility functions
5. **Detail Page Parser** - Extract comprehensive metrics
6. **State & County Discovery** - Find all states/counties
7. **County Page Parser** - Extract hospital listings
8. **Data Enrichment** - Add detail page data
9. **Main Scraping Function** - Orchestrate scraping
10. **Export & Summary** - Save and summarize data

### Execution Cells (Run to Scrape)
11. **Step 1: Discover Counties** - Find all counties
12. **Step 2: Setup Output** - Create output directory
13. **Step 3: Scrape Data** - Main scraping process ⏱️
14. **Step 4: Export Results** - Save to CSV
15. **Step 5: Print Summary** - Display statistics

### Analysis Cells (Optional)
16. **View Data Info** - Check structure and completeness
17. **Top 10 Hospitals** - Shortest wait times
18. **State Comparison** - Average wait times by state
19. **Mortality Analysis** - Best performing hospitals

## Configuration Options

### Test Mode (Fast)
```python
MAX_COUNTIES = 5
ENRICH_DATA = True
```
- **Time:** ~3-5 minutes
- **Data:** 5 counties with full details
- **Use:** Testing and verification

### Quick Scan (Faster)
```python
MAX_COUNTIES = 50
ENRICH_DATA = False
```
- **Time:** ~10-15 minutes
- **Data:** 50 counties, basic info only
- **Use:** Quick overview without details

### Medium Scrape
```python
MAX_COUNTIES = 100
ENRICH_DATA = True
```
- **Time:** ~1-2 hours
- **Data:** 100 counties with full details
- **Use:** Substantial dataset for analysis

### Full Scrape (Slow)
```python
MAX_COUNTIES = None
ENRICH_DATA = True
```
- **Time:** ~15-20 hours
- **Data:** All ~3000 counties with full details
- **Use:** Complete US hospital dataset

## Output Files

### Location
```
out/
└── us_states_YYYYMMDD_HHMMSS/
    ├── counties_list.csv
    └── us_hospitals_data_enriched.csv
```

### Files
1. **counties_list.csv**
   - All discovered counties
   - Columns: state_abbr, county_name, county_url

2. **us_hospitals_data_enriched.csv**
   - Complete hospital data
   - 30+ columns with all metrics

## Common Workflows

### Workflow 1: Quick Test
```python
# Configuration cell
MAX_COUNTIES = 5
ENRICH_DATA = True

# Run all cells
# Check output in ~3-5 minutes
```

### Workflow 2: State-Specific
```python
# After Step 1 (Discover Counties), add this cell:
df_counties = df_counties[df_counties['state_abbr'] == 'CA']

# Then continue with Steps 2-5
```

### Workflow 3: Incremental Scraping
```python
# First run: 10 counties
MAX_COUNTIES = 10
# Run all cells

# Second run: Next 10 counties
# Manually skip first 10 in df_counties
df_counties = df_counties.iloc[10:20]
# Continue with Steps 2-5
```

### Workflow 4: Fast Overview
```python
# Configuration
MAX_COUNTIES = 100
ENRICH_DATA = False  # Skip detail pages

# Run all cells
# Get basic data in ~15 minutes
```

## Troubleshooting

### Problem: Kernel Dies
**Cause:** Out of memory
**Solution:**
- Reduce `MAX_COUNTIES`
- Restart kernel and try again
- Close other applications

### Problem: Many Errors
**Cause:** Network issues or page structure changes
**Solution:**
- Check internet connection
- Verify a few URLs manually
- Errors are logged but don't stop scraping

### Problem: Slow Performance
**Cause:** Large number of counties or detail pages
**Solution:**
- Reduce `MAX_COUNTIES`
- Set `ENRICH_DATA = False`
- Increase `DELAY` if getting rate limited

### Problem: Empty Results
**Cause:** No hospitals found in selected counties
**Solution:**
- Check county URLs manually
- Try different counties
- Verify website structure hasn't changed

## Tips & Best Practices

### 1. Start Small
Always test with `MAX_COUNTIES = 5` first to verify everything works.

### 2. Monitor Progress
Watch the output as cells execute to catch errors early.

### 3. Save Intermediate Results
The notebook automatically saves:
- Counties list after Step 1
- Hospital data after Step 4

### 4. Use Analysis Cells
Explore your data with the built-in analysis cells before exporting.

### 5. Adjust Delay
If you get rate limited or blocked:
```python
DELAY = 1.5  # Slower, more polite
```

### 6. Resume Interrupted Scraping
If scraping is interrupted:
1. Load the existing CSV
2. Filter out already-scraped counties
3. Continue with remaining counties

### 7. Backup Your Data
Copy output files to a safe location after scraping.

## Data Analysis Examples

### Example 1: Filter by State
```python
# After Step 3
ca_hospitals = df_hospitals[df_hospitals['state_abbr'] == 'CA']
print(f"California hospitals: {len(ca_hospitals)}")
```

### Example 2: Find Best Hospitals
```python
# Hospitals with short wait times and low mortality
best = df_hospitals[
    (df_hospitals['wait_minutes'] < 60) &
    (df_hospitals['detail_mortality_overall_percent'] < 2.0)
]
print(best[['hospital_name', 'city', 'state_abbr']])
```

### Example 3: Export Subset
```python
# Export only hospitals with emergency services
emergency_only = df_hospitals[
    df_hospitals['detail_emergency_services'] == 'YES'
]
emergency_only.to_csv(outdir / 'emergency_hospitals.csv', index=False)
```

## Advanced Usage

### Custom Filtering
Add a cell after Step 1 to filter counties:

```python
# Filter to specific states
df_counties = df_counties[df_counties['state_abbr'].isin(['CA', 'NY', 'TX'])]

# Filter to specific counties
df_counties = df_counties[df_counties['county_name'].str.contains('Los Angeles')]

# Random sample
df_counties = df_counties.sample(n=20, random_state=42)
```

### Batch Processing
Process in batches to avoid long-running sessions:

```python
# Batch 1: First 100 counties
df_batch1 = df_counties.iloc[0:100]
df_hospitals_1 = scrape_all_counties(df_batch1, enrich=True)

# Batch 2: Next 100 counties
df_batch2 = df_counties.iloc[100:200]
df_hospitals_2 = scrape_all_counties(df_batch2, enrich=True)

# Combine
df_all = pd.concat([df_hospitals_1, df_hospitals_2], ignore_index=True)
```

### Custom Export
Add custom export logic after Step 4:

```python
# Export by state
for state in df_hospitals['state_abbr'].unique():
    state_data = df_hospitals[df_hospitals['state_abbr'] == state]
    state_data.to_csv(outdir / f'{state}_hospitals.csv', index=False)
```

## Comparison: Notebook vs Script

### Jupyter Notebook
**Pros:**
- Interactive exploration
- Step-by-step execution
- Built-in visualization
- Easy to modify and test

**Cons:**
- Requires Jupyter environment
- Not ideal for long-running tasks
- Can lose progress if kernel dies

### Python Script
**Pros:**
- Run in background (nohup, screen)
- Better for long-running tasks
- Command-line arguments
- More stable for large scrapes

**Cons:**
- Less interactive
- Harder to debug
- No built-in visualization

**Recommendation:**
- Use **notebook** for testing and exploration (< 100 counties)
- Use **script** for production scraping (> 100 counties)

## Next Steps

1. **Test the notebook:**
   ```python
   MAX_COUNTIES = 5
   ENRICH_DATA = True
   ```
   Run all cells and verify output.

2. **Explore the data:**
   Use the analysis cells to understand your data.

3. **Scale up:**
   Gradually increase `MAX_COUNTIES` as needed.

4. **Switch to script:**
   For full scrape, use `scrape_us_states_comprehensive.py` instead.

## Resources

- **README_COMPREHENSIVE.md** - Detailed documentation
- **USAGE_GUIDE.md** - Command-line usage examples
- **test_scraper.py** - Quick test script
- **scrape_us_states_comprehensive.py** - Production script

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review error messages in cell output
3. Verify website structure hasn't changed
4. Try with smaller `MAX_COUNTIES` first

---

**Happy scraping!** 🏥📊
