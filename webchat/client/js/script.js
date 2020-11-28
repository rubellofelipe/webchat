var websocket = new WebSocket('ws://localhost:8888');
var username = 'None';

var input = document.getElementById('mensagem');
input.addEventListener("keyup", function (event) {
    if (event.key === 'Enter') {
        console.log("apertou enter")
        document.getElementById('btn').click();
    }
});




websocket.onopen = function () {
    console.log('abriu')
}

websocket.onclose = function () {
    console.log('fechou')
}

websocket.onmessage = function (hash) {
    console.log(hash)
    var area = document.getElementById('area_de_texto');
    var elemento = document.createElement("P");
    var decodificado = JSON.parse(hash.data)

    var message_sender = decodificado.sender
    var mensagem = decodificado.data
    var tipo = decodificado.type

    var text = (message_sender + ': ' + mensagem);
    text = text.split(/\n/g);

    switch (tipo) {
        case 'alert':
            elemento.style.color = 'crimson'
            break;
        case 'command':
            elemento.style.color = 'gold'
            break;
        case 'set':
            elemento.style.color = 'purple'
            var comando = (mensagem.split(":"))
            username = comando[1].trim()
            break;
        case 'all':
            elemento.style.color = 'black'
            break;
        case 'target':
            elemento.style.color = 'blue'
            break
        default:
            break;
    }



    elemento.style.margin = '2px'
    for (let index = 0; index < text.length; index++) {
        elemento.appendChild(document.createTextNode(text[index]))
        if (index + 1 != text.length) {
            elemento.appendChild(document.createElement('br'))
        }

    }
    elemento.style.textAlign = "left"
    area.appendChild(elemento);
}


function change() {
    var mensagem = document.getElementById('mensagem').value.trim();
    var area = document.getElementById('area_de_texto');
    var elemento = document.createElement('p')
    elemento.appendChild(document.createTextNode(mensagem))
    elemento.style.textAlign = "right"
    area.appendChild(elemento)

    if (mensagem.trim()) {
        elemento.style.color = 'indigo'
        elemento.style.margin = '2px'
        var socketmessage = { 'sender': username, 'data': mensagem }
        var hash = JSON.stringify(socketmessage)
        websocket.send(hash);
        document.getElementById('mensagem').value = ''
    }
}