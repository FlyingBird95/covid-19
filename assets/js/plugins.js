// place any jQuery/helper plugins in here, instead of separate, slower script files.

const Plotly = require('plotly.js-dist');

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
      function unpack(rows, key) {
        return rows.map((row) => row[key]);
      }

      function delta(rows){
        let newRows = [];
        for(let i = 1; i<rows.length; i++){
          newRows.push(rows[i] - rows[i-1])
        }
        return newRows
      }

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

      Plotly.newPlot('plotly-confirmed-delta', [confirmedDelta], { title: 'Confirmations per day' });
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
        { data: 'province' },
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
