// place any jQuery/helper plugins in here, instead of separate, slower script files.

const Plotly = require('plotly.js-dist');

function unpack(rows, key) {
  return rows.map((row) => row[key]);
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
      const confirmed = {
        type: 'scatter',
        mode: 'lines',
        name: 'Confirmed',
        x: unpack(data.confirmed, 'moment'),
        y: unpack(data.confirmed, 'amount'),
        line: {color: '#021e20'},
      };

      Plotly.newPlot('plotly-confirmed', [confirmed], {title: 'Confirmed'});

      const recovered = {
        type: 'scatter',
        mode: 'lines',
        name: 'Recovered',
        x: unpack(data.recovered, 'moment'),
        y: unpack(data.recovered, 'amount'),
        line: {color: '#021e20'},
      };

      Plotly.newPlot('plotly-recovered', [recovered], {title: 'Recovered'});

      const deaths = {
        type: 'scatter',
        mode: 'lines',
        name: 'Deaths',
        x: unpack(data.deaths, 'moment'),
        y: unpack(data.deaths, 'amount'),
        line: {color: '#021e20'},
      };

      Plotly.newPlot('plotly-deaths', [deaths], {title: 'Deaths'});

      const confirmedDelta = {
        type: 'scatter',
        mode: 'lines',
        name: 'Confirmations per day',
        x: unpack(data.confirmed, 'moment').slice(1),
        y: delta(unpack(data.confirmed, 'amount')),
        line: {color: '#021e20'},
      };

      Plotly.newPlot('plotly-confirmed-delta', withMovingAvg(confirmedDelta), {title: 'Confirmations per day'});

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
      const futureInfected = {
        type: 'scatter',
        mode: 'markers',
        name: 'Actual cases',
        x: data.time_number_days,
        y: data.cases_ref,
        line: { color: '#ff392d' },
      };
      const futureInfected2 = {
        type: 'scatter',
        mode: 'lines',
        name: 'Predicted cases',
        x: data.time_sim,
        y: data.cases_sim,
        line: { color: 'rgba(255,57,45,0.87)' },
      };
      const layout = {
        title: data.name,
        xaxis: {
          title: { text: 'Days' },
        },
        yaxis: {
          title: { text: 'Number of active cases' },
        },
      };
      $('#plotly-future-infected').empty();
      Plotly.newPlot('plotly-future-infected', [futureInfected, futureInfected2], layout);
      const futureDeath = {
        type: 'scatter',
        mode: 'markers',
        name: 'Actual number of deaths',
        x: data.time_number_days,
        y: data.deaths_ref,
        line: { color: '#ff392d' },
      };
      const futureDeath2 = {
        type: 'scatter',
        mode: 'lines',
        name: 'Predicted number of deaths',
        x: data.time_sim,
        y: data.deaths_sim,
        line: { color: 'rgba(255,57,45,0.87)' },
      };
      const layoutDeath = {
        title: data.name,
        xaxis: {
          title: { text: 'Days' },
        },
        yaxis: {
          title: { text: 'Number of active cases' },
        },
      };
      $('#plotly-future-deaths').empty();
      Plotly.newPlot('plotly-future-deaths', [futureDeath, futureDeath2], layoutDeath);
    });
    // eslint-disable-next-line func-names
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
