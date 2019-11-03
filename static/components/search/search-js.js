//DEFINING PAGE
let searchTabs = new Tabs(0, "search");
searchTabs.create();
tabs.push(searchTabs);

let searchPopup = new Popup("search", searchTabs, appTabs);

$('#search-button').on('click', e => {
    let searchText = $('#search-field').val();
    if (searchText != null && searchText != "")
    {
        eventTrigger("search-request", searchText);
        searchTabs.change(0);
    }
});