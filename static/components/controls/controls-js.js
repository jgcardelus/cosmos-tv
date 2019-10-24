let slider = null;
//Deactivate swiping effect defined on ./static/components/tabs/tabs-js.js
$('#volume-slider').on('touchstart', function()
{
    allowPageChange = false;
});

$('#volume-slider').on('touchend', function()
{
    allowPageChange = true;
});
