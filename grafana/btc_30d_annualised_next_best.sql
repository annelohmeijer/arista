drop table if exists unique_deribit_futures_btc;
create temp table unique_deribit_futures_btc as
select distinct 
	asset, 
	future_reference,
	datetime_,
	datetime_ + INTERVAL '30 days' as datetime_30D,
	instrument,
	price,
	(TO_TIMESTAMP(SUBSTRING(instrument FROM 5), 'DDMONYY')::DATE - datetime_::DATE) AS days_between_future_and_datetime,
	(TO_TIMESTAMP(SUBSTRING(instrument FROM 5), 'DDMONYY')::DATE - (datetime_ + INTERVAL '30 days')::DATE) AS days_between_30d_and_future
from deribit_futures
where
	asset = 'BTC'
	AND
	future_reference != 'perpetual';

DROP TABLE IF EXISTS btc_perpetual;
CREATE TABLE btc_perpetual AS
SELECT 
    *, 
    price AS perpetual_future_price
FROM 
    deribit_futures
WHERE 
    asset = 'BTC'
    AND future_reference = 'perpetual';
DROP TABLE IF EXISTS ranked_futures;
CREATE TEMP TABLE ranked_futures AS (
    SELECT 
        datetime_,
        future_reference,
        days_between_30d_and_future,
		days_between_future_and_datetime,
		instrument,
		price,
        ROW_NUMBER() OVER (
            PARTITION BY datetime_ 
            ORDER BY ABS(days_between_30d_and_future) ASC
        ) AS rn
    FROM 
        unique_deribit_futures_btc
);

DROP TABLE IF EXISTS btc_monthly;
CREATE TABLE btc_monthly AS
SELECT 
    *, 
    price AS monthly_future_price
FROM 
    ranked_futures
WHERE 
	rn = 1;

-- do inner join and compute 90d annualised basis
DROP TABLE IF EXISTS btc_30d_annualised_basis;
CREATE TABLE btc_30d_annualised_basis AS
SELECT 
	monthly_futures.price AS monthly_future_price,
	perpetual_futures.price AS perpetual_future_price,
	monthly_futures.datetime_ AS datetime_,
	(TO_TIMESTAMP(SUBSTRING(monthly_futures.instrument FROM 5), 'DDMONYY')::DATE - monthly_futures.datetime_::DATE) AS days_between_future_and_datetime,
	monthly_futures.instrument AS expiration_date
FROM 
	btc_monthly monthly_futures
INNER JOIN
	btc_perpetual perpetual_futures
ON 
	monthly_futures.datetime_ = perpetual_futures.datetime_;

select 
	datetime_,
	(monthly_future_price/perpetual_future_price - 1) / (days_between_future_and_datetime/ 365 ::DOUBLE PRECISION) as btc_30d_annualised_basis
from btc_30d_annualised_basis



