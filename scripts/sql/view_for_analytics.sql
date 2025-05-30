create or replace view vw_monthly_revenue as
select
    date_trunc('month', created_at) as month,
    sum(amount) as total_revenue
from fact_invoices
group by 1
order by 1;

create or replace view vw_active_subscriptions as
select *
from dim_subscriptions
where status = 'active';

create or replace view vw_customer_ltv as
select
    customer_id,
    sum(amount) as lifetime_value
from fact_invoices
group by customer_id;
