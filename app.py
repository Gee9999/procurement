def calculate_replenishment_order(df):
    df.columns = df.columns.str.strip()
    months = ['06/24', '07/24', '08/24', '09/24', '10/24', '11/24', '12/24', '01/25', '02/25', '03/25', '04/25']
    df['current_stock'] = df['ONHAND']  # Use ONHAND only as current stock
    monthly_sales = df[months]
    sum_top3_sales = monthly_sales.apply(lambda row: row.nlargest(3).sum(), axis=1)
    sum_top6_sales = monthly_sales.apply(lambda row: row.nlargest(6).sum(), axis=1)
    def round_to_nearest_50(x):
        return int(round(x / 50) * 50)
    new_order = []
    for idx, row in df.iterrows():
        if row['current_stock'] >= sum_top6_sales[idx]:
            new_order.append(0)
        else:
            new_order.append(round_to_nearest_50(sum_top3_sales[idx]))
    report_df = df[['CODE', 'DESCRIPTION', 'ONHAND', 'CURRENT', 'current_stock']].copy()
    report_df['sum_top3_sales'] = sum_top3_sales
    report_df['sum_top6_sales'] = sum_top6_sales
    report_df['new_order'] = new_order
    return report_df