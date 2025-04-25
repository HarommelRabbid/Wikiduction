var tables = document.getElementsByTagName('table');
for (var i = 0; i < tables.length; i++)
    tables[i].setAttribute('class', 'table table-hover');

var figures = document.getElementsByTagName('figure');
for (var i = 0; i < figures.length; i++)
    figures[i].setAttribute('class', 'figure');
    var figcaptions = document.querySelectorAll('figure figcaption');
    for (var i = 0; i < figcaptions.length; i++)
    figcaptions[i].setAttribute('class', 'figure-caption');
    var imgs = document.querySelectorAll('figure img');
    for (var i = 0; i < imgs.length; i++)
        imgs[i].setAttribute('class', 'figure-img img-fluid rounded');

var imgs1 = document.querySelectorAll('img:not(figure img)');
for (var i = 0; i < imgs1.length; i++)
        imgs1[i].setAttribute('class', 'img-fluid');

var abbrs = document.querySelectorAll('abbr');
for (var i = 0; i < abbrs.length; i++)
        abbrs[i].setAttribute('data-bs-toggle', 'tooltip');
for (var i = 0; i < abbrs.length; i++)
        abbrs[i].setAttribute('style', 'text-decoration-line: underline; text-decoration-style: dotted; cursor: default;');

var links = document.querySelectorAll('#content a');
for (var i = 0; i < links.length; i++)
    links[i].setAttribute('class', 'link-primary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover')

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

const toastElList = document.querySelectorAll('.toast')
const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl, option))

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))