import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import warnings
warnings.filterwarnings('ignore')
np.random.seed(42)
n = 7000

data = pd.DataFrame({
    'customer_id':     [f'CUST{str(i).zfill(5)}' for i in range(1, n+1)],
    'gender':          np.random.choice(['Male', 'Female'], n),
    'senior_citizen':  np.random.choice([0, 1], n, p=[0.84, 0.16]),
    'tenure':          np.random.randint(1, 72, n),
    'contract':        np.random.choice(['Month-to-month', 'One year', 'Two year'], n,
                                         p=[0.55, 0.25, 0.20]),
    'internet_service':np.random.choice(['DSL', 'Fiber optic', 'No'], n,
                                         p=[0.35, 0.45, 0.20]),
    'monthly_charges': np.round(np.random.uniform(20, 110, n), 2),
    'tech_support':    np.random.choice(['Yes', 'No'], n),
    'online_security': np.random.choice(['Yes', 'No'], n),
    'payment_method':  np.random.choice(
                           ['Electronic check', 'Mailed check',
                            'Bank transfer', 'Credit card'], n),
})

# Churn logic: higher for month-to-month, low tenure, high charges
churn_prob = (
    (data['contract'] == 'Month-to-month').astype(float) * 0.35 +
    (data['tenure'] < 12).astype(float) * 0.20 +
    (data['monthly_charges'] > 70).astype(float) * 0.15 +
    (data['tech_support'] == 'No').astype(float) * 0.10
)
churn_prob = churn_prob.clip(0.05, 0.85)
data['churn'] = (np.random.rand(n) < churn_prob).astype(int)
data['churn_label'] = data['churn'].map({1: 'Yes', 0: 'No'})
data['total_charges'] = np.round(data['tenure'] * data['monthly_charges'], 2)

print("Dataset shape:", data.shape)
print(f"\nChurn Rate: {data['churn'].mean()*100:.1f}%")
print("\nChurn by Contract Type:\n",
      data.groupby('contract')['churn'].mean().mul(100).round(1))


conn = sqlite3.connect(':memory:')
data.to_sql('customers', conn, index=False, if_exists='replace')

queries = {
    "Overall Churn Rate": """
        SELECT
            ROUND(SUM(churn) * 100.0 / COUNT(*), 2) AS churn_rate_pct,
            COUNT(*) AS total_customers,
            SUM(churn) AS churned
        FROM customers
    """,
    "Churn by Contract": """
        SELECT contract,
               COUNT(*) AS total,
               SUM(churn) AS churned,
               ROUND(AVG(churn)*100, 1) AS churn_pct
        FROM customers
        GROUP BY contract
        ORDER BY churn_pct DESC
    """,
    "Avg Monthly Charges (Churned vs Not)": """
        SELECT churn_label,
               ROUND(AVG(monthly_charges), 2) AS avg_monthly,
               ROUND(AVG(tenure), 1) AS avg_tenure
        FROM customers
        GROUP BY churn_label
    """,
    "Top Payment Methods of Churned Customers": """
        SELECT payment_method,
               COUNT(*) AS churned_count
        FROM customers
        WHERE churn = 1
        GROUP BY payment_method
        ORDER BY churned_count DESC
    """
}

print("\n" + "="*55)
for title, query in queries.items():
    print(f"\n📊 {title}")
    print(pd.read_sql(query, conn).to_string(index=False))
print("="*55)

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Customer Churn Analysis Dashboard', fontsize=16, fontweight='bold')
grey_palette = ['#333333', '#888888']

# (a) Overall churn pie
churn_counts = data['churn_label'].value_counts()
axes[0, 0].pie(churn_counts, labels=churn_counts.index,
               autopct='%1.1f%%', colors=['#444444', '#BBBBBB'],
               startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
axes[0, 0].set_title('Overall Churn Distribution')

# (b) Churn by contract type
contract_churn = data.groupby('contract')['churn'].mean().mul(100).reset_index()
contract_churn.columns = ['contract', 'churn_pct']
sns.barplot(data=contract_churn, x='contract', y='churn_pct',
            palette=['#222222', '#666666', '#AAAAAA'], ax=axes[0, 1])
axes[0, 1].set_title('Churn Rate by Contract Type')
axes[0, 1].set_ylabel('Churn Rate (%)')
axes[0, 1].set_xlabel('')
for p in axes[0, 1].patches:
    axes[0, 1].annotate(f'{p.get_height():.1f}%',
                        (p.get_x() + p.get_width()/2, p.get_height()),
                        ha='center', va='bottom', fontweight='bold')

# (c) Tenure distribution
sns.histplot(data=data, x='tenure', hue='churn_label',
             bins=30, palette=grey_palette, ax=axes[0, 2], alpha=0.7)
axes[0, 2].set_title('Tenure Distribution by Churn')
axes[0, 2].set_xlabel('Tenure (months)')

# (d) Monthly charges box plot
sns.boxplot(data=data, x='churn_label', y='monthly_charges',
            palette=grey_palette, ax=axes[1, 0])
axes[1, 0].set_title('Monthly Charges vs Churn')
axes[1, 0].set_xlabel('Churned')

# (e) Churn by internet service
internet_churn = data.groupby('internet_service')['churn'].mean().mul(100).reset_index()
sns.barplot(data=internet_churn, x='internet_service', y='churn',
            palette=['#222222', '#666666', '#AAAAAA'], ax=axes[1, 1])
axes[1, 1].set_title('Churn Rate by Internet Service')
axes[1, 1].set_ylabel('Churn Rate (%)')
axes[1, 1].set_xlabel('')

# (f) Payment method churn
pay_churn = data[data['churn']==1]['payment_method'].value_counts()
axes[1, 2].barh(pay_churn.index, pay_churn.values, color='#444444')
axes[1, 2].set_title('Churned Customers by Payment Method')
axes[1, 2].set_xlabel('Count')

plt.tight_layout()
plt.savefig('churn_dashboard.png', dpi=150)
plt.show()
print("\nDashboard saved as churn_dashboard.png")
conn.close()
