$('#start-mouse-control').on('click', () => {
    mousePopup.activate();
});

//CANVAS BEHAVIOUR
let mouseX = null;
let mouseY = null;
$('#canvas').on('touchstart', e => {
    e.preventDefault();
    appTabs.allowPageChange = false;
    mouseX = e.changedTouches[0].pageX;
    mouseY = e.changedTouches[0].pageX;
});

$('#canvas').on('touchend', () => {
    appTabs.allowPageChange = true;
});

$('#canvas').on('touchmove', e => {
    e.preventDefault();
    handleCanvasTouch(e);
});

function handleCanvasTouch(e)
{
    let touches = e.changedTouches;
    for (let touch of touches)
    {
        handleMouseMove(touch.pageX, touch.pageY);
    }    
}

function handleMouseMove(x, y)
{
    let deltaX = mouseX - x;
    let deltaY = mouseY - y;

    mouseX = x;
    mouseY = y;
}

//INPUT BEHAVIOUR
let textVal = '';
$('#type-computer').on('keyup', function() {
    let newVal = $(this).val();
    if (textVal.length > newVal.length)
    {
        //KEYBOARD DELETE
        console.log("delete");
    }
    else if(newVal.length == 0 && textVal.length == newVal.length)
    {
        //KEYBOARD DELETE
        console.log("delete");
    }
    else
    {
        let lastLetter = newVal[newVal.length - 1];
        if(lastLetter == ' ')
        {
            //SPACE
            console.log("space");
        }
        else
        {
            //OTHER LETTER
            console.log(lastLetter);
        }
    }
    textVal = newVal;
});

$('#input-delete').on('click', () => {
    textVal = '';
    $('#type-computer').val("");
});

$('#input-done').on('click', () => {
    textVal = '';
    $('#type-computer').val("");
});