# HealthFlow Data Platform — Architecture

## 1. Architecture Overview

The HealthFlow Data Platform will collect operational laboratory data, preserve the raw data in a data lake, process the data through an automated data pipeline, store analytical data in a data warehouse, and provide the prepared data to business intelligence tools.

## 2. High-Level Data Flow

```text
HealthFlow Operational Source
            |
            v
       Raw Data Files
            |
            v
      Google Cloud Storage
         Data Lake
            |
            v
       Data Pipeline
            |
     +------+------+------+
     |      |      |      |
 Extract Validate Transform
            |
            v
         BigQuery
      Data Warehouse
            |
            v
         Power BI
        Dashboard