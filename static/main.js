document.querySelectorAll('[data-time]').forEach(function(element) {
    var m = new moment(element.getAttribute('data-time') * 1000);
    element.title = element.innerText;
    element.innerText = m.toString();
});
