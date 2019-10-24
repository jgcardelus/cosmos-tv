//Global variables
const DEBUG = false;
let allowPageChange = true;

//CONNECT TO SERVER
let socket = null;
function connectServer()
{
    //$SOCKET_IP
      socket = io.connect("http://192.168.2.51:8080"); //This line was autogenerated.

    socket.emit('validate_connection');
    socket.on('connection_validated', function()
    {
        console.log("Connected to server. Welcome back");
    });

}

function loadMDC()
{
    $('.mdc-button').attr('data-mdc-auto-init', 'MDCRipple');
    $('.mdc-icon-button').attr('data-mdc-auto-init', 'MDCRipple');
    $('.mdc-fab').attr('data-mdc-auto-init', 'MDCRipple');

	mdc.autoInit();
}

function startEnvironment()
{
    if(!DEBUG)
    {
        connectServer();
	}
	loadMDC();
}

startEnvironment();

//PAGE BEHAVIOUR
let windowWidth = $(window).width();
let windowHeight = $(window).height();

$(window).on('resize', function()
{
	windowWidth = $(window).width();
	windowHeight = $(window).height();

	pages.change(actualPage);
});
