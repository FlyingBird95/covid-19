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
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-confirmed', [confirmed], { title: 'Confirmed' });

      const recovered = {
        type: 'scatter',
        mode: 'lines',
        name: 'Recovered',
        x: unpack(data.recovered, 'moment'),
        y: unpack(data.recovered, 'amount'),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-recovered', [recovered], { title: 'Recovered' });

      const deaths = {
        type: 'scatter',
        mode: 'lines',
        name: 'Deaths',
        x: unpack(data.deaths, 'moment'),
        y: unpack(data.deaths, 'amount'),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-deaths', [deaths], { title: 'Deaths' });

      const confirmedDelta = {
        type: 'scatter',
        mode: 'lines',
        name: 'Confirmations per day',
        x: unpack(data.confirmed, 'moment').slice(1),
        y: delta(unpack(data.confirmed, 'amount')),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-confirmed-delta', withMovingAvg(confirmedDelta), { title: 'Confirmations per day' });

      const recoveredDelta = {
        type: 'scatter',
        mode: 'lines',
        name: 'Recoveries per day',
        x: unpack(data.recovered, 'moment').slice(1),
        y: delta(unpack(data.recovered, 'amount')),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-recovered-delta', withMovingAvg(recoveredDelta), { title: 'Recoveries per day' });

      const deathsDelta = {
        type: 'scatter',
        mode: 'lines',
        name: 'Deaths per day',
        x: unpack(data.deaths, 'moment').slice(1),
        y: delta(unpack(data.deaths, 'amount')),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-deaths-delta', withMovingAvg(deathsDelta), { title: 'Deaths per day' });

      const confirmedDelta2 = {
        type: 'scatter',
        mode: 'lines',
        name: 'Confirmed delta per day',
        x: unpack(data.confirmed, 'moment').slice(2),
        y: delta(delta(unpack(data.confirmed, 'amount'))),
        line: { color: '#021e20' },
      };

      Plotly.newPlot('plotly-confirmed-delta2', withMovingAvg(confirmedDelta2), { title: 'Confirmed delta per day' });
    });
    // eslint-disable-next-line func-names
  } else if (window.location.pathname.startsWith('/stats/')) {
    const table = $('#table');
    table.DataTable({
      ajax: '/stats/overview-json',
      order: [[2, 'desc']],
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
