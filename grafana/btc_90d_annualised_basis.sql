-- select btc perpetual future as spot price ref
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

-- select btc current quarter future as current quarter ref
DROP TABLE IF EXISTS btc_quarterly;
CREATE TABLE btc_quarterly AS
SELECT 
    *, 
    price AS quarterly_future_price
FROM 
    deribit_futures
WHERE 
    asset = 'BTC'
    AND future_reference = 'current_quarter';

-- do inner join and compute 90d annualised basis
DROP TABLE IF EXISTS btc_90d_annualised_basis;
CREATE TABLE btc_90d_annualised_basis AS
SELECT 
	quarterly_futures.price AS quarterly_future_price,
	perpetual_futures.price AS perpetual_future_price,
	quarterly_futures.datetime_ AS datetime_,
	(TO_TIMESTAMP(SUBSTRING(quarterly_futures.instrument FROM 5), 'DDMONYY')::DATE - quarterly_futures.datetime_::DATE) AS days_between_future_and_datetime,
	quarterly_futures.instrument AS expiration_date
FROM 
	btc_quarterly quarterly_futures
INNER JOIN
	btc_perpetual perpetual_futures
ON 
	quarterly_futures.datetime_ = perpetual_futures.datetime_;

select 
	datetime_,
	(quarterly_future_price/perpetual_future_price - 1) / days_between_future_and_datetime/ 365 ::DOUBLE PRECISION as btc_90d_annualised_basis
from btc_90d_annualised_basis


