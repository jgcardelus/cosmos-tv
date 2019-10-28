//DEFINING PAGE
let scanTabs = new Tabs(0, '#scan');
scanTabs.create();
tabs.push(scanTabs);

//PAGE ACTIVATION AND DEACTIVATION
function activateScan()
{
    for (let i = 0; i < tabs.length; i++)
    {
        let tab = tabs[i];
        if (tab != scanTabs)
        {
            tab.allowPageChange = false;
        }
    }
    scanTabs.allowPageChange = true;
    $('#scan').css('z-index', '500');
    $('#scan tabs').css('z-index', '500');
    if ($('#scan').hasClass('hidden'))
    {
        $('#scan').removeClass('hidden');
    }
    scanTabs.change(1);
}

function deactivateScan()
{
    $('#scan').css('z-index', '0');
    $('#scan tabs').css('z-index', '0');
    for (let i = 0; i < tabs.length; i++)
    {
        let tab = tabs[i];
        tab.allowPageChange = false;
    }
    appTabs.allowPageChange = true;
    if (!$('#scan').hasClass('hidden'))
    {
        $('#scan').addClass('hidden');
    }
}

let hasChanged = false;
scanTabs.on('page-change', () => {
    if (scanTabs.actualTab == 0)
    {
        if (hasChanged)
        {
            deactivateScan();
            hasChanged = false;
        }
    }
    else if(scanTabs.actualTab == 1)
    {
        hasChanged = true;
    }
});

$('#close-span').on('click', () =>{
    scanTabs.change(0);
})

// PAGE BEHAVIOUR
