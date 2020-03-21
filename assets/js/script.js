// App initialization code goes here

$(document).ready(() => {
  if ($('.sidenav').length > 0) { // side menu is used
    $('main').addClass('sidenav-offset');
    $('footer').addClass('sidenav-offset');
  }
});
