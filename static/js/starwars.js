// script.js
let currentPage = 1;

function showMore() {
    currentPage += 1;
    const collectionId = document.getElementById("collection-id").value;
    const url = `/app/collections/${collectionId}?page=${currentPage}`;
    console.log(url, collectionId)

    fetch(url)
        .then(response => response.text())
        .then(text => {
            const parser = new DOMParser();
            const htmlDoc = parser.parseFromString(text, 'text/html');
            const newTableRows = htmlDoc.querySelectorAll("#table-body tr");
            const tableBody = document.getElementById("table-body");

            newTableRows.forEach(row => {
                tableBody.appendChild(row.cloneNode(true));
            });

            const showMoreButton = document.getElementById("show-more");
            if (htmlDoc.getElementById("no-more-data")) {
                showMoreButton.disabled = true;
            }
        });
}

$(document).ready(function () {
      // Load the checked state from local storage
      $('.selectable').each(function () {
        var isChecked = sessionStorage.getItem($(this).attr('id')) === 'true';
        $(this).prop('checked', isChecked);
      });

     // Store the checked state in local storage when the checkbox is clicked
      $('.selectable').on('change', function () {
        sessionStorage.setItem($(this).attr('id'), $(this).is(':checked'));
      });

    function reloadPageWithCheckedValues() {
        const checkedValues = [];
        $('input.selectable:checked').each(function() {
          checkedValues.push($(this).val());
    });

    const currentUrl = window.location.href.split('?')[0];
    const newUrl = currentUrl + '?' + $.param({checked: checkedValues.join(',')});
    window.location.href = newUrl;
    }

  $('input.selectable').on('change', function() {
    // Remove any existing timeout to avoid multiple reloads
    clearTimeout(window.reloadTimeout);

    // Set a new timeout to reload the page after 2 seconds
    window.reloadTimeout = setTimeout(reloadPageWithCheckedValues, 2000);
  });
})
