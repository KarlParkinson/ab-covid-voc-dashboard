# ab-covid-voc-dashboard
A rudimentary dashboard charting the growth of COVID-19 Variants of Concern in the province of Alberta. See it at [https://karlparkinson.github.io/ab-covid-voc-dashboard/](https://karlparkinson.github.io/ab-covid-voc-dashboard/).

## How it works
`voc_scrape.py` runs as a lambda on AWS at 6:00 PM Mountain Time every evening It scrapes data from the Alberta COVID-19 portal https://www.alberta.ca/stats/covid-19-alberta-statistics.htm#total-cases and from https://beta.ctvnews.ca/content/dam/common/exceltojson/COVID-Variants.txt, which powers the [CTV variant tracker](https://www.ctvnews.ca/health/coronavirus/tracking-variants-of-the-novel-coronavirus-in-canada-1.5296141) to get the variant data.

Charts are made using [chartjs](https://www.chartjs.org/).
