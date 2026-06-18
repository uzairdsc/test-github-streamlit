# Staging Streamlit App

## Overview
Password-protected Streamlit dashboard for cricket ball-by-ball analysis. It supports wagon wheels, wagon zones, dismissal plots, and batch plot generation with filter controls for player, team, venue, phase, innings, and date range.

## Data Sources
- CSV upload
- S3
- Local cache files
- Squad files for batch generation

## Usage
1. Open the app in Streamlit
2. Load a dataset from the sidebar
3. Choose filters and plot types
4. Generate plots or batch outputs
5. Download the figures or the batch ZIP file

## Requirements
- `streamlit`
- `pandas`
- `numpy`
- `matplotlib`
- `boto3`

