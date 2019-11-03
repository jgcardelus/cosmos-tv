//SLIDER BEHAVIOUR
$('#volume-control').on('touchstart', () =>{
    appTabs.allowPageChange = false;
});

$('#volume-control').on('touchend', () =>{
    appTabs.allowPageChange = true;
});

//SCAN START
$('#start-scan').on('click', () =>{
    scanPopup.activate();
});


//SKIP BEHAVIOUR
let skipActive = true;
let skipAnimationTime = 300;
function activateSkip(animationTime=skipAnimationTime)
{
    if (!skipActive)
    {
        $('#skip').slideDown(animationTime, () => {
            skipActive = true;
        });
    }
}

function deactivateSkip(animationTime=skipAnimationTime)
{
    if(skipActive)
    {
        $('#skip').slideUp(animationTime, () => {
            skipActive = false;
        });
    }
}

deactivateSkip(0);

//BUTTONS BEHAVIOUR
$('#go-backwards').on('click', () => {
    console.log("go backwards");
});

$('go-forwards').on('click')