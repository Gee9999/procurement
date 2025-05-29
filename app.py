import streamlit as st
import pandas as pd
import io

def calculate_replenishment_order(df):
    df.columns = df.columns.str.strip()
    months = ['06/24', '07/24', '08/24', '09/24', '10/24', '11/24', '12/24', '01/25', '02/25', '03/25', '04/25']

    # Use ONHAND only as current stock, ignore 'In warehouse'
    df['ONHAND'] = pd.to_numeric(df['ONHAND'], errors='coerce').fillna(0)
    df['total_stock'] = df['ONHAND']

    monthly_sales = df[months].apply(pd.to_numeric, errors='coerce').fillna(0)

    sum_top3_sales = monthly_sales.apply(lambda row: row.nlargest(3).sum(), axis=1)
    sum_top6_sales = monthly_sales.apply(lambda row: row.nlargest(6).sum(), axis=1)

    def round_to_nearest_50(x):
        return int(round(x / 50) * 50)

    new_order = []
    for idx, row in df.iterrows():
        if row['total_stock'] >= sum_top6_sales[idx]:
            new_order.append(0)
        else:
            new_order.append(round_to_nearest_50(sum_top3_sales[idx]))

    report_df = df[['CODE', 'DESCRIPTION', 'ONHAND', 'total_stock']].copy()
    report_df['sum_top3_sales'] = sum_top3_sales
    report_df['sum_top6_sales'] = sum_top6_sales
    report_df['new_order'] = new_order
    return report_df

st.title('Stock Replenishment Calculator')

uploaded_file = st.file_uploader('Upload your stock Excel file', type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        result_df = calculate_replenishment_order(df)
        if result_df is not None:
            st.write('Replenishment Report:')
            st.dataframe(result_df)

            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False)
            output_buffer.seek(0)

            st.download_button(
                label='Download Report as Excel',
                data=output_buffer,
                file_name='replenishment_report.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
