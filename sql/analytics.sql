-- ============================================================
-- HEALTHFLOW ANALYTICS QUERIES
-- ============================================================


-- 1. Total laboratory services
SELECT
    COUNT(*) AS total_services
FROM vw_lab_service_analysis;


-- 2. Total revenue
SELECT
    COALESCE(SUM(revenue), 0) AS total_revenue
FROM vw_lab_service_analysis;


-- 3. Average turnaround time
SELECT
    ROUND(AVG(turnaround_minutes), 2) AS average_turnaround_minutes
FROM vw_lab_service_analysis
WHERE turnaround_minutes IS NOT NULL;


-- 4. Services by branch
SELECT
    branch_name,
    COUNT(*) AS total_services
FROM vw_lab_service_analysis
GROUP BY branch_name
ORDER BY total_services DESC;


-- 5. Revenue by service
SELECT
    service_name,
    COUNT(*) AS total_services,
    COALESCE(SUM(revenue), 0) AS total_revenue
FROM vw_lab_service_analysis
GROUP BY service_name
ORDER BY total_revenue DESC;


-- 6. Services with incomplete results
SELECT
    patient_service_id,
    patient_id,
    patient_service_id,
    service_name,
    branch_name,
    status,
    requested_at,
    completed_at,
    turnaround_minutes,
    revenue
FROM vw_lab_service_analysis
WHERE completed_at IS NULL;


-- 7. Services by category
SELECT
    category,
    COUNT(*) AS total_services
FROM vw_lab_service_analysis
GROUP BY category
ORDER BY total_services DESC;


-- 8. Revenue by branch
SELECT
    branch_name,
    COALESCE(SUM(revenue), 0) AS total_revenue
FROM vw_lab_service_analysis
GROUP BY branch_name
ORDER BY total_revenue DESC;