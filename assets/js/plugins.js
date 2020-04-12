// place any jQuery/helper plugins in here, instead of separate, slower script files.

const Plotly = require('plotly.js-dist');

function unpack(rows, key) {
  return rows.map((row) => row[key]);
}

function runningSum(values){
  var new_array = [];
  values.reduce(function(a,b,i) { return new_array[i] = a+b; },0);
  return new_array;
}

function delta(rows) {
  const newRows = [];
  for (let i = 1; i < rows.length; i += 1) {
    newRows.push(rows[i] - rows[i - 1]);
  }
  return newRows;
}

function movingAverage(trace) {
  const y = [trace.y[0]];
  for (let i = 1; i < trace.y.length - 1; i += 1) {
    y.push((trace.y[i - 1] + trace.y[i] + trace.y[i + 1]) / 3);
  }
  y.push(trace.y[trace.y.length - 1]);
  return {
    type: trace.type,
    mode: trace.mode,
    name: `${trace.name} (3 day average)`,
    x: trace.x,
    y: y,
    line: { color: '#939393' },
  };
}

function withMovingAvg(trace) {
  return [trace, movingAverage(trace)];
}

function plot(name, x, y, div){
  const confirmed = {
    type: 'scatter',
    mode: 'lines',
    name: name,
    x: x,
    y: y,
    line: {color: '#021e20'},
  };

  Plotly.newPlot(div, [confirmed], {title: name});
}

function plotSimple(name, data, div){
  plot(name, unpack(data, 'moment'), unpack(data, 'amount'), div)
}

function plotDelta(name, data, div){
  const confirmedDelta = {
    type: 'scatter',
    mode: 'lines',
    name: name,
    x: unpack(data, 'moment').slice(1),
    y: delta(unpack(data, 'amount')),
    line: {color: '#021e20'},
  };
  Plotly.newPlot(div, withMovingAvg(confirmedDelta), {title: name});
}

function predict(data, name, obj, div, title){
  const real = {
    type: 'scatter',
    mode: 'markers',
    name: `Real ${name}`,
    x: obj.time,
    y: obj.values,
    line: { color: '#ff392d' },
  };
  const predictions = {
    type: 'scatter',
    mode: 'lines',
    name: `Predicted ${name}`,
    x: obj.time,
    y: obj.predictions,
    line: { color: 'rgba(255,57,45,0.87)' },
  };
  const layout = {
    title: data.name,
    yaxis: {
      title: { text: title },
    },
  };
  $(`#${div}`).empty();
  Plotly.newPlot(div, [real, predictions], layout);
}

$(document).ready(() => {
  // eslint-disable-next-line no-restricted-globals
  if (window.location.pathname.startsWith('/stats/location/')) {
    $('#table').DataTable({
      paging: false,
      ordering: false,
      info: false,
      searching: false,
    });

    Plotly.d3.json(`${window.location.href}/json`, (err, data) => {
      plotSimple('Confirmed', data.confirmed, 'plotly-confirmed');
      plotSimple('Recovered', data.recovered, 'plotly-recovered');
      plotSimple('Deaths', data.deaths, 'plotly-deaths');

      plotDelta('Confirmations per day', data.confirmed, 'plotly-confirmed-delta')

      const compareChina = {
        type: 'scatter',
        mode: 'lines',
        name: 'China',
        y: delta(data.compare.china),
        line: {color: '#ff392d'},
      };
      const compareLocation = {
        type: 'scatter',
        mode: 'lines',
        name: data.name,
        y: delta(data.compare.location),
        line: {color: '#021e20'},
      };
      Plotly.newPlot('plotly-confirmed-china', [compareLocation, compareChina], {title: 'Growth comparison with China'});
    });
    Plotly.d3.json(`${window.location.href}/json-future`, (err, data) => {

      predict(data, 'number of daily confirmations', data.confirmations, 'plotly-future-infected', 'Daily number of confirmed cases')
      data.confirmations.values = runningSum(data.confirmations.values)
      data.confirmations.predictions = runningSum(data.confirmations.predictions)
      predict(data, 'cumulative confirmations', data.confirmations, 'plotly-future-infected-sum', 'Cumulative confirmed cases')

      predict(data, 'number of deaths', data.deaths, 'plotly-future-deaths', 'Daily predicted number of deaths')
      data.deaths.values = runningSum(data.deaths.values)
      data.deaths.predictions = runningSum(data.deaths.predictions)
      predict(data, 'cumulative deaths', data.deaths, 'plotly-future-deaths-sum', 'Cumulative deahts')
    });
    // eslint-disable-next-line func-names
  } else if (window.location.pathname.startsWith('/stats/world')) {
    Plotly.d3.json(`${window.location.href}/json`, (err, data) => {
      plotSimple('Confirmed', data.confirmed, 'plotly-confirmed');
      plotSimple('Recovered', data.recovered, 'plotly-recovered');
      plotSimple('Deaths', data.deaths, 'plotly-deaths');

      plotDelta('Confirmations per day', data.confirmed, 'plotly-confirmed-delta')
    });
    Plotly.d3.json(`${window.location.href}/json-future`, (err, data) => {

      predict(data, 'number of daily confirmations', data.confirmations, 'plotly-future-infected', 'Daily number of confirmed cases')
      data.confirmations.values = runningSum(data.confirmations.values)
      data.confirmations.predictions = runningSum(data.confirmations.predictions)
      predict(data, 'cumulative confirmations', data.confirmations, 'plotly-future-infected-sum', 'Cumulative confirmed cases')

      predict(data, 'number of deaths', data.deaths, 'plotly-future-deaths', 'Daily predicted number of deaths')
      data.deaths.values = runningSum(data.deaths.values)
      data.deaths.predictions = runningSum(data.deaths.predictions)
      predict(data, 'cumulative deaths', data.deaths, 'plotly-future-deaths-sum', 'Cumulative deahts')
    });

  } else if (window.location.pathname.startsWith('/stats/')) {
    const table = $('#table');
    table.DataTable({
      ajax: '/stats/overview-json',
      order: [[1, 'desc']],
      fnRowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $(nRow).attr('data-url', aData.url);
        return nRow;
      },
      columns: [
        { data: 'country' },
        {
          data: 'confirmed',
          render(data, type, row) {
            return data.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
          },
        },
        {
          data: 'recovered',
          render(data, type, row) {
            return data.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
          },
        },
        {
          data: 'death',
          render(data, type, row) {
            return data.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
          },
        },
      ],
    });
    $('#table tbody').on('click', 'tr', function () {
      window.location.href = $(this).attr('data-url');
    });
  }
});
