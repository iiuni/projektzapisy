/**
 * Funkcje i klasy odpowiedzialne za moduł newsów.
 */

News = Object();

News.init = function()
{
  $('#od-news-search-reset').click(function()
  {
    $('#od-news-search-form').val('')
  })
}

$(document).ready(function() {
  News.init()
})

