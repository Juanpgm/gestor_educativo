# Cost Monitoring

## Overview

Every LLM API call is logged in the `cost_log` table for tracking and budgeting.

## CostLog Table

| Column         | Type          | Description                     |
| -------------- | ------------- | ------------------------------- |
| id             | SERIAL        | Primary key                     |
| operacion      | VARCHAR(100)  | e.g., "llm_template_mapping"    |
| costo_estimado | DECIMAL(10,6) | Estimated USD cost              |
| tokens_usados  | INTEGER       | Total tokens (input + output)   |
| metadata_extra | JSONB         | Model name, document type, etc. |
| created_at     | TIMESTAMP     | When the operation occurred     |

## Cost Estimation

Current pricing (gpt-4o-mini):

- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Approximate: $0.002 / 1K tokens (blended)

## Querying Costs

```sql
-- Total cost this month
SELECT SUM(costo_estimado) as total_cost
FROM cost_log
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);

-- Cost by operation
SELECT operacion, COUNT(*), SUM(costo_estimado), SUM(tokens_usados)
FROM cost_log
GROUP BY operacion;

-- Daily trend
SELECT DATE(created_at) as day, SUM(costo_estimado)
FROM cost_log
GROUP BY DATE(created_at)
ORDER BY day;
```

## Budget Alerts

For the MVP, manual monitoring via SQL queries. Future enhancement: automated alerts when monthly cost exceeds threshold.
