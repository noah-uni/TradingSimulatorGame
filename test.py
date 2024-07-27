# chart_app.py
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def chart():
    chart_js = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            #chart {
                width: 100%;
                height: 400px;
            }
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        <script>
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {
                width: 600,
                height: 400,
                layout: {
                    backgroundColor: '#000000',
                    textColor: '#FFFFFF',
                },
                grid: {
                    vertLines: {
                        color: '#404040',
                    },
                    horzLines: {
                        color: '#404040',
                    },
                },
                priceScale: {
                    borderColor: '#cccccc',
                },
                timeScale: {
                    borderColor: '#cccccc',
                },
            });

            const lineSeries = chart.addLineSeries();
            lineSeries.setData([
                { time: '2023-01-01', value: 100 },
                { time: '2023-01-02', value: 105 },
                { time: '2023-01-03', value: 102 },
                // More data points...
            ]);
        </script>
    </body>
    </html>
    """
    return render_template_string(chart_js)

if __name__ == '__main__':
    app.run(debug=True)
