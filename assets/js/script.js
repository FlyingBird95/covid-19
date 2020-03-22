// App initialization code goes here

$(document).ready(() => {
  $('#sidebarCollapse').on('click', () => {
    $('#sidebar').toggleClass('active');
    $('footer').toggleClass('active');
  });
});
