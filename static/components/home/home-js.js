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

socket.on("activate-skip", () => {
    activateSkip();
});

socket.on("deactivate-skip", () => {
    deactivateSkip();
});

$('#skip').on('click', () => {
    deactivateSkip();
    socket.emit('skip');
});

//BUTTONS BEHAVIOUR
$('#fullscreen').on('click', () => {
    socket.emit('fullscreen');
});

$('#play').on('click', () => {
    socket.emit('play');
});

$('#next-show').on('click', () => {
    socket.emit('next-show');
});

$('#go-backwards').on('click', () => {
    socket.emit('backwards');
});

$('#go-forwards').on('click', () => {
    socket.emit('forwards');
});

//SOUND
socket.on('volume', value => {
    $('#volume-slider').val(value);
});

$('#mute').on('click', () =>
{
    socket.emit('mute');
});

$('#volume-slider').on('change', () =>
{
    value = parseInt($('#volume-slider').val());
    console.log(value);
    socket.emit('volume', value);
});

//SHOW INFO
socket.on('show-name', show_name => {
    $('#show-name').html(show_name);
});

socket.on('season-episode-info', value => {
    $('#season-episode-info').html(value);
});