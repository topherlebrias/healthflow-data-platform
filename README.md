# HealthFlow Data Platform

## Project Overview

HealthFlow Data Platform is a data engineering project for a fictional diagnostic laboratory organization.

The platform is designed to collect, validate, transform, store, and prepare healthcare laboratory data for analytics.

The project is inspired by real-world laboratory and healthcare data workflows.

## Business Problem

A diagnostic laboratory generates large amounts of operational data from patients, laboratory services, specimens, test results, and payments.

This operational data needs to be organized and processed so that management can reliably answer business questions about:

- Patient volume
- Laboratory workload
- Test turnaround time
- Pending results
- Branch performance
- Revenue
- Data quality

The goal of this project is to build an automated data platform that makes this information reliable and ready for analysis.

## Project Architecture

The planned architecture is:

Source Data
    ↓
Scheduled Job
    ↓
Data Lake
    ↓
Data Pipeline
    ↓
BigQuery
    ↓
Power BI Dashboard

## Technologies

- Python
- SQL
- PostgreSQL
- Google Cloud Storage
- BigQuery
- Git
- GitHub
- Power BI

## Project Goals

1. Design a realistic healthcare data model.
2. Generate synthetic laboratory data.
3. Build a data ingestion pipeline.
4. Validate incoming data.
5. Transform data for analytics.
6. Implement incremental data processing.
7. Store raw data in a data lake.
8. Load analytical data into BigQuery.
9. Automate pipeline execution.
10. Build business dashboards.
11. Implement data quality checks.
12. Document the complete data engineering workflow.

## Data Privacy

This project uses fictional and synthetic data.

No real patient information is used.