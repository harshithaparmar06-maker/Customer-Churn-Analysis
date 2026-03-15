#  Customer Churn Analysis Dashboard

An end-to-end **Data Analytics** project analyzing telecom customer churn using Python and SQL. Identifies key drivers of churn through EDA and visualizations.

##  Dataset
Synthetically generated telecom dataset with **7,000 customer records** including:
- Contract type, tenure, monthly charges
- Internet service, tech support, payment method
- Churn label (Yes / No)

##  Key Insights
- Overall churn rate: **~26%**
- Month-to-month contracts churn **3x more** than two-year contracts
- Customers with tenure < 12 months are at highest risk
- Fiber optic users have higher churn than DSL users
- Electronic check payment correlates with higher churn

##  SQL Queries Included
- Overall churn rate
- Churn by contract type
- Avg monthly charges: churned vs retained
- Top payment methods of churned customers

##  Dashboard Plots
1. Churn distribution pie chart
2. Churn rate by contract type
3. Tenure distribution by churn
4. Monthly charges box plot
5. Churn by internet service
6. Payment method breakdown

##  How to Run

```bash
pip install pandas numpy matplotlib seaborn
python churn_analysis.py
```

##  Tech Stack
`Python` `Pandas` `NumPy` `Seaborn` `Matplotlib` `SQLite (SQL)`
