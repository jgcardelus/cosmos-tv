if (socket != null)
{
    socket.emit("validate-connection");
    socket.on('connect', function(message)
    {
        print(message);
    });
}
