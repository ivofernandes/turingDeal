def printKeyMetrics(df):
    metrics = [
        'peRatio', 'totalStockholdersEquity', 'roe',
        'grahamNetNet', 'grahamNumber'
        'R&D_revenue', 'admin_revenue', 'sales_revenue']
    if 'fillingDate' in df and len(df['fillingDate']) > 0:
        report = 'Fundamentals at ' + str(df['fillingDate'][0]) + ': \n'
        for metric in metrics:
            if metric in df:
                report += metric + ': ' + str(round(df[metric][0], 2)) + ' | '

        print(report)
