//SLIDER BEHAVIOUR
$('#volume-control').on('touchstart', () =>{
    appTabs.allowPageChange = false;
});

$('#volume-control').on('touchend', () =>{
    appTabs.allowPageChange = true;
});

//SCAN START
$('#scan-fab').on('click', () =>{
    activateScan();
});
