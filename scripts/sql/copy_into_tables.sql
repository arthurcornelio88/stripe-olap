create or replace stage gcs_stage_prod
  TODO url='gcs://stripe-bucket-prod_v3/olap_outputs/2025-05-30_16-33-17/' 
  storage_integration = my_gcs_integration;

copy into fact_invoices from @gcs_stage_prod/fact_invoices.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_customers from @gcs_stage_prod/dim_customers.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_products from @gcs_stage_prod/dim_products.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_prices from @gcs_stage_prod/dim_prices.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_payment_methods from @gcs_stage_prod/dim_payment_methods.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_subscriptions from @gcs_stage_prod/dim_subscriptions.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_payment_intents from @gcs_stage_prod/dim_payment_intents.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
copy into dim_charges from @gcs_stage_prod/dim_charges.csv file_format = (type = csv field_delimiter = ',' skip_header = 1);
