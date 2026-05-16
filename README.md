# Data Storm 7.0 - Potential-Based Allocation Model

This repository contains the solution for the Data Storm 7.0 challenge. 

## Problem Statement

The goal is to help a leading Sri Lankan beverage manufacturer transition from allocating trade marketing resources based on flawed historical sales averages to a strategic "Potential-Based Allocation" model. We are tasked with predicting the latent maximum monthly volume potential (in liters) for January 2026 across 20,000 traditional retail outlets.

## Project Structure

- `data/`: Contains data lakes for raw (`bronze`), cleaned (`silver`), and aggregated (`gold`) data. Also holds `external` data like scraped POIs.
- `src/`: Source code including `data_pipeline`, `features`, `models`, `scraper`, and `utils`.
- `notebooks/`: Jupyter notebooks for EDA and prototyping.
- `tests/`: Unit tests for pipeline and models.
- `config/`: YAML files for configurations and hyperparameters.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
