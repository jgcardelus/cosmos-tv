$('#start-mouse-control').on('click', () => {
    raiseNotification('Action not supported at the moment.', LONG);
    //mousePopup.activate();
});

//CANVAS BEHAVIOUR
let mouseX = [];
let mouseY = [];
const bufferSize = 8;

$('#canvas').on('touchstart', e => {
    e.preventDefault();
    appTabs.allowPageChange = false;
    mouseX.push(e.changedTouches[0].pageX);
    mouseY.push(e.changedTouches[0].pageY);
});

$('#canvas').on('touchend', () => {
    appTabs.allowPageChange = true;
    // Reset variables
    mouseX = [];
    mouseY = [];
});

$('#canvas').on('touchmove', e => {
    e.preventDefault();
    handleCanvasTouch(e);
});

$('#canvas').on('click', e => {
    e.preventDefault();
    socket.emit('mouse-left');
});

function handleCanvasTouch(e)
{
    let touches = e.changedTouches;
    for (let i = 0; i < touches.length; i++)
    {
        let touch = touches[i];
        mouseX.push(touch.pageX);
        mouseY.push(touch.pageY);
    }

    if (mouseX.length >= bufferSize)
    {
        handleMouseMove();
    }
}

function handleMouseMove()
{
    let encodedPosition = '';
    for (let i = 0; i < (mouseX.length - 1); i++)
    {
        let deltaX = mouseX[i + 1] - mouseX[i];
        let deltaY = mouseY[i + 1] - mouseY[i];

        deltaX = Math.round(deltaX);
        deltaY = Math.round(deltaY);
        
        if (i == 0)
        {
            encodedPosition += String(deltaX) + ':' + String(deltaY);
        }
        else
        {
            encodedPosition += '/' + String(deltaX) + ':' + String(deltaY);
        }
    }
    mouseX.splice(0, mouseX.length - 2);
    mouseY.splice(0, mouseY.length - 2);

    socket.emit('mouse-canvas-move', encodedPosition);
}

$('#mouse-left').on('click', () =>
{
    socket.emit('mouse-left');
});

$('#mouse-right').on('click', () =>
{
    socket.emit('mouse-right');
});

//INPUT BEHAVIOUR
let textVal = '';
$('#type-computer').on('input', function() {
    let newVal = $(this).val();
    if (textVal.length > newVal.length)
    {
        //KEYBOARD DELETE
        socket.emit('key-pressed', 'delete');
    }
    else
    {
        let lastLetter = newVal[newVal.length - 1];
        if(lastLetter == ' ')
        {
            //SPACE
            socket.emit('key-pressed', 'space');
        }
        else
        {
            //OTHER LETTER
            socket.emit('key-pressed', lastLetter);
        }
    }
    textVal = newVal;
});

$('#type-computer').on('keyup', function() {
    let newVal = $(this).val();
    if (textVal.length > newVal.length)
    {
        //KEYBOARD DELETE
        socket.emit('key-pressed', 'delete');
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
    socket.emit('key-pressed', 'enter')
});