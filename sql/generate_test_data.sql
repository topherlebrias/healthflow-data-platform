-- ============================================================
-- HEALTHFLOW SYNTHETIC TEST DATA
-- ============================================================
-- Purpose:
-- Add a realistic second batch of laboratory activity.
-- All data is synthetic and created for the project.
-- ============================================================


BEGIN;


-- ============================================================
-- 1. NEW PATIENTS
-- ============================================================

INSERT INTO patients
(
    patient_id,
    first_name,
    last_name,
    date_of_birth,
    sex,
    address,
    registration_date
)
VALUES
(
    'P0002',
    'John',
    'Reyes',
    '1988-07-14',
    'Male',
    'Davao City',
    '2026-09-24'
),
(
    'P0003',
    'Ana',
    'Santos',
    '1995-11-22',
    'Female',
    'Cebu City',
    '2026-09-24'
),
(
    'P0004',
    'Carlo',
    'Garcia',
    '1979-02-05',
    'Male',
    'Quezon City',
    '2026-09-24'
),
(
    'P0005',
    'Lea',
    'Mendoza',
    '2002-08-30',
    'Female',
    'Manila',
    '2026-09-24'
),
(
    'P0006',
    'Ramon',
    'Flores',
    '1968-01-19',
    'Male',
    'Davao City',
    '2026-09-24'
);


-- ============================================================
-- 2. NEW PATIENT SERVICE REQUESTS
-- ============================================================

INSERT INTO patient_services
(
    patient_service_id,
    patient_id,
    service_id,
    branch_id,
    requested_at,
    status
)
VALUES
(
    'PS0003',
    'P0002',
    'S0001',
    'B002',
    '2026-09-24 08:00:00',
    'Completed'
),
(
    'PS0004',
    'P0002',
    'S0003',
    'B002',
    '2026-09-24 09:00:00',
    'Completed'
),
(
    'PS0005',
    'P0003',
    'S0002',
    'B003',
    '2026-09-24 10:00:00',
    'Completed'
),
(
    'PS0006',
    'P0003',
    'S0004',
    'B003',
    '2026-09-24 11:00:00',
    'Processing'
),
(
    'PS0007',
    'P0004',
    'S0001',
    'B001',
    '2026-09-24 13:00:00',
    'Completed'
),
(
    'PS0008',
    'P0004',
    'S0002',
    'B001',
    '2026-09-24 14:00:00',
    'Completed'
),
(
    'PS0009',
    'P0005',
    'S0003',
    'B002',
    '2026-09-24 15:00:00',
    'Pending'
),
(
    'PS0010',
    'P0006',
    'S0004',
    'B003',
    '2026-09-24 16:00:00',
    'Completed'
);


-- ============================================================
-- 3. SPECIMENS
-- ============================================================

INSERT INTO specimens
(
    specimen_id,
    patient_service_id,
    specimen_type,
    collected_at,
    received_at,
    status
)
VALUES
(
    'SP0002',
    'PS0003',
    'Blood',
    '2026-09-24 08:05:00',
    '2026-09-24 08:20:00',
    'Received'
),
(
    'SP0003',
    'PS0005',
    'Urine',
    '2026-09-24 10:05:00',
    '2026-09-24 10:20:00',
    'Received'
),
(
    'SP0004',
    'PS0007',
    'Blood',
    '2026-09-24 13:05:00',
    '2026-09-24 13:20:00',
    'Received'
),
(
    'SP0005',
    'PS0008',
    'Urine',
    '2026-09-24 14:05:00',
    '2026-09-24 14:20:00',
    'Received'
);


-- ============================================================
-- 4. LAB RESULTS
-- ============================================================

INSERT INTO lab_results
(
    result_id,
    patient_service_id,
    test_code,
    result_value,
    unit,
    reference_range,
    result_status,
    created_at,
    validated_at
)
VALUES
(
    'R0003',
    'PS0003',
    'HGB',
    14.10,
    'g/dL',
    '12.0-16.0',
    'Validated',
    '2026-09-24 10:20:00',
    '2026-09-24 10:30:00'
),
(
    'R0004',
    'PS0003',
    'WBC',
    6.80,
    'x10^9/L',
    '4.0-11.0',
    'Validated',
    '2026-09-24 10:20:00',
    '2026-09-24 10:30:00'
),
(
    'R0005',
    'PS0004',
    'XRAY_REPORT',
    NULL,
    NULL,
    NULL,
    'Validated',
    '2026-09-24 10:00:00',
    '2026-09-24 10:15:00'
),
(
    'R0006',
    'PS0005',
    'PH',
    6.50,
    'pH',
    '5.0-8.0',
    'Validated',
    '2026-09-24 10:50:00',
    '2026-09-24 11:00:00'
),
(
    'R0007',
    'PS0007',
    'HGB',
    12.80,
    'g/dL',
    '12.0-16.0',
    'Validated',
    '2026-09-24 15:20:00',
    '2026-09-24 15:30:00'
),
(
    'R0008',
    'PS0007',
    'WBC',
    8.10,
    'x10^9/L',
    '4.0-11.0',
    'Validated',
    '2026-09-24 15:20:00',
    '2026-09-24 15:30:00'
),
(
    'R0009',
    'PS0008',
    'PH',
    6.00,
    'pH',
    '5.0-8.0',
    'Validated',
    '2026-09-24 15:00:00',
    '2026-09-24 15:10:00'
),
 

(
    'R0010',
    'PS0010',
    'CT_REPORT',
    NULL,
    NULL,
    NULL,
    'Validated',
    '2026-09-24 17:45:00',
    '2026-09-24 18:00:00'
);


-- ============================================================
-- 5. PAYMENTS
-- ============================================================

INSERT INTO payments
(
    payment_id,
    patient_service_id,
    amount,
    payment_method,
    payment_status,
    payment_date
)
VALUES
(
    'PAY0002',
    'PS0003',
    350.00,
    'Cash',
    'Paid',
    '2026-09-24 08:10:00'
),
(
    'PAY0003',
    'PS0004',
    800.00,
    'Card',
    'Paid',
    '2026-09-24 09:05:00'
),
(
    'PAY0004',
    'PS0005',
    200.00,
    'Cash',
    'Paid',
    '2026-09-24 10:05:00'
),
(
    'PAY0005',
    'PS0007',
    350.00,
    'GCash',
    'Paid',
    '2026-09-24 13:05:00'
),
(
    'PAY0006',
    'PS0008',
    200.00,
    'Cash',
    'Paid',
    '2026-09-24 14:05:00'
),
(
    'PAY0007',
    'PS0010',
    4500.00,
    'Card',
    'Paid',
    '2026-09-24 16:05:00'
);


COMMIT;