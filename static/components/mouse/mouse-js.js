let mouseTabs = new Tabs(0, "mouse");
mouseTabs.create();
tabs.push(mouseTabs);

//PAGE ACTIVATION AND DEACTIVATION
let mousePopup = new Popup("mouse", mouseTabs, appTabs);

//PAGE BEHAVIOUR
let isScrolling = false;
let animationTime = 300;
function activateMouseControl(time)
{
    $('#mouse .tab .header').slideUp(time, () => {
        $('#mouse .tab .header').html("Mouse");
        $('#mouse .tab .header').slideDown(time);
    });

    $('#switch-mouse-mode .button p').fadeOut(time, () => {
        $('#switch-mouse-mode .button p').html("Switch to scrolling");
        $('#switch-mouse-mode .button p').fadeIn(time);
    });

    if($('#mouse-control-buttons').css("display") == "none")
    {
        $('#mouse-control-buttons').slideDown(time);
    }

    isScrolling = false;
}

function activateScrollingMode(time)
{
    $('#mouse .tab .header').slideUp(time, () => {
        $('#mouse .tab .header').html("Scrolling");
        $('#mouse .tab .header').slideDown(time);
    });

    $('#switch-mouse-mode .button p').fadeOut(time, () => {
        $('#switch-mouse-mode .button p').html("Switch to mouse");
        $('#switch-mouse-mode .button p').fadeIn(time);
    });

    if($('#mouse-control-buttons').css("display") != "none")
    {
        $('#mouse-control-buttons').slideUp(time);
    }

    isScrolling = true;
}

$('#switch-mouse-mode').on("click", () => {
    if (isScrolling)
    {
        activateMouseControl(animationTime);
    }
    else
    {
        activateScrollingMode(animationTime);
    }
});

activateMouseControl(0);