var lineChartCumulativeCtx = document.getElementById("cumulative-line-chart");
var dailyChartCtx = document.getElementById("daily-chart");
var barChartProportionCtx = document.getElementById("proportion-bar-chart");
var lastUpdatedField = document.getElementById("last-updated")

const dataEndpoint = "https://d3eu7xn6iz7q5z.cloudfront.net"

const lineChartCumulativeOptions = {
  responsive: true,
  maintainAspectRatio: true,
  title: {
    display: true,
    text: "AB Cumulative VOC By Reporting Date"
  },
  scales: {
    xAxes: [{
      display: true,
      scaleLabel: {
        display: true,
        labelString: "Date"
      }
    }],
    yAxes: [{
      display: true,
      scaleLabel: {
        display: true,
        labelString: "Cumulative Cases"
      }
    }]
  },
  layout: {
    padding: {
      left: 50,
      right: 50,
      top: 0,
      bottom: 0
    }
  }
}
const barChartDailyOptions = {
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    xAxes: [{
      stacked: true,
      scaleLabel: {
        display: true,
        labelString: "Date"
      }
    }],
    yAxes: [{
      stacked: true,
      scaleLabel: {
        display: true,
        labelString: "Daily Cases"
      }
    }]
  },
  title: {
    display: true,
    text: "AB Daily VOC Cases By Reporting Date"
  },
  layout: {
    padding: {
      left: 50,
      right: 50,
      top: 50,
      bottom: 0
    }
  }
}
const barChartionProportionOptions = {
  responsive: true,
  maintainAspectRatio: true,
  tooltips: {
    callbacks: {
      label: function(toolTipItem, data) {
        index = toolTipItem.index
        vocData = data.datasets.find(dataset => dataset.label === "VOC")
        allData = data.datasets.find(dataset => dataset.label === "Non-VOC")

        vocCases = vocData.data[index]
        allCases = allData.data[index]
        percentVOC = ((vocCases/allCases)*100).toFixed(2)
        return percentVOC + "% VOC\n" + "(" + vocCases + "/" + allCases + ")";
      },
      labelColor: function(tooltipItem, chart) {
        return {
          borderColor: "#FF0000",
          backgroundColor: "#FF0000"
        }
      }
    }
  },
  scales: {
    xAxes: [{
      stacked: true,
      scaleLabel: {
        display: true,
        labelString: "Week"
      }
    }],
    yAxes: [{
      stacked: true,
      scaleLabel: {
        display: true,
        labelString: "Cases"
      }
    }]
  },
  title: {
    display: true,
    text: "AB Proportion VOC By Week Starting Jan 25th"
  },
  layout: {
    padding: {
      left: 50,
      right: 50,
      top: 50,
      bottom: 0
    }
  }
}

var vocReq = fetch(dataEndpoint + "/voc.json");
var dailyReq = fetch(dataEndpoint + "/daily_cases.json");
Promise.all([vocReq, dailyReq]).then(function(values) {
  vocResponse = values[0]
  dailyResponse = values[1]

  if (vocResponse.status != 200) {
    console.log("Looks like there was a problem. Status code: " + vocResponse.status);
    return;
  }
  if (dailyResponse.status !== 200) {
    console.log('Looks like there was a problem. Status Code: ' + dailyResponse.status);
    return;
  }

  Promise.all([vocResponse.json(), dailyResponse.json()]).then(function(jsonValues) {
    vocJson = jsonValues[0]
    dailyJson = jsonValues[1]

    dates = Object.keys(vocJson["B117"]["Cumulative"])
    lastDate = dates[dates.length - 1]
    lastUpdatedField.innerText = "Last Updated " + lastDate + ". Updates around 6:00PM MST."

    b117_cumulative_cases = Object.values(vocJson["B117"]["Cumulative"])
    b1351_cumulative_cases = Object.values(vocJson["B1351"]["Cumulative"])
    p1_cumulative_cases = Object.values(vocJson["P1"]["Cumulative"])

    b117_daily_cases = Object.values(vocJson["B117"]["Daily"])
    b1351_daily_cases = Object.values(vocJson["B1351"]["Daily"])
    p1_daily_cases = Object.values(vocJson["P1"]["Daily"])
    rolling_daily_average = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0].concat(Object.values(vocJson["All VOC"]["7 Day Daily Average"]))

    weeks = Object.keys(vocJson["All VOC"]["Weekly"])
    weeklyVOC = Object.values(vocJson["All VOC"]["Weekly"])
    weeklyAll = Object.values(dailyJson["Weekly"])

    var myLineChart = new Chart(lineChartCumulativeCtx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "B117",
            data: b117_cumulative_cases,
            backgroundColor: "#FF0000",
            borderColor: "#FF0000",
            fill: false
          },
          {
            label: "B1351",
            data: b1351_cumulative_cases,
            backgroundColor: "#0000FF",
            borderColor: "#0000FF",
            fill: false
          },
          {
            label: "P1",
            data: p1_cumulative_cases,
            backgroundColor: "#008000",
            borderColor: "#008000",
            fill: false
          }
        ]
      },
      options: lineChartCumulativeOptions
    })

    var dailyChart = new Chart(dailyChartCtx, {
      type: "bar",
      data: {
        labels: dates,
        datasets: [
          {
            label: "7 Day Average",
            data: rolling_daily_average,
            backgroundColor: "#192430",
            borderColor: "#192430",
            type: "line",
            fill: false
          },
          {
            label: "B117",
            data: b117_daily_cases,
            backgroundColor: "#FF0000",
            borderColor: "#FF0000",
          },
          {
            label: "B1351",
            data: b1351_daily_cases,
            backgroundColor: "#0000FF",
            borderColor: "#0000FF",
          },
          {
            label: "P1",
            data: p1_daily_cases,
            backgroundColor: "#008000",
            borderColor: "#008000",
          },
        ]
      },
      options: barChartDailyOptions
    })

    var myBarChart2 = new Chart(barChartProportionCtx, {
      type: "bar",
      data: {
        labels: weeks,
        datasets: [
          {
            label: "Non-VOC",
            data: weeklyAll,
            backgroundColor: "#808080",
            borderColor: "#808080",
          },
          {
            label: "VOC",
            data: weeklyVOC,
            backgroundColor: "#FF0000",
            borderColor: "#FF0000",
          }
        ]
      },
      options: barChartionProportionOptions
    })
  });
});
